"""
upload_exports.py  —  seo-geo-technical-audit-v13
==================================================
Uploads a local CSV file to Google Drive as a Google Sheet, or a local
.txt / .md file as a Google Doc. Returns and saves the Drive URL.

    python3 scripts/upload_exports.py \
        --file Outputs/CSV/CLIENT-title-tag-issues.csv \
        --type sheet \
        --folder [GDRIVE_EXPORTS_DIR_ID] \
        --name "CLIENT - Title Tag Issues - April 2026"

Arguments
---------
  --file    Path to the local file to upload (CSV, .txt, or .md)
  --type    "sheet" — convert CSV to Google Sheet
            "doc"   — convert text/markdown to Google Doc
  --folder  Google Drive folder ID for the uploaded file
            If omitted, uses gdrive_exports_dir_id from audit-session-config.json
  --name    Display name for the file in Google Drive

Output
------
  - Prints the Google Drive URL to terminal
  - Writes URL to Outputs/CSV/[filename]-drive-url.txt for local reference

Branding
--------
  Google Sheets: header row formatted with #9b1e22 background, white bold text
  Google Docs:   title formatted with #9b1e22 colour, bold

REQUIREMENTS
------------
  pip install google-api-python-client google-auth gspread python-dotenv
"""

import argparse
import json
import os
import sys

SKILL_ROOT  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(SKILL_ROOT, "audit-session-config.json")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import api_clients

# ── COLOUR ────────────────────────────────────────────────────────────────────
HEADER_RED = {"red": 0.608, "green": 0.118, "blue": 0.133}   # #9b1e22
WHITE      = {"red": 1.0,   "green": 1.0,   "blue": 1.0}


# ── CONFIG LOADING ────────────────────────────────────────────────────────────
def load_config():
    if os.path.isfile(CONFIG_PATH):
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


# ── SHEET UPLOAD ──────────────────────────────────────────────────────────────
def upload_as_sheet(file_path, folder_id, display_name):
    """
    Upload a local CSV to Google Drive as a Google Sheet.
    Applies #9b1e22 header formatting to row 1.
    Returns the Google Drive URL.
    """
    if not os.path.isfile(file_path):
        sys.exit(f"ERROR: File not found: {file_path}")

    from googleapiclient.http import MediaFileUpload

    drive_svc  = api_clients.get_google_drive_client()
    sheets_svc = api_clients.get_google_sheets_service()

    print(f"Uploading {os.path.basename(file_path)} as Google Sheet...")

    # Upload CSV and convert to Google Sheet in one step
    file_metadata = {
        "name":     display_name,
        "mimeType": "application/vnd.google-apps.spreadsheet",
        "parents":  [folder_id],
    }
    media = MediaFileUpload(file_path, mimetype="text/csv", resumable=False)
    uploaded = drive_svc.files().create(
        body=file_metadata,
        media_body=media,
        fields="id",
    ).execute()
    file_id = uploaded["id"]

    # Apply header row formatting
    try:
        # Get sheet ID of first tab
        sheet_meta = sheets_svc.spreadsheets().get(spreadsheetId=file_id).execute()
        sheet_id   = sheet_meta["sheets"][0]["properties"]["sheetId"]
        n_cols     = sheet_meta["sheets"][0]["properties"]["gridProperties"].get("columnCount", 20)

        requests = [
            {
                "repeatCell": {
                    "range": {
                        "sheetId":          sheet_id,
                        "startRowIndex":    0,
                        "endRowIndex":      1,
                        "startColumnIndex": 0,
                        "endColumnIndex":   n_cols,
                    },
                    "cell": {
                        "userEnteredFormat": {
                            "backgroundColor": HEADER_RED,
                            "textFormat": {
                                "foregroundColor": WHITE,
                                "bold": True,
                                "fontSize": 10,
                            },
                        }
                    },
                    "fields": "userEnteredFormat(backgroundColor,textFormat)",
                }
            },
            {
                "updateSheetProperties": {
                    "properties": {
                        "sheetId": sheet_id,
                        "gridProperties": {"frozenRowCount": 1},
                    },
                    "fields": "gridProperties.frozenRowCount",
                }
            },
        ]
        sheets_svc.spreadsheets().batchUpdate(
            spreadsheetId=file_id,
            body={"requests": requests},
        ).execute()
    except Exception as e:
        print(f"  Warning: Could not apply header formatting: {e}")

    url = f"https://docs.google.com/spreadsheets/d/{file_id}"
    return url


# ── DOC UPLOAD ────────────────────────────────────────────────────────────────
def upload_as_doc(file_path, folder_id, display_name):
    """
    Upload a local .txt or .md file to Google Drive as a Google Doc.
    Applies a simple title style. Returns the Google Drive URL.
    """
    if not os.path.isfile(file_path):
        sys.exit(f"ERROR: File not found: {file_path}")

    from googleapiclient.http import MediaFileUpload

    drive_svc = api_clients.get_google_drive_client()
    docs_svc  = api_clients.get_google_docs_client()

    print(f"Uploading {os.path.basename(file_path)} as Google Doc...")

    # Determine MIME type based on extension
    ext = os.path.splitext(file_path)[1].lower()
    src_mime = "text/markdown" if ext == ".md" else "text/plain"

    file_metadata = {
        "name":     display_name,
        "mimeType": "application/vnd.google-apps.document",
        "parents":  [folder_id],
    }
    media = MediaFileUpload(file_path, mimetype=src_mime, resumable=False)
    uploaded = drive_svc.files().create(
        body=file_metadata,
        media_body=media,
        fields="id",
    ).execute()
    file_id = uploaded["id"]

    # Apply title formatting to first paragraph
    try:
        doc = docs_svc.documents().get(documentId=file_id).execute()
        content = doc.get("body", {}).get("content", [])
        # Find the first text run and apply heading style + brand colour
        if content and len(content) > 1:
            first_elem = content[1]
            para = first_elem.get("paragraph", {})
            elements = para.get("elements", [])
            if elements:
                start = elements[0].get("startIndex", 1)
                end   = elements[-1].get("endIndex", 2)
                docs_svc.documents().batchUpdate(
                    documentId=file_id,
                    body={"requests": [
                        {
                            "updateParagraphStyle": {
                                "range": {"startIndex": start, "endIndex": end},
                                "paragraphStyle": {"namedStyleType": "HEADING_1"},
                                "fields": "namedStyleType",
                            }
                        }
                    ]},
                ).execute()
    except Exception as e:
        print(f"  Warning: Could not apply Doc title formatting: {e}")

    url = f"https://docs.google.com/document/d/{file_id}"
    return url


# ── URL SAVER ─────────────────────────────────────────────────────────────────
def save_url_locally(file_path, url):
    """Write the Drive URL to a sidecar .txt file next to the local source file."""
    base     = os.path.splitext(file_path)[0]
    url_file = f"{base}-drive-url.txt"
    with open(url_file, "w", encoding="utf-8") as f:
        f.write(url + "\n")
    return url_file


# ── MAIN ──────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="Upload a local file to Google Drive — seo-geo-technical-audit v13"
    )
    parser.add_argument("--file",   required=True,  help="Local file path to upload")
    parser.add_argument("--type",   required=True,  choices=["sheet", "doc"],
                        help="sheet = CSV → Google Sheet | doc = text/md → Google Doc")
    parser.add_argument("--folder", default="",     help="Google Drive folder ID")
    parser.add_argument("--name",   default="",     help="Display name in Google Drive")
    args = parser.parse_args()

    # Resolve folder ID
    folder_id = args.folder
    if not folder_id:
        config    = load_config()
        folder_id = config.get("gdrive_exports_dir_id", "").strip()
    if not folder_id:
        sys.exit(
            "ERROR: No folder ID provided. Either pass --folder or ensure "
            "gdrive_exports_dir_id is set in audit-session-config.json."
        )

    # Derive display name from filename if not given
    display_name = args.name or os.path.splitext(os.path.basename(args.file))[0]

    # Upload
    if args.type == "sheet":
        url = upload_as_sheet(args.file, folder_id, display_name)
    else:
        url = upload_as_doc(args.file, folder_id, display_name)

    # Save URL locally
    url_file = save_url_locally(args.file, url)

    print(f"\nUploaded: {display_name}")
    print(f"Drive URL: {url}")
    print(f"URL saved to: {url_file}")
    print(f"\nAdd this URL to the Sources column of the corresponding scoring row.")

    return url


if __name__ == "__main__":
    main()
