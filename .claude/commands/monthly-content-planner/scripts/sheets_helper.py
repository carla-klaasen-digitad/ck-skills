#!/usr/bin/env python3
"""
Google Sheets + brand-scan helper for monthly-content-planner.

Commands:
  scan_brands <guidelines_dir>          -- scan .md files, return approved brands JSON
  read_rows --sheet-id ID --tab TAB --month MONTH --year YEAR --col-map JSON
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

def col_letter_to_index(letter):
    """Convert column letter(s) to 0-based index. Supports A-Z and AA-ZZ."""
    letter = letter.upper().strip()
    result = 0
    for ch in letter:
        result = result * 26 + (ord(ch) - ord('A') + 1)
    return result - 1

def safe_get(row, idx, default=""):
    try:
        val = row[idx]
        return val.strip() if isinstance(val, str) else str(val).strip()
    except IndexError:
        return default

def parse_col_map(col_map_str):
    """
    Parse '9. Column Mapping: month=D, year=E, heading=K, ...' into a dict.
    Returns e.g. {'month': 'D', 'year': 'E', 'heading': 'K', ...}
    """
    result = {}
    for part in col_map_str.split(","):
        part = part.strip()
        if "=" in part:
            k, v = part.split("=", 1)
            result[k.strip().lower()] = v.strip().upper()
    return result


# ─── scan_brands ───────────────────────────────────────────────────────────────
def scan_brands(guidelines_dir):
    results = []
    for fname in sorted(os.listdir(guidelines_dir)):
        if not fname.endswith(".md") or fname == "general_legal.md":
            continue
        path = os.path.join(guidelines_dir, fname)
        content = open(path, encoding="utf-8").read()
        brand_key = fname.replace(".md", "")

        def field(n, pattern=None):
            # Match numbered field like "1. Website:" or "6b. Template (EN):"
            if pattern:
                m = re.search(pattern, content, re.IGNORECASE | re.MULTILINE)
            else:
                m = re.search(rf"^{n}\.\s*[^:]+:\s*(.+)", content, re.IGNORECASE | re.MULTILINE)
            return m.group(1).strip() if m else ""

        status = field("2")
        if not re.search(r"appro", status, re.IGNORECASE):
            continue

        website_url = field("1")
        tab_name = field("4").strip("'\"")
        folder_url = field("5")
        template_url = field("6")
        template_en_url = field(None, pattern=r"^6b\.\s*[^:]+:\s*(.+)")
        nw_url = field("7")
        # Column Mapping may be field 8 or 9 depending on brand file
        col_map_raw = field(None, pattern=r"^\d+\.\s*Column Mapping:\s*(.+)")

        # Extract IDs from URLs
        folder_id_m = re.search(r"drive\.google\.com/drive/folders/([A-Za-z0-9_-]+)", folder_url)
        template_id_m = re.search(r"docs\.google\.com/document/d/([A-Za-z0-9_-]+)", template_url)
        template_en_id_m = re.search(r"docs\.google\.com/document/d/([A-Za-z0-9_-]+)", template_en_url) if template_en_url else None
        nw_project_id_m = re.search(r"neuronwriter\.com/project/view/([A-Za-z0-9_-]+)", nw_url)

        col_map = parse_col_map(col_map_raw) if col_map_raw else {
            "month": "D", "year": "E", "heading": "K", "keyword": "L",
            "secondary": "M", "type": "H", "url": "P",
            "doc_output": "N", "nw_output": "Q", "status": "C",
            "header_row": "4",
        }

        entry = {
            "brand_key": brand_key,
            "brand_label": brand_key.upper(),
            "website_url": website_url,
            "tab_name": tab_name,
            "folder_id": folder_id_m.group(1) if folder_id_m else "",
            "template_doc_id": template_id_m.group(1) if template_id_m else "",
            "template_en_doc_id": template_en_id_m.group(1) if template_en_id_m else "",
            "nw_project_id": nw_project_id_m.group(1) if nw_project_id_m else "",
            "col_map": col_map,
        }
        results.append(entry)

    print(json.dumps(results, indent=2))


# ─── read_rows ─────────────────────────────────────────────────────────────────
def read_rows(sheet_id, tab_name, month, year, col_map=None):
    if col_map is None:
        col_map = {}

    # Resolve column indices from col_map (or defaults)
    def ci(key, default_letter):
        return col_letter_to_index(col_map.get(key, default_letter))

    heading_ci = ci("heading", "K")
    keyword_ci = ci("keyword", "L")
    secondary_ci = ci("secondary", "M")
    type_ci   = ci("type",    "H")
    language_ci = ci("language", "I")
    url_ci    = ci("url",     "P")
    doc_out_ci = ci("doc_output", "N")
    nw_out_ci = ci("nw_output", "Q")
    status_ci = ci("status",  "C")
    b_ci = col_letter_to_index("B")

    header_row = int(col_map.get("header_row", "1"))

    # month_ci / year_ci are resolved after reading the sheet header (auto-detect first)
    month_ci_from_map = ci("month", "E")   # col_map hint, default E
    year_ci_from_map  = ci("year",  "F")   # col_map hint, default F

    svc = sheets_service()

    # Determine last relevant column
    max_ci = max(month_ci_from_map, year_ci_from_map, heading_ci, keyword_ci,
                 secondary_ci, type_ci, language_ci, url_ci, doc_out_ci,
                 nw_out_ci, status_ci) + 1
    # Convert max 0-based index back to letter for range
    def idx_to_col(n):
        s = ""
        n += 1
        while n:
            n, r = divmod(n - 1, 26)
            s = chr(65 + r) + s
        return s

    last_col = idx_to_col(max_ci)
    range_str = f"'{tab_name}'!A1:{last_col}500"

    result = svc.spreadsheets().values().get(
        spreadsheetId=sheet_id, range=range_str
    ).execute()
    all_rows = result.get("values", [])

    # Auto-detect Month/Year columns from header rows (override col_map hint if found)
    month_ci = month_ci_from_map
    year_ci  = year_ci_from_map
    for hrow in all_rows[:header_row + 1]:
        for hci, cell in enumerate(hrow):
            cv = str(cell).strip().lower()
            if cv == "month":
                month_ci = hci
            elif cv == "year":
                year_ci = hci

    eligible = []
    for i, row in enumerate(all_rows):
        # Skip header rows
        if i < header_row:
            continue

        col_month = safe_get(row, month_ci)
        col_year  = safe_get(row, year_ci)
        col_doc   = safe_get(row, doc_out_ci)
        col_kw    = safe_get(row, keyword_ci)
        col_type  = safe_get(row, type_ci).lower()
        col_lang  = safe_get(row, language_ci)

        if col_month.lower().rstrip(".") != month.lower().rstrip("."):
            continue
        if str(col_year).strip() != str(year).strip():
            continue
        if col_doc.strip():         # already has a brief link
            continue
        if not col_kw.strip():      # no target keyword
            continue
        # Skip translation rows
        if re.search(r"translat|traduction", col_type, re.IGNORECASE):
            continue

        # Parse search demand from keyword cell: "keyword (10,000)" or "keyword [10,000]"
        kw_clean = col_kw
        search_demand = ""
        sd_m = re.search(r'^(.*?)\s*[\(\[]([\d,]+)[\)\]]?\s*$', col_kw)
        if sd_m:
            kw_clean     = sd_m.group(1).strip()
            search_demand = sd_m.group(2).strip()

        eligible.append({
            "row_index": i + 1,     # 1-based sheet row
            "col_b": safe_get(row, b_ci),
            "col_c": safe_get(row, status_ci),
            "col_k": safe_get(row, heading_ci),
            "col_l": kw_clean,           # keyword without search demand
            "col_l_raw": col_kw,         # original cell value
            "col_l_search_demand": search_demand,
            "col_m": safe_get(row, secondary_ci),
            "col_n": col_doc,
            "col_h": safe_get(row, type_ci),   # content type
            "col_i": col_lang,                  # language (Mitacs)
            "col_p": safe_get(row, url_ci),
            "col_q": safe_get(row, nw_out_ci),
            # Pass back the column letters for write-back
            "doc_output_col": col_map.get("doc_output", "N"),
            "nw_output_col": col_map.get("nw_output", "Q"),
            "status_col": col_map.get("status", "C"),
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
    except Exception:
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
        p.add_argument("--col-map", default="{}")
        args = p.parse_args(sys.argv[2:])
        col_map = json.loads(args.col_map)
        read_rows(args.sheet_id, args.tab, args.month, args.year, col_map)

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
