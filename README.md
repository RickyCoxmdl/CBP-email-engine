# CBP Email Engine

Crystal Blue Press — Subscription Email Engine v2

Handles monthly issue delivery for the Otter Pups Club subscription service.

## What It Does

- Accepts Stripe webhook events
- Sends Issue 1 when a new subscriber signs up
- Automatically sends the next issue every month on renewal
- Tracks each subscriber's progress through the issue sequence
- Handles cancellations and coming soon emails

## Services Used

- Flask — web server
- Stripe — payments and webhooks
- SendGrid — email delivery with PDF attachments
- Render — hosting

## Files

- server_v2.py — main application
- config_v2.py — issue sequence and email templates
- requirements.txt — Python dependencies
- Procfile — Render startup command
- pdfs folder — issue PDF files

## Crystal Blue Press

crystalbluepress.com
