"""
validate_phase.py  —  seo-geo-technical-audit-v9
=================================================
Validates a single phase .md scoring file against the v9 spec before the
workbook pipeline runs. Run after each phase is written (L1 gate) and again
across all 6 files before extract_data.py (L2 gate).

USAGE
-----
  python3 validate_phase.py <path_to_phase.md> [expected_row_count]

  expected_row_count is optional. Phase counts: 26 / 14 / 11 / 26 / 11 / 26
  If omitted, row count is reported but not validated against a target.

EXIT CODES
----------
  0 — all checks passed
  1 — one or more checks failed (details printed to stdout)

EXAMPLE
-------
  python3 validate_phase.py "Outputs/Brand - Phase 1 Technical - March 2026.md" 26
"""

import re
import sys
import os

# ── SPEC CONSTANTS ─────────────────────────────────────────────────────────────
CANONICAL_HEADER = (
    "| Status | Family | Category | Sub-Category | Analyzed Element | Description "
    "| Score | Weight/Importance (Numeric) | Importance Tier | Priority Score "
    "| Priority | Who's in charge? | Score Explanation | Data Analyzed "
    "| How to correct? | Comments | Sources |"
)
EXPECTED_COL_COUNT = 17

ALLOWED_STATUSES = {
    "Issue Found", "Passing", "Opportunity",
    "Data Missing", "Not Applicable", "Manual Verification Required",
}

# Single-letter score codes that should never appear as the full Score value
DISALLOWED_SCORE_CODES = {"NP", "W", "M", "H", "E", "NA"}

# Element code pattern — e.g. T01, G12, U04, O26, F11, C09
ELEMENT_CODE_RE = re.compile(r'\b[TUGCOFG]\d{2}\b')

KNOWN_STATUS_PREFIXES = tuple(f"| {s} |" for s in ALLOWED_STATUSES)


def parse_file(filepath):
    """Return (headers, data_rows) where each data_row is a list of cell strings."""
    headers = None
    data_rows = []
    raw_data_lines = []

    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line.startswith("|"):
                continue
            # Skip separator rows
            if re.match(r"^\|[\s\-|]+\|$", line):
                continue
            cells = [c.strip() for c in line.split("|")][1:-1]
            if headers is None:
                if "Status" in cells and "Analyzed Element" in cells:
                    headers = cells
                continue
            if any(line.startswith(p) for p in KNOWN_STATUS_PREFIXES):
                data_rows.append(cells)
                raw_data_lines.append(line)

    return headers, data_rows, raw_data_lines


def validate(filepath, expected_rows=None):
    failures = []
    warnings = []

    # ── FILE EXISTS ────────────────────────────────────────────────────────────
    if not os.path.isfile(filepath):
        print(f"FAIL  File not found: {filepath}")
        sys.exit(1)

    headers, data_rows, raw_lines = parse_file(filepath)
    filename = os.path.basename(filepath)

    # ── HEADER PRESENT ─────────────────────────────────────────────────────────
    if headers is None:
        failures.append("No valid header row found — 'Status' and 'Analyzed Element' must both be present")
        report(filename, failures, warnings)
        return

    # ── COLUMN COUNT ───────────────────────────────────────────────────────────
    if len(headers) != EXPECTED_COL_COUNT:
        failures.append(f"Column count: expected {EXPECTED_COL_COUNT}, found {len(headers)}")

    # ── CANONICAL HEADER MATCH ─────────────────────────────────────────────────
    # Reconstruct header string from parsed cells to compare against canonical
    reconstructed = "| " + " | ".join(headers) + " |"
    if reconstructed != CANONICAL_HEADER:
        failures.append(f"Header mismatch.\n  Expected : {CANONICAL_HEADER}\n  Found    : {reconstructed}")

    # ── ROW COUNT ─────────────────────────────────────────────────────────────
    row_count = len(data_rows)
    if expected_rows is not None:
        if row_count != expected_rows:
            failures.append(f"Row count: expected {expected_rows}, found {row_count}")
        else:
            print(f"  Row count: {row_count} / {expected_rows} — OK")
    else:
        print(f"  Row count: {row_count} (no target supplied — not validated)")

    # ── PER-ROW CHECKS ─────────────────────────────────────────────────────────
    for i, (row, raw) in enumerate(zip(data_rows, raw_lines), 1):
        row_id = f"Row {i}"

        # Pipe in cell content: more cells than headers
        if len(row) > len(headers):
            failures.append(f"{row_id}: pipe character in cell content detected — {raw[:100]}")
            row = row[:len(headers)]
        elif len(row) < len(headers):
            row += [""] * (len(headers) - len(row))

        cell = dict(zip(headers, row))

        # Status value
        status = cell.get("Status", "").strip()
        if status not in ALLOWED_STATUSES:
            failures.append(f"{row_id}: invalid Status value '{status}'")

        # Score shorthand codes
        score = cell.get("Score", "").strip()
        if score in DISALLOWED_SCORE_CODES:
            failures.append(f"{row_id}: Score uses shorthand code '{score}' — write full name")

        # Element codes anywhere in the row
        for col, value in cell.items():
            match = ELEMENT_CODE_RE.search(value)
            if match:
                failures.append(f"{row_id} [{col}]: element code '{match.group()}' found — remove from output")

        # Emoji (basic unicode block check)
        full_row_text = " ".join(row)
        if re.search(r"[\U0001F300-\U0001FAFF]", full_row_text):
            failures.append(f"{row_id}: emoji character detected")

    report(filename, failures, warnings)


def report(filename, failures, warnings):
    print(f"\n{'='*60}")
    print(f"  {filename}")
    print(f"{'='*60}")
    if not failures and not warnings:
        print("  PASS — all checks passed")
    else:
        for w in warnings:
            print(f"  WARN  {w}")
        for f in failures:
            print(f"  FAIL  {f}")
        print(f"\n  Result: {len(failures)} failure(s), {len(warnings)} warning(s)")
    print()
    if failures:
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 validate_phase.py <phase_file.md> [expected_row_count]")
        sys.exit(1)

    path = sys.argv[1]
    target = int(sys.argv[2]) if len(sys.argv) >= 3 else None
    validate(path, target)
