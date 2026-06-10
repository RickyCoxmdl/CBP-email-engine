"""
CRYSTAL BLUE PRESS — EMAIL ENGINE v2
=====================================
Evergreen issue sequencing:
  - Every subscriber starts at Issue #1
  - Each monthly renewal sends the next issue in sequence
  - Subscriber data stored in subscribers.json
  - Works for unlimited groups
"""

import os
import json
import base64
import stripe

from datetime import datetime
from flask import Flask, request, jsonify
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import (
    Mail, Attachment, FileContent, FileName,
    FileType, Disposition, To
)
from config_v2 import (
    GROUPS,
    STRIPE_SECRET_KEY,
    STRIPE_WEBHOOK_SECRET,
    SENDGRID_API_KEY,
    FREE_SAMPLE_PDF,
    FREE_SAMPLE_FROM_NAME,
    FREE_SAMPLE_FROM_EMAIL,
    FREE_SAMPLE_SUBJECT,
    FREE_SAMPLE_BODY,
)

app = Flask(__name__)
stripe.api_key = STRIPE_SECRET_KEY

# ── Subscriber tracking file ──────────────────────────────────
SUBSCRIBERS_FILE = "subscribers.json"


def load_subscribers():
    if os.path.exists(SUBSCRIBERS_FILE):
        with open(SUBSCRIBERS_FILE) as f:
            return json.load(f)
    return {}


def save_subscribers(data):
    with open(SUBSCRIBERS_FILE, "w") as f:
        json.dump(data, f, indent=2)


def get_subscriber(customer_id):
    return load_subscribers().get(customer_id, {})


def set_subscriber(customer_id, data):
    subs = load_subscribers()
    subs[customer_id] = data
    save_subscribers(subs)


def increment_issue(customer_id):
    """Bump subscriber to next issue. Returns new issue number."""
    subs = load_subscribers()
    sub  = subs.get(customer_id, {"issue": 0})
    sub["issue"] = sub.get("issue", 0) + 1
    sub["last_sent"] = datetime.utcnow().isoformat()
    subs[customer_id] = sub
    save_subscribers(subs)
    return sub["issue"]


# ══════════════════════════════════════════════════════════════
# EMAIL HELPER
# ══════════════════════════════════════════════════════════════

def send_email_with_pdf(to_email, subject, body, pdf_path,
                         from_name, from_email):
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


def get_customer_info(customer_id):
    try:
        c = stripe.Customer.retrieve(customer_id)
        email = c.get("email", "")
        name  = c.get("name", "") or ""
        first = name.split()[0] if name else "Explorer"
        return email, first
    except Exception as e:
        print(f"Stripe error: {e}")
        return None, "Explorer"


def get_group_by_price_id(price_id):
    for key, group in GROUPS.items():
        if price_id in (
            group.get("stripe_monthly_price_id"),
            group.get("stripe_annual_price_id"),
        ):
            return group
    return None


# ══════════════════════════════════════════════════════════════
# SEND ISSUE
# ══════════════════════════════════════════════════════════════

def send_issue(customer_id, email, first_name, group, issue_number):
    """Send the correct issue PDF for this subscriber's position."""
    sequence = group["issue_sequence"]
    titles   = group["issue_titles"]

    if issue_number not in sequence:
        # No more issues yet — send coming soon email
        print(f"No issue {issue_number} yet — sending coming soon")
        subject = group["coming_soon_subject"]
        body    = group["coming_soon_body"].format(first_name=first_name)
        # Send plain email (no PDF)
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

    pdf_path    = sequence[issue_number]
    issue_title = titles.get(issue_number, f"Issue #{issue_number}")

    if issue_number == 1:
        # Welcome email
        subject = group["welcome_subject"]
        body    = group["welcome_body"].format(first_name=first_name)
    else:
        subject = group["monthly_subject"].format(issue_number=issue_number)
        body    = group["monthly_body"].format(
            first_name   = first_name,
            issue_number = issue_number,
            issue_title  = issue_title,
        )

    send_email_with_pdf(
        to_email   = email,
        subject    = subject,
        body       = body,
        pdf_path   = pdf_path,
        from_name  = group["from_name"],
        from_email = group["from_email"],
    )


# ══════════════════════════════════════════════════════════════
# ROUTES
# ══════════════════════════════════════════════════════════════

@app.route("/", methods=["GET"])
def health():
    subs = load_subscribers()
    return jsonify({
        "status":      "ok",
        "service":     "Crystal Blue Press Email Engine v2",
        "subscribers": len(subs),
    })


@app.route("/free-sample", methods=["POST"])
def free_sample():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data"}), 400

    first_name = data.get("first_name", "Explorer").strip()
    email      = data.get("email", "").strip()

    if not email or "@" not in email:
        return jsonify({"error": "Invalid email"}), 400

    success = send_email_with_pdf(
        to_email   = email,
        subject    = FREE_SAMPLE_SUBJECT,
        body       = FREE_SAMPLE_BODY.format(first_name=first_name),
        pdf_path   = FREE_SAMPLE_PDF,
        from_name  = FREE_SAMPLE_FROM_NAME,
        from_email = FREE_SAMPLE_FROM_EMAIL,
    )

    return jsonify({"status": "sent" if success else "failed"}), 200 if success else 500


@app.route("/stripe-webhook", methods=["POST"])
def stripe_webhook():
    payload    = request.get_data()
    sig_header = request.headers.get("Stripe-Signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except stripe.error.SignatureVerificationError:
        return jsonify({"error": "Invalid signature"}), 400

    event_type = event["type"]
    data       = event["data"]["object"]

    # ── NEW SUBSCRIPTION → Issue #1 ───────────────────────────
    if event_type == "customer.subscription.created":
        customer_id = data.get("customer")
        items       = data.get("items", {}).get("data", [])
        price_id    = items[0]["price"]["id"] if items else None

        if not price_id:
            return jsonify({"status": "no price"}), 200

        group = get_group_by_price_id(price_id)
        if not group:
            return jsonify({"status": "unknown group"}), 200

        email, first_name = get_customer_info(customer_id)
        if not email:
            return jsonify({"status": "no email"}), 200

        # Initialize subscriber at issue 1
        set_subscriber(customer_id, {
            "email":      email,
            "first_name": first_name,
            "group":      next(k for k, v in GROUPS.items() if v is group),
            "issue":      1,
            "joined":     datetime.utcnow().isoformat(),
            "last_sent":  datetime.utcnow().isoformat(),
        })

        send_issue(customer_id, email, first_name, group, 1)

    # ── MONTHLY RENEWAL → Next issue ─────────────────────────
    elif event_type == "invoice.payment_succeeded":
        billing_reason = data.get("billing_reason")
        if billing_reason == "subscription_create":
            # Already handled above
            return jsonify({"status": "skipped"}), 200

        customer_id = data.get("customer")
        lines       = data.get("lines", {}).get("data", [])
        price_id    = lines[0]["price"]["id"] if lines else None

        if not price_id:
            return jsonify({"status": "no price"}), 200

        group = get_group_by_price_id(price_id)
        if not group:
            return jsonify({"status": "unknown group"}), 200

        email, first_name = get_customer_info(customer_id)
        if not email:
            return jsonify({"status": "no email"}), 200

        # Increment to next issue
        next_issue = increment_issue(customer_id)

        send_issue(customer_id, email, first_name, group, next_issue)

    # ── CANCELLATION → Log it ─────────────────────────────────
    elif event_type == "customer.subscription.deleted":
        customer_id = data.get("customer")
        subs = load_subscribers()
        if customer_id in subs:
            subs[customer_id]["cancelled"] = datetime.utcnow().isoformat()
            save_subscribers(subs)
            print(f"Subscriber {customer_id} cancelled")

    return jsonify({"status": "ok"}), 200


@app.route("/subscribers", methods=["GET"])
def list_subscribers():
    """Quick dashboard — see all subscribers and their issue progress."""
    subs = load_subscribers()
    summary = []
    for cid, data in subs.items():
        summary.append({
            "email":      data.get("email"),
            "first_name": data.get("first_name"),
            "group":      data.get("group"),
            "issue":      data.get("issue"),
            "joined":     data.get("joined"),
            "cancelled":  data.get("cancelled", None),
        })
    summary.sort(key=lambda x: x["joined"] or "", reverse=True)
    return jsonify({"total": len(summary), "subscribers": summary})


# ══════════════════════════════════════════════════════════════
# RUN
# ══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
