#!/usr/bin/env python3
"""
Gmail email helper for the monthly-content-planner skill.
Sends a summary email to the analyst listing all briefs created this month.

Usage:
  python email_helper.py send <json_rows_file>

json_rows_file: path to a JSON array of row objects with keys:
  brand, heading, target_kw, nw_url, doc_url, position, clicks, impressions

The ANALYST_EMAIL env var (or hardcoded fallback) sets the recipient.
Credentials are loaded from GOOGLE_REFRESH_TOKEN, GOOGLE_CLIENT_ID,
GOOGLE_CLIENT_SECRET in /Users/carlaklaasen/claude_code/.env.
"""

import sys
import os
import json
import base64
import warnings
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
warnings.filterwarnings("ignore")

from dotenv import load_dotenv
load_dotenv("/Users/carlaklaasen/claude_code/.env")

try:
    from googleapiclient.discovery import build
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install",
                           "google-api-python-client", "google-auth", "-q"])
    from googleapiclient.discovery import build
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request

# Analyst email — update when provided
ANALYST_EMAIL = os.getenv("ANALYST_EMAIL", "carla.klaasen@digitad.ca")

CLIENT_ID     = os.getenv("GOOGLE_CLIENT_ID", "")
CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
REFRESH_TOKEN = os.getenv("GOOGLE_REFRESH_TOKEN", "")
TOKEN_URI     = os.getenv("GOOGLE_TOKEN_URI", "https://oauth2.googleapis.com/token")

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]


def get_gmail_service():
    creds = Credentials(
        token=None,
        refresh_token=REFRESH_TOKEN,
        token_uri=TOKEN_URI,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        scopes=SCOPES,
    )
    creds.refresh(Request())
    return build("gmail", "v1", credentials=creds)


def build_html_table(rows: list[dict]) -> str:
    style_table = (
        "border-collapse:collapse;width:100%;font-family:Arial,sans-serif;font-size:13px;"
    )
    style_th = (
        "background:#4A4A8A;color:#fff;padding:8px 12px;text-align:left;border:1px solid #ddd;"
    )
    style_td = "padding:7px 12px;border:1px solid #ddd;vertical-align:top;"
    style_tr_alt = "background:#f5f5fb;"

    headers = ["Brand", "Heading", "Target Keyword", "Pos.", "Clicks", "Impr.", "NW Brief", "Doc Brief"]
    header_html = "".join(f"<th style='{style_th}'>{h}</th>" for h in headers)

    rows_html = ""
    for i, r in enumerate(rows):
        bg = f" style='{style_tr_alt}'" if i % 2 == 1 else ""
        nw_link  = f"<a href='{r.get('nw_url','#')}'>Open</a>"  if r.get('nw_url')  else "—"
        doc_link = f"<a href='{r.get('doc_url','#')}'>Open</a>" if r.get('doc_url') else "—"
        pos   = r.get('position', '—')
        clicks = r.get('clicks', '—')
        impr  = r.get('impressions', '—')
        rows_html += (
            f"<tr{bg}>"
            f"<td style='{style_td}'><b>{r.get('brand','')}</b></td>"
            f"<td style='{style_td}'>{r.get('heading','')}</td>"
            f"<td style='{style_td}'>{r.get('target_kw','')}</td>"
            f"<td style='{style_td}'>{pos}</td>"
            f"<td style='{style_td}'>{clicks}</td>"
            f"<td style='{style_td}'>{impr}</td>"
            f"<td style='{style_td}'>{nw_link}</td>"
            f"<td style='{style_td}'>{doc_link}</td>"
            "</tr>"
        )

    return (
        f"<table style='{style_table}'>"
        f"<thead><tr>{header_html}</tr></thead>"
        f"<tbody>{rows_html}</tbody>"
        "</table>"
    )


def build_email_html(rows: list[dict], month_label: str) -> str:
    table = build_html_table(rows)
    total = len(rows)
    brands = sorted({r.get("brand", "") for r in rows if r.get("brand")})
    brand_list = ", ".join(brands) if brands else "—"

    return f"""
<html><body style="font-family:Arial,sans-serif;color:#333;max-width:900px;margin:0 auto;">
  <h2 style="color:#4A4A8A;">Monthly Content Briefs — {month_label}</h2>
  <p>Hi,</p>
  <p>Here is your automated monthly content brief summary. <b>{total} brief(s)</b> were created
  this month across: <b>{brand_list}</b>.</p>
  <p>The table below includes Neuronwriter and Google Doc links for each brief, plus current
  search landscape data (position, clicks, impressions) pulled from SE Ranking / GSC.</p>
  <br>
  {table}
  <br>
  <p style="font-size:12px;color:#999;">
    Generated automatically by the Digitad monthly-content-planner on {datetime.today().strftime('%Y-%m-%d')}.
    Production plan: <a href="https://docs.google.com/spreadsheets/d/13ZKd5UVG_OcvRS9Wri8c8XSbwqiCguiJBDvUuUN9hbg">View Sheet</a>
  </p>
</body></html>
"""


def send_email(rows: list[dict], month_label: str, recipient: str) -> dict:
    html_body = build_email_html(rows, month_label)
    subject = f"[Digitad] Monthly Content Briefs Ready — {month_label}"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = "me"
    msg["To"] = recipient
    msg.attach(MIMEText(html_body, "html"))

    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    svc = get_gmail_service()
    result = svc.users().messages().send(userId="me", body={"raw": raw}).execute()
    return {"sent": True, "message_id": result.get("id", ""), "recipient": recipient}


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""

    if cmd == "send":
        # send <json_rows_file> [recipient_email] [month_label]
        json_file = sys.argv[2]
        recipient = sys.argv[3] if len(sys.argv) > 3 else ANALYST_EMAIL
        month_label = sys.argv[4] if len(sys.argv) > 4 else datetime.today().strftime("%B %Y")

        with open(json_file) as f:
            rows = json.load(f)

        result = send_email(rows, month_label, recipient)
        print(json.dumps(result))

    elif cmd == "preview":
        # preview <json_rows_file>  — prints HTML to stdout for inspection
        json_file = sys.argv[2]
        month_label = sys.argv[3] if len(sys.argv) > 3 else datetime.today().strftime("%B %Y")
        with open(json_file) as f:
            rows = json.load(f)
        print(build_email_html(rows, month_label))

    else:
        print("Unknown command. Use: send | preview", file=sys.stderr)
        sys.exit(1)
