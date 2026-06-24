# ══════════════════════════════════════════════════════════════
# CRYSTAL BLUE PRESS — EMAIL ENGINE CONFIG v2
# ══════════════════════════════════════════════════════════════

# ── OTTER PUPS CLUB ISSUE SEQUENCE ───────────────────────────
# Add new issues here as you create them.
# File goes in the /pdfs folder on GitHub.
# Issue number = month number since subscriber joined.


import os

OTTER_PUPS_ISSUES = {
    0:  "pdfs/otter_pups_free_sample.pdf",        # Welcome / Free sample
    1:  "pdfs/issue_01_bluebonnet.pdf",            # Texas Hill Country
    2:  "pdfs/issue_02_big_bend.pdf",              # Big Bend
    3:  "pdfs/issue_03_grand_canyon.pdf",          # Grand Canyon
    4:  "pdfs/issue_04_yellowstone.pdf",           # Yellowstone
    5:  "pdfs/issue_05_grand_teton.pdf",           # Grand Teton
    6:  "pdfs/issue_06_zion.pdf",                  # Zion
    7:  "pdfs/issue_07_arches.pdf",                # Arches
    8:  "pdfs/issue_08_great_smoky.pdf",           # Great Smoky Mountains
    9:  "pdfs/issue_09_glacier.pdf",               # Glacier
    10: "pdfs/issue_10_acadia.pdf",                # Acadia
    11: "pdfs/issue_11_saguaro.pdf",               # Saguaro
    12: "pdfs/issue_12_hawaii_volcanoes.pdf",      # Hawaii Volcanoes
    # Add Year 2 issues here as you build them:
    # 13: "pdfs/issue_13_xxx.pdf",
    # 14: "pdfs/issue_14_xxx.pdf",
}

OTTER_PUPS_ISSUE_TITLES = {
    0:  "The Lantern Shore Treasure Hunt",
    1:  "The Bluebonnet Adventure — Texas Hill Country",
    2:  "The Big Bend Adventure",
    3:  "The Grand Canyon Adventure",
    4:  "The Yellowstone Adventure",
    5:  "The Grand Teton Adventure",
    6:  "The Zion Adventure",
    7:  "The Arches Adventure",
    8:  "The Great Smoky Mountains Adventure",
    9:  "The Glacier Adventure",
    10: "The Acadia Adventure",
    11: "The Saguaro Adventure",
    12: "The Hawai'i Volcanoes Adventure",
}

# ── GROUPS ────────────────────────────────────────────────────
# Each group can have its own issue sequence.
# Add new groups here as you launch them.

GROUPS = {

    "otter_pups_club": {
        "name":                    "Otter Pups Club",
        "stripe_monthly_price_id": "YOUR_STRIPE_MONTHLY_PRICE_ID",
        "stripe_annual_price_id":  "YOUR_STRIPE_ANNUAL_PRICE_ID",
        "issue_sequence":          OTTER_PUPS_ISSUES,
        "issue_titles":            OTTER_PUPS_ISSUE_TITLES,
        "from_name":               "Otter Pups Club",
        "from_email":              "hello@crystalbluepress.com",
        "welcome_subject":         "🐾 Welcome to the Otter Pups Club! Issue #1 is Here!",
        "welcome_body": """Hi {first_name}!

Welcome to the Otter Pups Club! 🦦

Finn, Ollie, and Lila are SO excited you joined the adventure.

Your first Explorer Pack — Issue #1: The Bluebonnet Adventure — is attached!

Print it out, gather the family, and let the adventure begin.

Every month you'll receive the next issue automatically. Here's what's coming:
  Issue #2 — The Big Bend Adventure
  Issue #3 — The Grand Canyon Adventure
  Issue #4 — The Yellowstone Adventure
  ...all the way through all 63 U.S. National Parks!

Adventure awaits, Otter Pup!
— The Crystal Blue Press Team
crystalbluepress.com""",

        "monthly_subject":  "🐾 Your Otter Pups Club Issue #{issue_number} is Here!",
        "monthly_body": """Hi {first_name}!

Your new Otter Pups Explorer Pack just arrived! 🦦

Issue #{issue_number}: {issue_title}

It's attached to this email — print it out and explore!

See you next month,
— The Crystal Blue Press Team
crystalbluepress.com""",

        "coming_soon_subject": "🐾 Your Next Adventure is Coming Soon!",
        "coming_soon_body": """Hi {first_name}!

You've completed all current Otter Pups Club issues — amazing! 🦦

Our team is hard at work on the next adventure and it will be in your inbox very soon.

Thank you for exploring with Finn, Ollie, and Lila!
— The Crystal Blue Press Team""",
    },

    # ── ADD NEW GROUPS HERE ───────────────────────────────────
    # "math_academy": {
    #     "name": "Math Academy",
    #     "stripe_monthly_price_id": "https://buy.stripe.com/4gMcN56EE9Hr0C07DpfnO01",
    #     "stripe_annual_price_id":  "YOUR_PRICE_ID",
    #     "issue_sequence": MATH_ACADEMY_ISSUES,
    #     "issue_titles":   MATH_ACADEMY_TITLES,
    #     "from_name":      "Math Academy",
    #     "from_email":     "hello@crystalbluepress.com",
    #     "welcome_subject": "Welcome to Math Academy!",
    #     "welcome_body":    "Hi {first_name}! ...",
    #     "monthly_subject": "Your Month #{issue_number} Math Pack!",
    #     "monthly_body":    "Hi {first_name}! Issue #{issue_number}...",
    # },
}

# ── STRIPE ────────────────────────────────────────────────────
STRIPE_SECRET_KEY     = "pk_live_51TfqVzErGSVifBGvipWPEmjM4vdd8irCW8cUM6k9tAUPIr2mOrMUlDizPvuUcC5bTz30MrM6ZIrljZCfFVjA3DWY00jbO764EZ"
STRIPE_WEBHOOK_SECRET = "YOUR_STRIPE_WEBHOOK_SECRET"

# ── SENDGRID ──────────────────────────────────────────────────
SENDGRID_API_KEY      = os.environ.get(“SENDGRID_API_KEY”)

# ── FREE SAMPLE ───────────────────────────────────────────────
FREE_SAMPLE_PDF        = "pdfs/otter_pups_free_sample.pdf"
FREE_SAMPLE_FROM_NAME  = "Otter Pups Club"
FREE_SAMPLE_FROM_EMAIL = "hello@crystalbluepress.com"
FREE_SAMPLE_SUBJECT    = "🐾 Your Free Otter Pups Explorer Pack!"
FREE_SAMPLE_BODY       = """Hi {first_name}!

Your free Otter Pups Club sample adventure is attached! 🦦

Inside you'll find a story, activities, coloring pages, nature discovery, and more.

If your family loves it, join us for a new national park adventure every month:
  👉 Monthly: $9.99/month
  👉 Annual:  $99/year (2 months free!)

Explore all 63 U.S. National Parks with Finn, Ollie & Lila — one adventure at a time.

Adventure awaits!
— The Crystal Blue Press Team
crystalbluepress.com"""
