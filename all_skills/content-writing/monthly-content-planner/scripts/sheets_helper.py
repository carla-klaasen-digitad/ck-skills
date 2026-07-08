#!/usr/bin/env python3
"""
Google Sheets + brand-scan helper for monthly-content-planner.

Commands:
  scan_brands <guidelines_dir>          -- scan .md files, return approved brands JSON
  read_rows --sheet-id ID --tab TAB --month MONTH --year YEAR
  write_cell --sheet-id ID --tab TAB --row N --col LETTER --value VAL
  pull_keyword_data --keyword KW --website URL
"""

import sys, os, json, re, argparse, warnings
warnings.filterwarnings("ignore")

from dotenv import load_dotenv
load_dotenv("/Users/carlaklaasen/claude_code/.env")

from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

SE_API_KEY = os.getenv("SE_RANKING_API_KEY", "")

SCOPES_SHEETS = ["https://www.googleapis.com/auth/spreadsheets"]


def sheets_service():
    creds = Credentials(
        token=None,
        refresh_token=os.getenv("GOOGLE_REFRESH_TOKEN", ""),
        token_uri=os.getenv("GOOGLE_TOKEN_URI", "https://oauth2.googleapis.com/token"),
        client_id=os.getenv("GOOGLE_CLIENT_ID", ""),
        client_secret=os.getenv("GOOGLE_CLIENT_SECRET", ""),
        scopes=SCOPES_SHEETS,
    )
    creds.refresh(Request())
    return build("sheets", "v4", credentials=creds)


# ─── Column helpers ────────────────────────────────────────────────────────────
COL_MAP = {
    "A": 0, "B": 1, "C": 2, "D": 3, "E": 4,
    "F": 5, "G": 6, "H": 7, "I": 8, "J": 9,
    "K": 10, "L": 11, "M": 12, "N": 13, "O": 14,
    "P": 15, "Q": 16, "R": 17,
}

def col_letter_to_index(letter):
    return COL_MAP.get(letter.upper(), 0)

def safe_get(row, idx, default=""):
    try:
        val = row[idx]
        return val.strip() if isinstance(val, str) else str(val).strip()
    except IndexError:
        return default


# ─── scan_brands ───────────────────────────────────────────────────────────────
def scan_brands(guidelines_dir):
    results = []
    for fname in sorted(os.listdir(guidelines_dir)):
        if not fname.endswith(".md") or fname == "general_legal.md":
            continue
        path = os.path.join(guidelines_dir, fname)
        content = open(path, encoding="utf-8").read()
        brand_key = fname.replace(".md", "")

        def field(n):
            m = re.search(rf"{n}\.\s*[^:]+:\s*(.+)", content, re.IGNORECASE)
            return m.group(1).strip() if m else ""

        status = field("2")
        if not re.search(r"appro", status, re.IGNORECASE):
            continue

        website_url = field("1")
        tab_name = field("4").strip("'\"")
        folder_url = field("5")
        template_url = field("6")
        nw_url = field("7")

        # Extract IDs from URLs
        folder_id_m = re.search(r"drive\.google\.com/drive/folders/([A-Za-z0-9_-]+)", folder_url)
        template_id_m = re.search(r"docs\.google\.com/document/d/([A-Za-z0-9_-]+)", template_url)
        nw_project_id_m = re.search(r"neuronwriter\.com/project/view/([A-Za-z0-9_-]+)", nw_url)

        results.append({
            "brand_key": brand_key,
            "brand_label": brand_key.upper(),
            "website_url": website_url,
            "tab_name": tab_name,
            "folder_id": folder_id_m.group(1) if folder_id_m else "",
            "template_doc_id": template_id_m.group(1) if template_id_m else "",
            "nw_project_id": nw_project_id_m.group(1) if nw_project_id_m else "",
        })

    print(json.dumps(results, indent=2))


# ─── read_rows ─────────────────────────────────────────────────────────────────
def read_rows(sheet_id, tab_name, month, year):
    svc = sheets_service()
    range_str = f"'{tab_name}'!A1:R500"
    result = svc.spreadsheets().values().get(
        spreadsheetId=sheet_id, range=range_str
    ).execute()
    all_rows = result.get("values", [])

    # Detect Month/Year columns by scanning the header row (rows 1-5)
    month_col_idx = col_letter_to_index("E")  # default
    year_col_idx  = col_letter_to_index("F")  # default
    for hrow in all_rows[:6]:
        for ci, cell in enumerate(hrow):
            cv = str(cell).strip().lower()
            if cv == "month":
                month_col_idx = ci
            elif cv == "year":
                year_col_idx = ci

    eligible = []
    for i, row in enumerate(all_rows):
        col_month = safe_get(row, month_col_idx)
        col_year  = safe_get(row, year_col_idx)
        col_n = safe_get(row, col_letter_to_index("N"))
        col_l = safe_get(row, col_letter_to_index("L"))

        if col_month.lower().rstrip(".") != month.lower().rstrip("."):
            continue
        if str(col_year).strip() != str(year).strip():
            continue
        if col_n.strip():        # already has a brief link
            continue
        if not col_l.strip():   # no target keyword
            continue

        eligible.append({
            "row_index": i + 1,   # 1-based sheet row
            "col_b": safe_get(row, col_letter_to_index("B")),
            "col_c": safe_get(row, col_letter_to_index("C")),
            "col_k": safe_get(row, col_letter_to_index("K")),
            "col_l": col_l,
            "col_m": safe_get(row, col_letter_to_index("M")),
            "col_n": col_n,
            "col_p": safe_get(row, col_letter_to_index("P")),
            "col_q": safe_get(row, col_letter_to_index("Q")),
        })

    print(json.dumps(eligible, indent=2))


# ─── write_cell ────────────────────────────────────────────────────────────────
def write_cell(sheet_id, tab_name, row_num, col_letter, value):
    svc = sheets_service()
    cell_ref = f"'{tab_name}'!{col_letter.upper()}{row_num}"
    svc.spreadsheets().values().update(
        spreadsheetId=sheet_id,
        range=cell_ref,
        valueInputOption="USER_ENTERED",
        body={"values": [[value]]}
    ).execute()
    print(json.dumps({"ok": True, "cell": cell_ref, "value": value}))


# ─── pull_keyword_data ─────────────────────────────────────────────────────────
def pull_keyword_data(keyword, website):
    """Pull position, clicks, impressions from SE Ranking API."""
    import urllib.request, urllib.parse
    if not SE_API_KEY:
        print(json.dumps({"keyword": keyword, "position": "-", "clicks": "-", "impressions": "-", "error": "no_api_key"}))
        return

    # Clean domain for SE Ranking
    domain = re.sub(r"https?://", "", website).rstrip("/")

    try:
        params = urllib.parse.urlencode({
            "key": SE_API_KEY,
            "url": domain,
            "query": keyword,
            "se": "google.com",
            "regions": "us",
        })
        req = urllib.request.Request(
            f"https://api4.seranking.com/v1/site/keywords/search?{params}",
            headers={"Accept": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
        pos = data.get("position", "-")
        clicks = data.get("clicks", "-")
        impressions = data.get("impressions", "-")
    except Exception as e:
        pos = clicks = impressions = "-"

    print(json.dumps({
        "keyword": keyword,
        "position": pos,
        "clicks": clicks,
        "impressions": impressions,
    }))


# ─── CLI dispatch ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""

    if cmd == "scan_brands":
        scan_brands(sys.argv[2])

    elif cmd == "read_rows":
        p = argparse.ArgumentParser()
        p.add_argument("--sheet-id"); p.add_argument("--tab")
        p.add_argument("--month"); p.add_argument("--year")
        args = p.parse_args(sys.argv[2:])
        read_rows(args.sheet_id, args.tab, args.month, args.year)

    elif cmd == "write_cell":
        p = argparse.ArgumentParser()
        p.add_argument("--sheet-id"); p.add_argument("--tab")
        p.add_argument("--row", type=int); p.add_argument("--col")
        p.add_argument("--value")
        args = p.parse_args(sys.argv[2:])
        write_cell(args.sheet_id, args.tab, args.row, args.col, args.value)

    elif cmd == "pull_keyword_data":
        p = argparse.ArgumentParser()
        p.add_argument("--keyword"); p.add_argument("--website")
        args = p.parse_args(sys.argv[2:])
        pull_keyword_data(args.keyword, args.website)

    else:
        print(f"Unknown command: {cmd}", file=sys.stderr)
        sys.exit(1)
