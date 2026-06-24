"""
CRYSTAL BLUE PRESS — EMAIL ENGINE v3
=====================================
Lemon Squeezy webhook handler.
Evergreen issue sequencing:
  - Every subscriber starts at Issue #1
  - Each monthly renewal sends the next issue in sequence
  - Subscriber data stored in subscribers.json
"""

import os
import json
import base64
import hmac
import hashlib

from datetime import datetime
from flask import Flask, request, jsonify
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import (
    Mail, Attachment, FileContent, FileName,
    FileType, Disposition, To
)
from config import (
    GROUPS,
    SENDGRID_API_KEY,
    FREE_SAMPLE_PDF,
    FREE_SAMPLE_FROM_NAME,
    FREE_SAMPLE_FROM_EMAIL,
    FREE_SAMPLE_SUBJECT,
    FREE_SAMPLE_BODY,
)

app = Flask(__name__)

LS_WEBHOOK_SECRET = os.environ.get("LS_WEBHOOK_SECRET")

SUBSCRIBERS_FILE = "subscribers.json"


def load_subscribers():
    if os.path.exists(SUBSCRIBERS_FILE):
        with open(SUBSCRIBERS_FILE) as f:
            return json.load(f)
    return {}


def save_subscribers(data):
    with open(SUBSCRIBERS_FILE, "w") as f:
        json.dump(data, f, indent=2)


def set_subscriber(customer_id, data):
    subs = load_subscribers()
    subs[customer_id] = data
    save_subscribers(subs)


def increment_issue(customer_id):
    subs = load_subscribers()
    sub = subs.get(customer_id, {"issue": 0})
    sub["issue"] = sub.get("issue", 0) + 1
    sub["last_sent"] = datetime.utcnow().isoformat()
    subs[customer_id] = sub
    save_subscribers(subs)
    return sub["issue"]


def verify_signature(payload, signature):
    secret = LS_WEBHOOK_SECRET.encode("utf-8")
    expected = hmac.new(secret, payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)


def send_email_with_pdf(to_email, subject, body, pdf_path, from_name, from_email):
    if not os.path.exists(pdf_path):
        print(f"ERROR: PDF not found → {pdf_path}")
        return False

    with open(pdf_path, "rb") as f:
        pdf_data = base64.b64encode(f.read()).decode()

    message = Mail(
        from_email=(from_email, from_name),
        to_emails=To(to_email),
        subject=subject,
        plain_text_content=body,
    )
    message.attachment = Attachment(
        FileContent(pdf_data),
        FileName(os.path.basename(pdf_path)),
        FileType("application/pdf"),
        Disposition("attachment"),
    )

    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        resp = sg.send(message)
        print(f"Sent to {to_email} — {resp.status_code}")
        return True
    except Exception as e:
        print(f"SendGrid error: {e}")
        return False


def send_issue(customer_id, email, first_name, group, issue_number):
    sequence = group["issue_sequence"]
    titles = group["issue_titles"]

    if issue_number not in sequence:
        print(f"No issue {issue_number} yet — sending coming soon")
        subject = group["coming_soon_subject"]
        body = group["coming_soon_body"].format(first_name=first_name)
        message = Mail(
            from_email=(group["from_email"], group["from_name"]),
            to_emails=To(email),
            subject=subject,
            plain_text_content=body,
        )
        try:
            sg = SendGridAPIClient(SENDGRID_API_KEY)
            sg.send(message)
        except Exception as e:
            print(f"Coming soon email error: {e}")
        return

    pdf_path = sequence[issue_number]
    issue_title = titles.get(issue_number, f"Issue #{issue_number}")

    if issue_number == 1:
        subject = group["welcome_subject"]
        body = group["welcome_body"].format(first_name=first_name)
    else:
        subject = group["monthly_subject"].format(issue_number=issue_number)
        body = group["monthly_body"].format(
            first_name=first_name,
            issue_number=issue_number,
            issue_title=issue_title,
        )

    send_email_with_pdf(
        to_email=email,
        subject=subject,
        body=body,
        pdf_path=pdf_path,
        from_name=group["from_name"],
        from_email=group["from_email"],
    )


@app.route("/", methods=["GET"])
def health():
    subs = load_subscribers()
    return jsonify({
        "status": "ok",
        "service": "Crystal Blue Press Email Engine v3",
        "subscribers": len(subs),
    })


@app.route("/free-sample", methods=["POST"])
def free_sample():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data"}), 400

    first_name = data.get("first_name", "Explorer").strip()
    email = data.get("email", "").strip()

    if not email or "@" not in email:
        return jsonify({"error": "Invalid email"}), 400

    success = send_email_with_pdf(
        to_email=email,
        subject=FREE_SAMPLE_SUBJECT,
        body=FREE_SAMPLE_BODY.format(first_name=first_name),
        pdf_path=FREE_SAMPLE_PDF,
        from_name=FREE_SAMPLE_FROM_NAME,
        from_email=FREE_SAMPLE_FROM_EMAIL,
    )

    return jsonify({"status": "sent" if success else "failed"}), 200 if success else 500


@app.route("/ls-webhook", methods=["POST"])
def ls_webhook():
    payload = request.get_data()
    signature = request.headers.get("X-Signature", "")

    if not verify_signature(payload, signature):
        return jsonify({"error": "Invalid signature"}), 400

    data = request.get_json()
    event_type = data.get("meta", {}).get("event_name", "")
    attrs = data.get("data", {}).get("attributes", {})

    customer_email = attrs.get("user_email", "")
    customer_name = attrs.get("user_name", "") or "Explorer"
    first_name = customer_name.split()[0]
    customer_id = str(data.get("data", {}).get("id", ""))

    group = GROUPS.get("otter_pups_club")
    if not group:
        return jsonify({"status": "no group"}), 200

    if event_type == "subscription_created":
        set_subscriber(customer_id, {
            "email": customer_email,
            "first_name": first_name,
            "group": "otter_pups_club",
            "issue": 1,
            "joined": datetime.utcnow().isoformat(),
            "last_sent": datetime.utcnow().isoformat(),
        })
        send_issue(customer_id, customer_email, first_name, group, 1)

    elif event_type == "subscription_payment_success":
        sub = load_subscribers().get(customer_id, {})
        if sub.get("issue", 0) == 1 and sub.get("joined", "")[:10] == datetime.utcnow().isoformat()[:10]:
            return jsonify({"status": "skipped"}), 200
        next_issue = increment_issue(customer_id)
        send_issue(customer_id, customer_email, first_name, group, next_issue)

    elif event_type == "subscription_cancelled":
        subs = load_subscribers()
        if customer_id in subs:
            subs[customer_id]["cancelled"] = datetime.utcnow().isoformat()
            save_subscribers(subs)

    return jsonify({"status": "ok"}), 200


@app.route("/subscribers", methods=["GET"])
def list_subscribers():
    subs = load_subscribers()
    summary = []
    for cid, data in subs.items():
        summary.append({
            "email": data.get("email"),
            "first_name": data.get("first_name"),
            "group": data.get("group"),
            "issue": data.get("issue"),
            "joined": data.get("joined"),
            "cancelled": data.get("cancelled", None),
        })
    summary.sort(key=lambda x: x["joined"] or "", reverse=True)
    return jsonify({"total": len(summary), "subscribers": summary})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
