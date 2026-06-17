"""
extract_data.py  —  seo-geo-technical-audit-v14
================================================
Parses all 6 phase .md audit files, applies workbook transformations,
and writes workbook_data.json for use by generate_gsheet.py.

HOW TO USE FOR A NEW CLIENT
-----------------------------
1. Set CLIENT_NAME, AUDIT_DATE, AUDIT_DIR below.
2. Set PHASE_SLUGS to match your client's phase file naming.
   Canonical slug names (recommended — match these when naming phase .md files):
     "Phase 1 Technical"
     "Phase 2 User Experience"
     "Phase 3 Tools and Configuration"
     "Phase 4 On-Site SEO"
     "Phase 5 Off-Site"
     "Phase 6 GEO"
3. Set EXEC_SUMMARY text from the Overall Assessment section of the Executive Summary .md.
4. Leave PHASE_SCORES as {} to calculate dynamically, or hardcode from the Executive Summary.
5. Run: python3 extract_data.py
6. Then run: python3 generate_gsheet.py

FOLDER STRUCTURE (created at Phase 0)
--------------------------------------
  {AUDIT_DIR}/Outputs/          — phase .md files (what this script reads)
  {AUDIT_DIR}/Outputs/CSV/      — tertiary CSV files
  {AUDIT_DIR}/Workbook/         — workbook_data.json (written here) + Google Sheet URL

PIPELINE NOTES
--------------
- Header-based parsing — works regardless of column order.
- Family names are normalised to canonical workbook labels during extraction.
- Element codes (T01, G09 etc.) are stripped from the Analyzed Element field.
- Who's in charge? is assigned from TECHNICAL_TEAM_ELEMENTS, overriding phase file values.
- Phase scores are calculated dynamically if PHASE_SCORES is left as {}.
- Run extract_data.py once per audit (or when phase files are updated).
- Run generate_gsheet.py to create the Google Sheet from the JSON.
"""

import json
import re
import os
from collections import defaultdict

# ── CLIENT CONFIGURATION ─────────────────────────────────────────────────────
CLIENT_NAME = ""       # e.g. "YoCrunch"
AUDIT_DATE  = ""       # e.g. "March 2026"
AUDIT_DIR   = ""       # e.g. "/Users/username/claude_code/client_audit"

# Subfolder within AUDIT_DIR containing the phase .md files.
MD_SUBDIR = "Outputs"

# Phase file slugs — the part of each filename between CLIENT_NAME and AUDIT_DATE.
# Update these to match the actual filenames in your Outputs/ folder.
# Canonical names (recommended — use these when naming phase .md files):
PHASE_SLUGS = [
    "Phase 1 Technical",
    "Phase 2 User Experience",
    "Phase 3 Tools and Configuration",
    "Phase 4 On-Site SEO",
    "Phase 5 Off-Site",
    "Phase 6 GEO",
]

# Leave as {} to calculate phase scores dynamically from scored elements.
# Formula: average Priority Score for scored rows / 50 × 100 (higher = healthier).
# Override with explicit values from the Executive Summary if preferred.
PHASE_SCORES = {}

# Executive summary text for the Overview tab.
# Copy the Overall Site Health Assessment section from the Executive Summary .md.
# WARNING: if left blank, the Performances Summary tab will have no executive summary text.
EXEC_SUMMARY = ""

# ── TECHNICAL TEAM ELEMENTS ───────────────────────────────────────────────────
# Elements whose "Who's in charge?" = "Technical Team".
# All others default to "Digitad".
# Rule: Digitad = SEO/content/strategy work. Technical Team = physical website
# changes (code, plugins, server config, template edits, CSS, CDN, pixels).
# Match is on the cleaned Analyzed Element value (element codes stripped).
TECHNICAL_TEAM_ELEMENTS = {
    # Phase 1 — Technical (physical site / server / code work)
    "Internal 404 Errors — Broken Page Inventory",
    "HTTPS Implementation — Protocol Consistency & Mixed Content",
    "SSL Certificate — Validity, Coverage & Expiry Timeline",
    "WordPress Admin Panel — Default URL Exposure & Authentication",
    "WordPress Core & Plugin — Version Currency",
    "External Links — noopener noreferrer Attribute",
    "Contact Form — reCAPTCHA & Spam Prevention",
    "PageSpeed Insights — Desktop Performance Score & CWV",
    "PageSpeed Insights — Mobile Core Web Vitals Field Data",
    "GTmetrix Performance Report — Grade, Page Weight & Requests",
    "Unused JavaScript — Unused CSS — Minification & Legacy Code",
    "Lazy Loading — Offscreen Image Deferral",
    "CDN Usage — Static Asset Delivery & Server Proximity",
    "W3C HTML Validation — Error Count & Severity",
    "Server Technology — Hosting Model, Response Time & DNS Security",
    "JavaScript Dependency — Critical Content & Navigation Rendering",
    "Star Rating & Review System — AggregateRating Schema Eligibility",
    # Phase 2 — UX (template / CSS / plugin implementation)
    "Mobile Rendering — Layout, Navigation & Tap Targets",
    "Crawl Depth — Page Reachability from Homepage",
    "Breadcrumbs — Presence — Schema & Navigational Clarity",
    "Custom 404 Page — Quality & User Retention",
    "Footer Navigation — Link Coverage — Trust Elements",
    "Font Legibility — Body Text Size — Tap Target Dimensions",
    "Social Sharing Buttons — Page-Level Share Functionality",
    "Contact Page — Navigation Prominence — Form & Direct Contact Information",
    "Favicon — Presence — Brand Legibility — Apple Touch Icon",
    "Newsletter — Email Signup — First-Party Audience Building",
    # Phase 3 — Tools & Config (tag/pixel/analytics implementation)
    "Google Analytics 4 — Tracking Completeness — Event Configuration — Data Retention",
    "Google Tag Manager — Container Presence — Tag Firing — Configuration",
    "WHOIS — Registrar — Hosting Provider — IP Neighbourhood — DNSSEC",
    "Remarketing Tags — Google Ads — Meta Pixel — Tag Firing Verification",
    # Phase 4 — On-Site (code / template / asset level changes)
    "Image Format — File Size — Width/Height Attributes",
    "OpenGraph Tags — Twitter Card Tags — og:image Dimensions",
    "Semantic HTML Elements — Article — Section — Nav — Figure Usage",
    # Phase 6 — GEO (code / markup implementation)
    "Semantic HTML Tables",
    "On-Site Customer Reviews and Ratings",
}

# ── FAMILY NORMALISATION ──────────────────────────────────────────────────────
# Maps all known Family label variants to canonical workbook names.
# Handles mixed v6/v7 column orders and client-specific label variations.
FAMILY_NORMALISE = {
    "Technical":              "Technical",
    "Technical SEO":          "Technical",
    "UX":                     "User Experience",
    "User Experience":        "User Experience",
    "Tools":                  "Tools & Configuration",
    "Tools & Config":         "Tools & Configuration",
    "Tools & Configuration":  "Tools & Configuration",
    "On-Site":                "On-Site SEO",
    "On-Page":                "On-Site SEO",
    "On-Site SEO":            "On-Site SEO",
    "Off-Site":               "Off-Site",
    "Off-Site SEO":           "Off-Site",
    "Off-Site / Backlinks":   "Off-Site",
    "GEO":                    "GEO / AI Visibility",
    "GEO / LLM Visibility":   "GEO / AI Visibility",
    "GEO / AI Visibility":    "GEO / AI Visibility",
}

CANONICAL_PHASES = [
    "Technical",
    "User Experience",
    "Tools & Configuration",
    "On-Site SEO",
    "Off-Site",
    "GEO / AI Visibility",
]

# ── VALIDATION CONSTANTS ──────────────────────────────────────────────────────
# Matches the 17-column phase .md spec defined in CLAUDE.md and SKILL.md.
# Phase files and workbook are now aligned — all 17 columns are written in
# every phase .md scoring table and extracted here.
EXPECTED_COLUMNS = {
    'Status', 'Family', 'Category', 'Sub-Category', 'Analyzed Element',
    'Description', 'Score', 'Weight/Importance (Numeric)', 'Importance Tier',
    'Priority Score', 'Priority', "Who's in charge?", 'Score Explanation',
    'Data Analyzed', 'How to correct?', 'Comments', 'Sources',
}
EXPECTED_ROW_COUNT = 122  # 26+14+11+26+11+34 — full 6-phase audit (Phase 6 expanded to 34 elements)

# ── PATHS ─────────────────────────────────────────────────────────────────────
OUTPUTS_DIR = os.path.join(AUDIT_DIR, MD_SUBDIR)
PHASE_FILES = [
    os.path.join(OUTPUTS_DIR, f"{CLIENT_NAME} - {slug} - {AUDIT_DATE}.md")
    for slug in PHASE_SLUGS
]
OUTPUT_JSON = os.path.join(AUDIT_DIR, "Workbook", "workbook_data.json")

# ── TRANSFORMS ────────────────────────────────────────────────────────────────
SCORE_MAP = {
    "Moderate":     "Medium",
    "NA":           "Not Applicable",
    "DATA MISSING": "Data Missing",
    "[DATA MISSING]": "Data Missing",
}

def normalise_score(raw):
    return SCORE_MAP.get(raw.strip(), raw.strip())

def normalise_priority(priority_raw, score):
    p = priority_raw.strip()
    if score == "Data Missing":
        return ""  # Leave blank — DATA MISSING means no source was provided, not a verification gap
    if p in ("NA", "—", ""):
        return ""
    return p

def normalise_priority_score(raw):
    v = raw.strip()
    if v in ("—", "", "DATA MISSING", "–"):
        return ""
    try:
        f = float(v)
        return int(f) if f == int(f) else f
    except ValueError:
        return ""

def strip_element_code(text):
    """Remove leading element codes like 'T01 — ' or 'G09 - ' from Analyzed Element."""
    return re.sub(r'^[A-Za-z]\d{1,2}\s*[—–\-]+\s*', '', text.strip())

def clean_explanation(text):
    """Convert <br> tags to newlines for Excel cell line breaks."""
    text = re.sub(r'<br\s*/?>', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'\n[ \t]+', '\n', text)
    return text.strip()

def split_label(segment):
    """
    If a segment ends with a colon-terminated label (e.g. 'sentence. Priority actions:'),
    split it into (bullet_text, label). Returns (text, label) or (text, None).
    """
    m = re.match(r'(.*\S)\.\s+([A-Z][^.\n]+:)\s*$', segment, re.DOTALL)
    if m:
        return m.group(1) + '.', m.group(2)
    return segment, None

def convert_to_bullets(text):
    """
    Convert 'How to correct?' field text to newline-separated bullet lines for Excel.

    Handles two input formats:
    1. Already bullet-formatted: '• Step one. • Step two.' — splits on bullet markers,
       rejoins with newlines. Prevents double-bullet artefact (• • text).
    2. Numbered prose: '(1) Point one. (2) Point two.' — converts to bullet lines.
    Falls back to a single bullet if no structure is found.

    Note: apply ONLY to the 'How to correct?' field — never to Comments or other fields.
    """
    text = text.strip()
    if not text or text == "—":
        return ""
    # If already bullet-formatted (contains • characters), split and rejoin with newlines
    if '•' in text:
        parts = [p.strip() for p in re.split(r'\s*•\s*', text) if p.strip()]
        return '\n'.join(f"• {p}" for p in parts)
    # Convert numbered prose (1) ... (2) ... to bullet lines
    parts = re.split(r'\s*\(\d+\)\s*', text)
    if len(parts) <= 1:
        return f"• {text}"
    bullets = []
    if parts[0].strip():
        bullets.append(f"• {parts[0].strip()}")
    for segment in parts[1:]:
        s = segment.strip().rstrip('.')
        if not s:
            continue
        bullet_text, label = split_label(s + '.')
        if label:
            bullets.append(f"• {bullet_text}")
            bullets.append(label)
        else:
            bullets.append(f"• {s}.")
    return "\n".join(bullets)

def clean_comments(text):
    """
    Strip element codes (T01, G09 etc.), phase cross-references, and automated-audit language.
    Comments must be plain language source attribution only, self-contained.
    Also strips orphaned bullet characters left by cleaning, and automated-audit language
    ('user confirmed', 'user-provided', 'user said') — replacing with neutral equivalents.
    """
    if text == "—":
        return ""
    text = re.sub(r'\b[TUOCFG]\d{2}\b', '', text)
    text = re.sub(r'Phase \d+\b', '', text)
    text = re.sub(r'Key Decision #\d+\b', '', text)
    # Strip automated-audit language — replace with neutral equivalents
    text = re.sub(r'\bthe user confirmed\b', 'confirmed by site owner', text, flags=re.IGNORECASE)
    text = re.sub(r'\buser confirmed\b', 'confirmed by site owner', text, flags=re.IGNORECASE)
    text = re.sub(r'\buser-provided\b', 'provided', text, flags=re.IGNORECASE)
    text = re.sub(r'\buser said\b', 'the site owner stated', text, flags=re.IGNORECASE)
    text = re.sub(r'\buser provided\b', 'provided', text, flags=re.IGNORECASE)
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\( *\)', '', text)
    text = re.sub(r' ([,.])', r'\1', text)
    text = re.sub(r'— *\.', '—', text)
    # Strip orphaned bullet characters (e.g. '• •' left after code removal)
    text = re.sub(r'•\s*•', '•', text)
    text = re.sub(r'^•\s*$', '', text)
    text = re.sub(r'•\s*([,.])', r'\1', text)
    return text.strip()

# ── PARSER ────────────────────────────────────────────────────────────────────
def parse_row_from_dict(d):
    """
    Build an output row dict from a header-keyed row dict.
    Handles any column order — robust to v6/v7 and mixed-phase files.
    """
    score    = normalise_score(d.get('Score', ''))
    priority = normalise_priority(d.get('Priority', ''), score)
    p_score  = normalise_priority_score(d.get('Priority Score', ''))
    element  = strip_element_code(d.get('Analyzed Element', ''))
    who      = "Technical Team" if element in TECHNICAL_TEAM_ELEMENTS else "Digitad"
    family   = FAMILY_NORMALISE.get(d.get('Family', '').strip(), d.get('Family', '').strip())
    sources  = d.get('Sources', '').strip()
    if sources == '—':
        sources = ''

    return {
        "status":         "To do",  # Always "To do" in workbook — client uses this for remediation tracking
        "family":         family,
        "category":       d.get('Category', ''),
        "sub_category":   d.get('Sub-Category', ''),
        "element":        element,
        "description":    d.get('Description', ''),
        "score":          score,
        "weight":         d.get('Weight/Importance (Numeric)', ''),
        "tier":           d.get('Importance Tier', ''),
        "priority_score": p_score,
        "priority":       priority,
        "who":            who,
        "explanation":    clean_explanation(d.get('Score Explanation', '')),
        "data_analyzed":  d.get('Data Analyzed', ''),
        "how_to":         convert_to_bullets(d.get('How to correct?', '')),
        "comments":       clean_comments(d.get('Comments', '')),
        "sources":        sources,
    }

KNOWN_STATUSES = (
    '| Passing |',
    '| Issue Found |',
    '| Data Missing |',
    '| Not Applicable |',
    '| Opportunity |',
    '| Manual Verification Required |',
    '| To do |',  # legacy — kept for backwards compatibility
)

def parse_file(filepath):
    """
    Parse a phase .md file using header-based column detection.
    Works regardless of column order — handles v6 and v7 phase files,
    and mixed-order files where phases were scored across different sessions.
    """
    rows = []
    headers = None
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line_stripped = line.rstrip('\n')
            if not line_stripped.startswith('|'):
                continue
            # Skip separator rows (|---|---|)
            stripped = line_stripped.replace(' ', '').replace('-', '')
            if re.match(r'^\|+$', stripped):
                continue
            cells = [c.strip() for c in line_stripped.split('|')][1:-1]
            # Detect header row by presence of required columns
            if headers is None:
                if 'Status' in cells and 'Analyzed Element' in cells:
                    headers = cells
                    missing_cols = EXPECTED_COLUMNS - set(headers)
                    if missing_cols:
                        print(f"  WARNING: {os.path.basename(filepath)} — missing expected columns: {sorted(missing_cols)}")
                    if len(headers) != 17:
                        print(f"  WARNING: {os.path.basename(filepath)} — expected 17 columns, found {len(headers)}")
                continue
            # Only process known status rows
            if not any(line_stripped.startswith(s) for s in KNOWN_STATUSES):
                # Warn if this looks like a data row that was skipped (has 10+ cells)
                # but didn't match any known status — likely a whitespace or typo issue
                if len(cells) >= 10:
                    print(f"  WARNING: skipped unrecognised row in {os.path.basename(filepath)}: {line_stripped[:80]}")
                continue
            if len(cells) > len(headers):
                print(f"  WARNING: pipe in cell content detected — {os.path.basename(filepath)}: {line_stripped[:100]}")
                cells = cells[:len(headers)]
            elif len(cells) < len(headers):
                cells += [''] * (len(headers) - len(cells))
            row_dict = dict(zip(headers, cells[:len(headers)]))
            row = parse_row_from_dict(row_dict)
            if row:
                rows.append(row)
    return rows

# ── PHASE SCORE CALCULATION ───────────────────────────────────────────────────
# All phases use the same score scale (Not Present=0, Weak=2.5, Medium=5, High=7.5, Excellent=10)
# and the same weight scale (2.5–10).
# Phase 6 additionally reports a normalised GEO Score using the same Priority Score values.
GEO_PHASE = "GEO / AI Visibility"
GEO_SCORE_LABELS = {
    "not present": 1,
    "weak": 2,
    "medium": 3,
    "high": 4,
    "excellent": 5,
}

def _geo_score_to_num(label):
    """Map Phase 6 text score label to numeric value. Returns None if not mappable."""
    return GEO_SCORE_LABELS.get(str(label).strip().lower())

def calculate_phase_scores(rows):
    """
    Calculate per-phase health scores as a percentage (higher = healthier).
    All phases: avg(Priority Score) / 50 × 100.
    Phase 6 also reports a normalised GEO Score: sum(S×W) / sum(5×W) × 100.
    Excludes DATA MISSING and Not Applicable rows (no numeric priority score).
    """
    phase_ps = defaultdict(list)
    geo_pairs = []  # (score_num, weight_num) for Phase 6 GEO Score calculation

    for r in rows:
        family = r.get('family', '')
        ps = r.get('priority_score')
        if isinstance(ps, (int, float)):
            phase_ps[family].append(ps)
        if family == GEO_PHASE:
            score_num = _geo_score_to_num(r.get('score', ''))
            try:
                weight_num = float(r.get('weight', ''))
            except (ValueError, TypeError):
                weight_num = None
            if score_num is not None and weight_num is not None:
                geo_pairs.append((score_num, weight_num))

    scores = {}
    all_ps = []
    for phase in CANONICAL_PHASES:
        ps_list = phase_ps.get(phase, [])
        if ps_list:
            avg = sum(ps_list) / len(ps_list)
            scores[phase] = round(avg / 50 * 100, 1)
            all_ps.extend(ps_list)
        else:
            scores[phase] = 0.0

    scores['Overall'] = round(sum(all_ps) / len(all_ps) / 50 * 100, 1) if all_ps else 0.0

    # Supplementary normalised GEO Score for Phase 6 (reported separately in output)
    if geo_pairs:
        total_sw = sum(s * w for s, w in geo_pairs)
        max_sw   = sum(5 * w for _, w in geo_pairs)
        scores['GEO Score'] = round(total_sw / max_sw * 100, 1) if max_sw > 0 else 0.0
    else:
        scores['GEO Score'] = 0.0

    return scores

# ── MAIN ──────────────────────────────────────────────────────────────────────
def main():
    all_rows = []
    for path in PHASE_FILES:
        phase_rows = parse_file(path)
        print(f"  {os.path.basename(path)}: {len(phase_rows)} rows")
        all_rows.extend(phase_rows)

    print(f"\nTotal rows extracted: {len(all_rows)}")
    if len(all_rows) != EXPECTED_ROW_COUNT:
        print(f"  WARNING: expected {EXPECTED_ROW_COUNT} rows, got {len(all_rows)}. Check phase files for missing or extra rows.")
    else:
        print(f"  Row count verified: {EXPECTED_ROW_COUNT} rows confirmed.")

    computed_scores = PHASE_SCORES if PHASE_SCORES else calculate_phase_scores(all_rows)
    print(f"Phase scores: {computed_scores}")

    output = {
        "client":        CLIENT_NAME,
        "audit_date":    AUDIT_DATE,
        "rows":          all_rows,
        "phase_scores":  computed_scores,
        "exec_summary":  EXEC_SUMMARY,
    }

    os.makedirs(os.path.dirname(OUTPUT_JSON), exist_ok=True)
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"Written: {OUTPUT_JSON}")
    if not EXEC_SUMMARY:
        print("  WARNING: EXEC_SUMMARY is blank — Performances Summary tab will have no executive summary text.")
    print(f"Next step: python3 generate_gsheet.py")

if __name__ == "__main__":
    main()
