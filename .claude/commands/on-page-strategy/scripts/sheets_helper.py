#!/usr/bin/env python3
"""
Google Sheets helper for the on-page-strategy skill.
Usage:
  python sheets_helper.py read   <spreadsheet_id> <tab_name> <range>
  python sheets_helper.py headers <spreadsheet_id> <tab_name>
  python sheets_helper.py write  <spreadsheet_id> <tab_name> <start_row> <json_rows_file>
  python sheets_helper.py last_row <spreadsheet_id> <tab_name>

All operations use the service account from GOOGLE_SERVICE_ACCOUNT_FILE env var
or the default path.
"""

import sys
import os
import json
import warnings
warnings.filterwarnings("ignore")

from dotenv import load_dotenv
load_dotenv("/Users/carlaklaasen/claude_code/.env")

from googleapiclient.discovery import build
from google.oauth2 import service_account

SA_FILE = os.getenv(
    "GOOGLE_SERVICE_ACCOUNT_FILE",
    "/Users/carlaklaasen/claude_code/content_automation/content-automation-492519-da1e80a65441.json"
)
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


def get_service():
    creds = service_account.Credentials.from_service_account_file(SA_FILE, scopes=SCOPES)
    return build("sheets", "v4", credentials=creds)


def read_range(spreadsheet_id, tab_name, range_notation):
    """Read a range from a sheet. range_notation like 'A1:Z100'"""
    svc = get_service()
    full_range = f"'{tab_name}'!{range_notation}"
    result = svc.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=full_range
    ).execute()
    rows = result.get("values", [])
    print(json.dumps(rows))


def get_headers(spreadsheet_id, tab_name):
    """Return first 5 rows (to find header row) as JSON."""
    svc = get_service()
    full_range = f"'{tab_name}'!A1:Z5"
    result = svc.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=full_range
    ).execute()
    rows = result.get("values", [])
    print(json.dumps(rows))


def get_last_data_row(spreadsheet_id, tab_name):
    """Return the index (1-based) of the last non-empty row in column B."""
    svc = get_service()
    full_range = f"'{tab_name}'!B1:B1000"
    result = svc.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=full_range
    ).execute()
    rows = result.get("values", [])
    print(json.dumps({"last_row": len(rows)}))


def write_rows(spreadsheet_id, tab_name, start_row, json_rows_file):
    """
    Write rows to the sheet starting at start_row.
    json_rows_file: path to a JSON file containing a list of row arrays.
    Each row array has values for columns A through P (index 0–15).
    Only columns B, H, I, J, K, L, M, P are written (others left blank).
    Column mapping (1-indexed): A=1, B=2, H=8, I=9, J=10, K=11, L=12, M=13, P=16
    """
    with open(json_rows_file) as f:
        rows_data = json.load(f)

    svc = get_service()
    values = []
    for row in rows_data:
        # Build a 16-element array (A through P), blank except for our columns
        cells = [""] * 16
        cells[1]  = row.get("website", "")   # B
        cells[7]  = row.get("type", "")       # H
        cells[8]  = row.get("language", "EN") # I
        cells[9]  = str(row.get("words", "")) # J
        cells[10] = row.get("heading", "")    # K
        cells[11] = row.get("target_kw", "")  # L
        cells[12] = row.get("secondary_kw", "")  # M
        cells[15] = row.get("url", "")        # P
        values.append(cells)

    end_row = start_row + len(values) - 1
    full_range = f"'{tab_name}'!A{start_row}:P{end_row}"

    body = {"values": values}
    svc.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=full_range,
        valueInputOption="USER_ENTERED",
        body=body
    ).execute()

    print(json.dumps({
        "written": len(values),
        "start_row": start_row,
        "end_row": end_row,
        "range": full_range
    }))


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""

    if cmd == "read":
        read_range(sys.argv[2], sys.argv[3], sys.argv[4])
    elif cmd == "headers":
        get_headers(sys.argv[2], sys.argv[3])
    elif cmd == "last_row":
        get_last_data_row(sys.argv[2], sys.argv[3])
    elif cmd == "write":
        write_rows(sys.argv[2], sys.argv[3], int(sys.argv[4]), sys.argv[5])
    else:
        print("Unknown command. Use: read | headers | last_row | write", file=sys.stderr)
        sys.exit(1)
