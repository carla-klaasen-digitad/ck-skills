"""
generate_gsheet.py  —  seo-geo-technical-audit-v14
===================================================
Replaces generate_workbook.py as the primary deliverable pipeline.
Reads workbook_data.json (produced by extract_data.py) and creates (or
writes to) a Google Sheet in the configured Google Drive directory.

HOW TO USE
----------
1. Run extract_data.py first to produce workbook_data.json.
2. Set AUDIT_DIR below to match the client project root.
3. To create a new sheet: leave SHEET_ID empty. Set AUDIT_DIR only.
   To write to an existing sheet: set SHEET_ID and TAB_NAME.
4. Run: python3 scripts/generate_gsheet.py
   The script reads CLIENT_NAME and AUDIT_DATE from workbook_data.json.
   Google Drive directory is read from audit-session-config.json.

OUTPUT
------
  - Google Sheet created in GDRIVE_MAIN_DIR_ID folder (or written to SHEET_ID)
  - URL printed to terminal
  - URL written to {AUDIT_DIR}/Workbook/workbook_url.txt

TABS (5)
--------
  1. Performances summary  — phase scorecard, HIGH items, exec summary
  2. Detailed Technical Audit (or TAB_NAME) — all 122 rows, 19-column template layout
  3. Schema Analysis        — schema sub-phase output (if CSV present)
  4. Sources                — unique source documents from audit
  5. Glossary               — Analyzed Element + Description reference

COLUMN LAYOUT (Detailed Technical Audit — 19 columns A–S)
----------------------------------------------------------
  A(blank) | B(Status) | C(Family) | D(Category) | E(Sub-Category) |
  F(Analyzed Element) | G(Description) | H(Score) |
  I(Weight/Importance Numeric) | J(Importance Tier) | K(Priority Score) |
  L(Score Explanation) | M(Priority) | N(Who's in charge?) |
  O(Data Analyzed) | P(How to correct?) | Q(Comments) | R(Sources) |
  S(Comments for Claude)   ← user-filled post-delivery; empty from script

REQUIREMENTS
------------
  pip install google-api-python-client google-auth gspread python-dotenv openpyxl
"""

import csv
import json
import os
import sys
import time

# Resolve skill root from scripts/ location
SKILL_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(SKILL_ROOT, "audit-session-config.json")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import api_clients

# ── CLIENT CONFIGURATION ─────────────────────────────────────────────────────
# Set AUDIT_DIR to the client project root. All other values are read
# automatically from workbook_data.json and audit-session-config.json.
AUDIT_DIR = ""   # e.g. "/Users/username/projects/client_audit"

INCLUDE_SCHEMA = False  # Set True when schema CSV exists

# ── OUTPUT MODE ───────────────────────────────────────────────────────────────
# Leave SHEET_ID empty to CREATE a new Google Sheet in GDRIVE_MAIN_DIR_ID.
# Set SHEET_ID to write audit data into an existing spreadsheet by ID.
#   SHEET_ID: the long string between /d/ and /edit in the Sheet URL.
#   TAB_NAME: the tab to write the main audit data into (created if absent).
SHEET_ID = ""                    # e.g. "1_Lm66qr-n4wM6B3gC7221GTB1tgKCJM5n7e2cbi-xBk"
TAB_NAME = "Technical Audit"     # Used only when SHEET_ID is set

# ── COLOURS (Google Sheets API — RGB values, 0.0–1.0 scale) ──────────────────
HEADER_RED = {"red": 0.608, "green": 0.118, "blue": 0.133}   # #9b1e22

PRIORITY_FILLS = {
    "HIGH":                         {"red": 0.957, "green": 0.800, "blue": 0.800},
    "MEDIUM":                       {"red": 0.988, "green": 0.910, "blue": 0.698},
    "LOW":                          {"red": 0.718, "green": 0.882, "blue": 0.804},
    "MONITOR":                      {"red": 0.749, "green": 0.749, "blue": 0.749},
    "Manual Verification Required": {"red": 0.788, "green": 0.855, "blue": 0.973},
}

PHASE_GREEN = {"red": 0.851, "green": 0.918, "blue": 0.827}  # #D9EAD3
RAG_RED     = {"red": 0.957, "green": 0.800, "blue": 0.800}
RAG_AMBER   = {"red": 0.988, "green": 0.910, "blue": 0.698}
RAG_GREEN   = {"red": 0.718, "green": 0.882, "blue": 0.804}

WHITE       = {"red": 1.0, "green": 1.0, "blue": 1.0}

# ── FAMILY DISPLAY NAMES ──────────────────────────────────────────────────────
# Maps internal canonical names → template display names for the sheet
FAMILY_DISPLAY = {
    "Technical":            "Technical",
    "User Experience":      "UX",
    "Tools & Configuration":"Tools",
    "On-Site SEO":          "On site",
    "Off-Site":             "Off site",
    "GEO / AI Visibility":  "GEO",
}

# Phase order for sorting (uses internal canonical names)
PHASES_INTERNAL = [
    "Technical", "User Experience", "Tools & Configuration",
    "On-Site SEO", "Off-Site", "GEO / AI Visibility",
]

# ── SHEET COLUMN SPEC (19 columns A–S — template layout) ─────────────────────
# (header_label, json_key)  json_key=None → always write empty string
SHEET_COLUMNS = [
    ("",                      None),             # A — blank spacer
    ("Status",                "status"),         # B
    ("Family",                "family_display"),  # C — mapped via FAMILY_DISPLAY
    ("Category",              "category"),        # D
    ("Sub-Category",          "sub_category"),    # E
    ("Analyzed Element",      "element"),         # F
    ("Description",           "description"),     # G
    ("Score",                 "score"),            # H — text rating
    ("Weight/Importance",     "weight"),           # I — numeric
    ("Importance Tier",       "tier"),             # J — label
    ("Priority Score",        "priority_score"),  # K — numeric
    ("Score Explanation",     "explanation"),      # L
    ("Priority",              None),               # M — left blank; user fills via dropdown
    ("Who's in charge?",      None),               # N — left blank; user fills via dropdown
    ("Data Analyzed",         "data_analyzed"),    # O — now included
    ("How to correct?",       "how_to"),           # P
    ("Comments",              "comments"),         # Q
    ("Sources",               "sources"),          # R
    ("Comments for Claude",   None),               # S — user-filled post-delivery
]

# Schema tab columns (unchanged from generate_workbook.py)
SCHEMA_COLUMNS = [
    "Page Type", "Schema Markup Type", "Implementation Status",
    "Current Schema Markup", "Recommended Schema Markup",
    "Recommendations", "Sources",
]

# ── HELPERS ───────────────────────────────────────────────────────────────────
def rag_color(pct):
    if pct < 50:  return RAG_RED
    if pct < 75:  return RAG_AMBER
    return RAG_GREEN


def row_values(r):
    """Map JSON row keys to 19-column template order (A=blank, B-R=data, S=empty)."""
    display_family = FAMILY_DISPLAY.get(r.get("family", ""), r.get("family", ""))
    vals = []
    for _, key in SHEET_COLUMNS:
        if key is None:
            vals.append("")
        elif key == "family_display":
            vals.append(display_family)
        else:
            vals.append(r.get(key, ""))
    return vals


def load_config():
    if not os.path.isfile(CONFIG_PATH):
        sys.exit(
            f"ERROR: audit-session-config.json not found at {CONFIG_PATH}\n"
            "Run python3 scripts/init_session.py first."
        )
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


# ── SHEETS API HELPERS ────────────────────────────────────────────────────────
def color_cell_request(sheet_id, row, col, bg_color, text_color=None, bold=False, font_size=None):
    """Build a repeatCell batchUpdate request for a single cell."""
    fmt = {"backgroundColor": bg_color}
    if text_color or bold or font_size:
        fmt["textFormat"] = {}
        if text_color:
            fmt["textFormat"]["foregroundColor"] = text_color
        if bold:
            fmt["textFormat"]["bold"] = bold
        if font_size:
            fmt["textFormat"]["fontSize"] = font_size
    return {
        "repeatCell": {
            "range": {
                "sheetId": sheet_id,
                "startRowIndex": row,
                "endRowIndex": row + 1,
                "startColumnIndex": col,
                "endColumnIndex": col + 1,
            },
            "cell": {"userEnteredFormat": fmt},
            "fields": "userEnteredFormat(backgroundColor,textFormat)",
        }
    }


def color_row_request(sheet_id, row, n_cols, bg_color, text_color=None, bold=False, font_size=None):
    """Build a repeatCell batchUpdate request for an entire row."""
    fmt = {"backgroundColor": bg_color}
    if text_color or bold or font_size:
        fmt["textFormat"] = {}
        if text_color:
            fmt["textFormat"]["foregroundColor"] = text_color
        if bold:
            fmt["textFormat"]["bold"] = bold
        if font_size:
            fmt["textFormat"]["fontSize"] = font_size
    return {
        "repeatCell": {
            "range": {
                "sheetId": sheet_id,
                "startRowIndex": row,
                "endRowIndex": row + 1,
                "startColumnIndex": 0,
                "endColumnIndex": n_cols,
            },
            "cell": {"userEnteredFormat": fmt},
            "fields": "userEnteredFormat(backgroundColor,textFormat)",
        }
    }


def freeze_rows_request(sheet_id, n_rows=1):
    return {
        "updateSheetProperties": {
            "properties": {
                "sheetId": sheet_id,
                "gridProperties": {"frozenRowCount": n_rows},
            },
            "fields": "gridProperties.frozenRowCount",
        }
    }


def autofilter_request(sheet_id, n_rows, n_cols):
    return {
        "setBasicFilter": {
            "filter": {
                "range": {
                    "sheetId": sheet_id,
                    "startRowIndex": 0,
                    "endRowIndex": n_rows,
                    "startColumnIndex": 0,
                    "endColumnIndex": n_cols,
                }
            }
        }
    }


def wrap_columns_request(sheet_id, col_indices, n_rows):
    """Enable text wrap on specific columns."""
    requests = []
    for col in col_indices:
        requests.append({
            "repeatCell": {
                "range": {
                    "sheetId": sheet_id,
                    "startRowIndex": 1,
                    "endRowIndex": n_rows,
                    "startColumnIndex": col,
                    "endColumnIndex": col + 1,
                },
                "cell": {
                    "userEnteredFormat": {
                        "wrapStrategy": "WRAP",
                        "verticalAlignment": "TOP",
                    }
                },
                "fields": "userEnteredFormat(wrapStrategy,verticalAlignment)",
            }
        })
    return requests


def set_column_widths_request(sheet_id, col_widths_px):
    """Set column widths in pixels. col_widths_px: list of (col_index, width_px)."""
    requests = []
    for col_idx, width in col_widths_px:
        requests.append({
            "updateDimensionProperties": {
                "range": {
                    "sheetId": sheet_id,
                    "dimension": "COLUMNS",
                    "startIndex": col_idx,
                    "endIndex": col_idx + 1,
                },
                "properties": {"pixelSize": width},
                "fields": "pixelSize",
            }
        })
    return requests


# ── TAB BUILDERS ──────────────────────────────────────────────────────────────
def build_performances_summary(gc, spreadsheet, rows, phase_scores, exec_summary,
                                client_name, audit_date, sheets_svc):
    """Tab 1 — Performances summary."""
    ws = spreadsheet.add_worksheet(title="Performances summary", rows=80, cols=20)
    sheet_id = ws.id

    # Title block
    ws.update("A1", [[f"{client_name} — SEO & GEO Audit — {audit_date}"]])
    ws.update("A2", [["Performances summary"]])

    # Phase scorecard header
    ws.update("A4", [["Phase"]])
    ws.update("B4", [["Score"]])
    ws.update("C4", [["Status"]])

    phase_display_map = {v: k for k, v in FAMILY_DISPLAY.items()}
    scorecard_rows = []
    for phase_internal in PHASES_INTERNAL:
        display = FAMILY_DISPLAY.get(phase_internal, phase_internal)
        pct = phase_scores.get(phase_internal, 0)
        status = "To optimize" if pct < 50 else ("May be optimised" if pct < 75 else "Optimised")
        scorecard_rows.append([display, f"{pct}%", status])

    overall = phase_scores.get("Overall", 0)
    scorecard_rows.append(["Overall", f"{overall}%",
                           "To optimize" if overall < 50 else
                           ("May be optimised" if overall < 75 else "Optimised")])
    geo_score = phase_scores.get("GEO Score", 0)
    scorecard_rows.append(["GEO Score (normalised)", f"{geo_score}%",
                           "To optimize" if geo_score < 50 else
                           ("May be optimised" if geo_score < 75 else "Optimised")])
    ws.update("A5", scorecard_rows)

    # HIGH priority items
    high_start = 5 + len(scorecard_rows) + 2
    ws.update(f"A{high_start}", [["HIGH PRIORITY ITEMS"]])
    hp_rows = []
    for phase_internal in PHASES_INTERNAL:
        display = FAMILY_DISPLAY.get(phase_internal, phase_internal)
        high = sorted(
            [r for r in rows if r["family"] == phase_internal and r["priority"] == "HIGH"],
            key=lambda r: r["priority_score"] if isinstance(r.get("priority_score"), (int, float)) else 999
        )
        for item in high:
            ps = item.get("priority_score", "")
            hp_rows.append([display, item["element"], f"Priority Score: {ps}" if ps != "" else ""])
    if hp_rows:
        ws.update(f"A{high_start + 1}", hp_rows)

    # Score distribution
    dist_start = high_start + len(hp_rows) + 3
    dist_headers = ["Phase", "Not Present", "Weak", "Medium",
                    "High", "Excellent", "Not Applicable", "Data Missing"]
    ws.update(f"A{dist_start}", [dist_headers])
    score_labels = ["Not Present", "Weak", "Medium", "High",
                    "Excellent", "Not Applicable", "Data Missing"]
    dist_rows = []
    for phase_internal in PHASES_INTERNAL + ["All"]:
        display = FAMILY_DISPLAY.get(phase_internal, phase_internal) if phase_internal != "All" else "All Phases"
        phase_rows = [r for r in rows if r["family"] == phase_internal] if phase_internal != "All" else rows
        dist_rows.append([display] + [sum(1 for r in phase_rows if r["score"] == lbl)
                                      for lbl in score_labels])
    ws.update(f"A{dist_start + 1}", dist_rows)

    # Executive summary block
    exec_start = dist_start + len(dist_rows) + 3
    ws.update(f"A{exec_start}", [["EXECUTIVE SUMMARY"]])
    ws.update(f"A{exec_start + 1}", [[exec_summary]])

    # RAG key
    ws.update("E5", [
        ["Key"],
        ["To optimize (<50%)"],
        ["May be optimised (<75%)"],
        ["Optimised (>75%)"],
    ])

    # Formatting via batchUpdate
    requests = [
        color_row_request(sheet_id, 0, 5, HEADER_RED, WHITE, bold=True, font_size=12),
        color_row_request(sheet_id, 1, 5, HEADER_RED, WHITE, bold=True, font_size=11),
        color_row_request(sheet_id, 3, 5, HEADER_RED, WHITE, bold=True, font_size=10),
        color_row_request(sheet_id, high_start - 1, 5, PRIORITY_FILLS["HIGH"], bold=True),
        color_row_request(sheet_id, dist_start - 1, 8, PHASE_GREEN, bold=True),
        color_row_request(sheet_id, exec_start - 1, 5, PHASE_GREEN, bold=True),
        # RAG key colours
        color_cell_request(sheet_id, 5, 4, RAG_RED),
        color_cell_request(sheet_id, 6, 4, RAG_AMBER),
        color_cell_request(sheet_id, 7, 4, RAG_GREEN),
    ]

    # Scorecard row colours by health score
    for i, phase_internal in enumerate(PHASES_INTERNAL + ["Overall"]):
        pct = overall if phase_internal == "Overall" else phase_scores.get(phase_internal, 0)
        requests.append(color_cell_request(sheet_id, 4 + i, 1, rag_color(pct)))

    sheets_svc.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet.id,
        body={"requests": requests},
    ).execute()

    return ws


def build_detailed_audit(gc, spreadsheet, rows, sheets_svc, tab_name="Detailed Technical Audit"):
    """Tab 2 — Detailed Technical Audit (19-column template layout, A–S).

    tab_name: sheet tab to write into. When SHEET_ID is set (write-to-existing
    mode), this is the user-supplied TAB_NAME. The tab is created if absent.
    """
    # Reuse existing tab if present, otherwise create
    try:
        ws = spreadsheet.worksheet(tab_name)
        ws.clear()
    except Exception:
        ws = spreadsheet.add_worksheet(title=tab_name, rows=len(rows) + 10, cols=19)
    sheet_id = ws.id

    n_cols = len(SHEET_COLUMNS)   # 19
    headers = [col[0] for col in SHEET_COLUMNS]

    # Write header row
    ws.update("A1", [headers])

    # Sort: phase order → category → sub-category
    sorted_rows = sorted(rows, key=lambda r: (
        PHASES_INTERNAL.index(r["family"]) if r["family"] in PHASES_INTERNAL else 99,
        r.get("category") or "",
        r.get("sub_category") or "",
    ))

    data = [row_values(r) for r in sorted_rows]
    if data:
        ws.update("A2", data)

    # Batch formatting
    requests = [
        color_row_request(sheet_id, 0, n_cols, HEADER_RED, WHITE, bold=True, font_size=10),
        freeze_rows_request(sheet_id, 1),
        autofilter_request(sheet_id, len(data) + 1, n_cols),
    ]

    # Priority column (M, index 12) — conditional formatting so colours apply
    # automatically when the user selects a value from the dropdown.
    PRIORITY_CF = [
        ("High",                         {"red": 0.957, "green": 0.800, "blue": 0.800}),
        ("Medium",                       {"red": 0.988, "green": 0.910, "blue": 0.698}),
        ("Low",                          {"red": 0.718, "green": 0.882, "blue": 0.804}),
        ("Monitor",                      {"red": 0.749, "green": 0.749, "blue": 0.749}),
        ("Manual Verification Required", {"red": 0.788, "green": 0.855, "blue": 0.973}),
    ]
    for idx, (label, bg) in enumerate(PRIORITY_CF):
        requests.append({
            "addConditionalFormatRule": {
                "rule": {
                    "ranges": [{
                        "sheetId": sheet_id,
                        "startRowIndex": 1,
                        "endRowIndex": len(data) + 10,
                        "startColumnIndex": 12,
                        "endColumnIndex": 13,
                    }],
                    "booleanRule": {
                        "condition": {
                            "type": "TEXT_EQ",
                            "values": [{"userEnteredValue": label}],
                        },
                        "format": {
                            "backgroundColor": bg,
                            "textFormat": {"bold": True},
                        },
                    },
                },
                "index": idx,
            }
        })

    # Priority dropdown (M, index 12)
    requests.append({
        "setDataValidation": {
            "range": {
                "sheetId": sheet_id,
                "startRowIndex": 1,
                "endRowIndex": len(data) + 10,
                "startColumnIndex": 12,
                "endColumnIndex": 13,
            },
            "rule": {
                "condition": {
                    "type": "ONE_OF_LIST",
                    "values": [{"userEnteredValue": v} for v in [
                        "High", "Medium", "Low", "Monitor",
                        "Manual Verification Required",
                    ]],
                },
                "showCustomUi": True,
                "strict": False,
            },
        }
    })

    # Who's in charge? dropdown (N, index 13)
    requests.append({
        "setDataValidation": {
            "range": {
                "sheetId": sheet_id,
                "startRowIndex": 1,
                "endRowIndex": len(data) + 10,
                "startColumnIndex": 13,
                "endColumnIndex": 14,
            },
            "rule": {
                "condition": {
                    "type": "ONE_OF_LIST",
                    "values": [
                        {"userEnteredValue": "Digitad"},
                        {"userEnteredValue": "Technical Team"},
                    ],
                },
                "showCustomUi": True,
                "strict": False,
            },
        }
    })

    # Text wrap on: G(6)=Description, L(11)=Score Explanation, O(14)=Data Analyzed,
    # P(15)=How to correct?, Q(16)=Comments, R(17)=Sources, S(18)=Comments for Claude
    wrap_cols = [6, 11, 14, 15, 16, 17, 18]
    requests.extend(wrap_columns_request(sheet_id, wrap_cols, len(data) + 2))

    # Status column (B, index 1) — dropdown validation so client can update via list
    STATUS_VALUES = [
        "To do", "Issue Found", "Passing", "Opportunity",
        "Data Missing", "Not Applicable", "Manual Verification Required",
    ]
    requests.append({
        "setDataValidation": {
            "range": {
                "sheetId": sheet_id,
                "startRowIndex": 1,
                "endRowIndex": len(data) + 10,
                "startColumnIndex": 1,
                "endColumnIndex": 2,
            },
            "rule": {
                "condition": {
                    "type": "ONE_OF_LIST",
                    "values": [{"userEnteredValue": v} for v in STATUS_VALUES],
                },
                "showCustomUi": True,
                "strict": False,
            },
        }
    })

    # Column widths (pixels) — A(0) through S(18)
    col_widths = [
        (0,  30),   # A — blank spacer
        (1,  100),  # B — Status
        (2,  90),   # C — Family
        (3,  140),  # D — Category
        (4,  160),  # E — Sub-Category
        (5,  200),  # F — Analyzed Element
        (6,  300),  # G — Description
        (7,  90),   # H — Score (text)
        (8,  80),   # I — Weight/Importance (numeric)
        (9,  110),  # J — Importance Tier
        (10, 80),   # K — Priority Score (numeric)
        (11, 380),  # L — Score Explanation
        (12, 90),   # M — Priority
        (13, 130),  # N — Who's in charge?
        (14, 280),  # O — Data Analyzed
        (15, 380),  # P — How to correct?
        (16, 300),  # Q — Comments
        (17, 250),  # R — Sources
        (18, 300),  # S — Comments for Claude
    ]
    requests.extend(set_column_widths_request(sheet_id, col_widths))

    sheets_svc.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet.id,
        body={"requests": requests},
    ).execute()

    return ws


def build_schema_analysis(gc, spreadsheet, schema_csv, sheets_svc):
    """Tab 3 — Schema Analysis (from schema CSV)."""
    ws = spreadsheet.add_worksheet(title="Schema Analysis", rows=200, cols=len(SCHEMA_COLUMNS))
    sheet_id = ws.id

    ws.update("A1", [SCHEMA_COLUMNS])

    rows = []
    if os.path.isfile(schema_csv):
        with open(schema_csv, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                rows.append([row.get(col, "") for col in SCHEMA_COLUMNS])
    if rows:
        ws.update("A2", rows)

    requests = [
        color_row_request(sheet_id, 0, len(SCHEMA_COLUMNS), HEADER_RED, WHITE, bold=True, font_size=10),
        freeze_rows_request(sheet_id, 1),
        autofilter_request(sheet_id, len(rows) + 1, len(SCHEMA_COLUMNS)),
    ]
    requests.extend(wrap_columns_request(sheet_id, [3, 4, 5], len(rows) + 2))
    col_widths = [(i, 200) for i in range(len(SCHEMA_COLUMNS))]
    col_widths[3] = (3, 400)
    col_widths[4] = (4, 400)
    col_widths[5] = (5, 350)
    requests.extend(set_column_widths_request(sheet_id, col_widths))

    sheets_svc.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet.id,
        body={"requests": requests},
    ).execute()

    return ws


def build_sources(gc, spreadsheet, rows, sheets_svc):
    """Tab 4 — Sources (unique source documents from audit rows)."""
    ws = spreadsheet.add_worksheet(title="Sources", rows=200, cols=3)
    sheet_id = ws.id

    headers = ["Source", "Phase", "Element"]
    ws.update("A1", [headers])

    # Collect unique non-empty sources with their phase and element context
    seen = {}
    for r in rows:
        src = r.get("sources", "").strip()
        if src:
            # A Sources cell may contain multiple entries separated by newlines or semicolons
            for entry in src.replace("\n", ";").split(";"):
                entry = entry.strip()
                if entry and entry not in seen:
                    seen[entry] = {
                        "phase": FAMILY_DISPLAY.get(r.get("family", ""), r.get("family", "")),
                        "element": r.get("element", ""),
                    }

    source_rows = [[src, info["phase"], info["element"]] for src, info in seen.items()]
    if source_rows:
        ws.update("A2", source_rows)

    requests = [
        color_row_request(sheet_id, 0, 3, HEADER_RED, WHITE, bold=True, font_size=10),
        freeze_rows_request(sheet_id, 1),
    ]
    requests.extend(wrap_columns_request(sheet_id, [0], len(source_rows) + 2))
    requests.extend(set_column_widths_request(sheet_id, [(0, 400), (1, 100), (2, 280)]))

    sheets_svc.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet.id,
        body={"requests": requests},
    ).execute()

    return ws


def build_glossary(gc, spreadsheet, rows, sheets_svc):
    """Tab 5 — Glossary (Analyzed Element + Description for every row)."""
    ws = spreadsheet.add_worksheet(title="Glossary", rows=len(rows) + 5, cols=3)
    sheet_id = ws.id

    headers = ["Analyzed Element", "Phase", "Description"]
    ws.update("A1", [headers])

    # Deduplicate by element name, preserve phase context
    seen_elements = {}
    for r in rows:
        el = r.get("element", "").strip()
        if el and el not in seen_elements:
            seen_elements[el] = {
                "phase": FAMILY_DISPLAY.get(r.get("family", ""), r.get("family", "")),
                "description": r.get("description", ""),
            }

    glossary_rows = [
        [el, info["phase"], info["description"]]
        for el, info in seen_elements.items()
    ]
    if glossary_rows:
        ws.update("A2", glossary_rows)

    requests = [
        color_row_request(sheet_id, 0, 3, HEADER_RED, WHITE, bold=True, font_size=10),
        freeze_rows_request(sheet_id, 1),
    ]
    requests.extend(wrap_columns_request(sheet_id, [0, 2], len(glossary_rows) + 2))
    requests.extend(set_column_widths_request(sheet_id, [(0, 250), (1, 100), (2, 500)]))

    sheets_svc.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet.id,
        body={"requests": requests},
    ).execute()

    return ws


# ── MAIN ──────────────────────────────────────────────────────────────────────
def main():
    if not AUDIT_DIR:
        sys.exit("ERROR: Set AUDIT_DIR at the top of generate_gsheet.py before running.")

    # Load audit data
    json_path = os.path.join(AUDIT_DIR, "Workbook", "workbook_data.json")
    if not os.path.isfile(json_path):
        sys.exit(f"ERROR: workbook_data.json not found at {json_path}\nRun extract_data.py first.")

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    client_name  = data["client"]
    audit_date   = data["audit_date"]
    rows         = data["rows"]
    phase_scores = data["phase_scores"]
    exec_summary = data.get("exec_summary", "")

    # Load session config for Drive folder ID
    config = load_config()
    gdrive_main_dir_id = config.get("gdrive_main_dir_id", "").strip()

    # Schema CSV path
    schema_csv = os.path.join(
        AUDIT_DIR, "Outputs", "CSV",
        f"{client_name} - Schema Markup Corrections - {audit_date}.csv"
    )

    # Authenticate
    print(f"Authenticating with Google APIs...")
    print(f"  .env loaded from: {api_clients.get_env_path()}")
    gc          = api_clients.get_google_sheets_client()
    drive_svc   = api_clients.get_google_drive_client()
    sheets_svc  = api_clients.get_google_sheets_service()

    if SHEET_ID:
        # ── WRITE-TO-EXISTING mode ──────────────────────────────────────────
        print(f"Opening existing Google Sheet: {SHEET_ID}")
        print(f"  Target tab: {TAB_NAME}")
        spreadsheet = gc.open_by_key(SHEET_ID)
        audit_tab_name = TAB_NAME
    else:
        # ── CREATE-NEW mode ─────────────────────────────────────────────────
        if not gdrive_main_dir_id:
            sys.exit(
                "ERROR: gdrive_main_dir_id is empty in audit-session-config.json\n"
                "Run init_session.py and confirm the Google Drive folder, "
                "or set SHEET_ID to write to an existing spreadsheet."
            )
        sheet_title = f"{client_name} - SEO GEO Audit - {audit_date}"
        print(f"Creating Google Sheet: {sheet_title}")
        spreadsheet = gc.create(sheet_title)

        # Move to correct Drive folder
        drive_svc.files().update(
            fileId=spreadsheet.id,
            addParents=gdrive_main_dir_id,
            removeParents="root",
            fields="id, parents",
        ).execute()
        print(f"  Moved to Drive folder: {gdrive_main_dir_id}")

        # Delete the default Sheet1
        default_sheet_id = spreadsheet.sheet1.id
        sheets_svc.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet.id,
            body={"requests": [{"deleteSheet": {"sheetId": default_sheet_id}}]},
        ).execute()
        audit_tab_name = "Detailed Technical Audit"

    # Build all tabs
    print("Building tabs...")

    print("  Tab 1: Performances summary")
    build_performances_summary(gc, spreadsheet, rows, phase_scores, exec_summary,
                               client_name, audit_date, sheets_svc)
    time.sleep(1)  # Respect Sheets API rate limits between writes

    print(f"  Tab 2: {audit_tab_name}")
    build_detailed_audit(gc, spreadsheet, rows, sheets_svc, tab_name=audit_tab_name)
    time.sleep(1)

    if INCLUDE_SCHEMA and os.path.isfile(schema_csv):
        print("  Tab 3: Schema Analysis")
        build_schema_analysis(gc, spreadsheet, schema_csv, sheets_svc)
        time.sleep(1)
    else:
        print("  Tab 3: Schema Analysis — placeholder (set INCLUDE_SCHEMA=True to populate)")
        ws = spreadsheet.add_worksheet(title="Schema Analysis", rows=5, cols=len(SCHEMA_COLUMNS))
        ws.update("A1", [SCHEMA_COLUMNS])

    print("  Tab 4: Sources")
    build_sources(gc, spreadsheet, rows, sheets_svc)
    time.sleep(1)

    print("  Tab 5: Glossary")
    build_glossary(gc, spreadsheet, rows, sheets_svc)

    # Sheet URL
    sheet_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet.id}"
    mode_label = "written to existing" if SHEET_ID else "created"
    print(f"\nGoogle Sheet {mode_label}: {sheet_url}")

    # Write URL to local reference file
    url_file = os.path.join(AUDIT_DIR, "Workbook", "workbook_url.txt")
    os.makedirs(os.path.dirname(url_file), exist_ok=True)
    with open(url_file, "w", encoding="utf-8") as f:
        f.write(sheet_url + "\n")
    print(f"URL saved to: {url_file}")

    # Summary
    high_count   = sum(1 for r in rows if r["priority"] == "HIGH")
    medium_count = sum(1 for r in rows if r["priority"] == "MEDIUM")
    print(f"\nSummary:")
    print(f"  Total rows:    {len(rows)}")
    print(f"  HIGH priority: {high_count}")
    print(f"  MEDIUM:        {medium_count}")
    print(f"  Overall score: {phase_scores.get('Overall', 0)}%")
    if INCLUDE_SCHEMA:
        print(f"  Schema tab:    from {os.path.basename(schema_csv)}")

    return sheet_url


if __name__ == "__main__":
    main()
