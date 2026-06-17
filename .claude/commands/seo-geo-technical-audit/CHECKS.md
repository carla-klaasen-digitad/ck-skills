---
name: seo-geo-technical-audit / CHECKS.md
load: On demand — load at L0 (pre-launch), L1 (post-phase), L2 (pre-workbook), L3 (post-pipeline), L4 (post-HTML). Trigger rules are in CLAUDE.md.
---

# SEO & GEO Audit — Validation Gates

## CANONICAL COLUMN HEADER — 17 columns (phase .md files only)

`| Status | Family | Category | Sub-Category | Analyzed Element | Description | Score | Weight/Importance (Numeric) | Importance Tier | Priority Score | Priority | Who's in charge? | Score Explanation | Data Analyzed | How to correct? | Comments | Sources |`

Note: The Google Sheet uses 19 columns (A–S) — A is a blank spacer, B–R map to the 17 .md columns with Score Explanation reordered to column L and Data Analyzed included as column O, and S is "Comments for Claude" (user-filled post-delivery). The 17-column header above is the authoritative format for phase .md scoring files only. Do not change it.

---

## L0 — PRE-LAUNCH GATE

Run once before the audit begins. Do not proceed to Phase 0 until all checks pass.

| # | Check | Pass condition |
|---|---|---|
| L0-01 | CLAUDE.md present in skill directory | File exists and is auto-loaded |
| L0-02 | Column header in CLAUDE.md matches canonical above | Zero diff — character-for-character |
| L0-03 | Column position index in CLAUDE.md matches SKILL.md | Zero diff |
| L0-04 | Phase element counts sum to 122 (26+14+11+26+11+34) | Equals 122 |
| L0-05 | extract_data.py passes syntax check | python3 -m py_compile — exit 0 |
| L0-06 | generate_gsheet.py passes syntax check | python3 -m py_compile — exit 0 |
| L0-07 | All files listed in SKILL.md directory table exist on disk | All files present |
| L0-08 | All example files referenced in FORMS.md exist on disk | All present |
| L0-09 | extract_data.py EXPECTED_COLUMNS set matches 17 columns above | Zero diff |
| L0-10 | Rule S1 write-check: Outputs/test-write-check.md and .csv written | Both confirmed written |
| L0-11 | api_clients.py passes syntax check | python3 -m py_compile — exit 0 |
| L0-12 | init_session.py passes syntax check | python3 -m py_compile — exit 0 |
| L0-13 | fetch_data.py passes syntax check | python3 -m py_compile — exit 0 |
| L0-14 | upload_exports.py passes syntax check | python3 -m py_compile — exit 0 |
| L0-15 | ~/.config/digitad/.env exists with required keys | File present — GOOGLE_SERVICE_ACCOUNT_JSON, GDRIVE_MAIN_DIR_ID, GDRIVE_EXPORTS_DIR_ID, GDRIVE_HTML_DIR_ID at minimum |
| L0-16 | audit-session-config.json written and valid JSON | init_session.py has been run — file present in skill root and parseable |

---

## PRE-/COMPACT SAVE — run before every /compact

Write `Outputs/session-state.md` before every /compact. Do not compact without writing this file first.
After /compact, re-read session-state.md before proceeding to the next phase.

```
## Session State — [CLIENT] — [date] — pre-compact [N]
Style choice: [A / B / C — as confirmed at Phase 0]
W-ADJ adjustments: [element — adjustment — reason, or None]
DATA MISSING declarations: [element — missing file, or None]
PROMPT USER answers given: [element — answer summary, or None]
COMP tags accumulated: [tag text, or None]
Production Plan status: [paste current status block]
Phase counts to date: [Phase N: X scored / Y DATA MISSING / Z N/A = total]
```

---

## L1 — POST-PHASE GATE

Run after each phase .md is written to disk, before /compact.
Programmatic check: `python3 [SKILL_DIR]/scripts/validate_phase.py "[AUDIT_DIR]/Outputs/[filename].md" [expected_rows]`
**Path rule**: Always call validate_phase.py using the full absolute path to the skill directory (e.g. `/path/to/skill/scripts/validate_phase.py`). Using the audit directory as the working directory will cause a "file not found" error. This is the most common L1 setup error. The skill directory is wherever `seo-geo-technical-audit` is installed — check the Claude Code commands directory for the exact path.
Manual spot-checks below are a supplement — the script covers columns, statuses, element codes, and pipe detection exhaustively.

| # | Check | Pass condition |
|---|---|---|
| L1-01 | Phase .md file exists in Outputs/ | File present |
| L1-02 | Header column count = 17 | Pipe count in header row = 18 |
| L1-03 | Header string matches canonical above | Character-for-character |
| L1-04 | Row count = phase total (26 / 14 / 11 / 26 / 11 / 34) | Scored + DATA MISSING + N/A = phase total |
| L1-05 | No element codes in any cell | Zero matches on [TUGCOFG][0-9]{2} |
| L1-06 | No emoji in any cell | Zero unicode emoji characters |
| L1-07 | No pipe chars in cell content — spot check 5 rows | Cell count per row does not exceed 17 |
| L1-08 | Score values use full names only | No NP / W / M / H / E / NA shorthand |
| L1-09 | Status values from allowed enum | Issue Found — Passing — Opportunity — Data Missing — Not Applicable — Manual Verification Required |
| L1-10 | All URLs in Sources column are absolute | All begin with https:// |
| L1-11 | Priority Score = Rating Value × Weight — spot check 5 rows | Calculated value matches written value |
| L1-12 | Writing style consistent with Phase 0 confirmed choice | Spot-check Score Explanation on 3 rows |
| L1-13 | Sources column contains no element codes, no "User confirmation," no raw export filenames | Spot-check all Sources cells — must be report names only or blank |
| L1-14 | Comments column contains no element codes (T01, G09, etc.) | Zero matches on [TUOCFG][0-9]{2} in Comments cells |
| L1-15 | No automated-audit language in any cell | Zero instances of "user confirmed," "user-provided," "user said" in any column |
| L1-16 | Conditional outputs triggered this phase confirmed on disk | Any conditional output file referenced in a Score Explanation, How to correct?, Comments, or Sources cell for this phase (e.g. robots-txt-recommendation.txt, http-header-summary.csv) exists on disk in Outputs/ or Outputs/CSV/ before /compact is called |
| L1-17 | Schema sub-phase offered if schema issues found (Phase 4 only) | If any row in Phase 4 scored the schema overview element as Weak, Not Present, or Opportunity: user was explicitly asked about running the Schema Sub-Phase before /compact was called. Not applicable in Phases 1–3, 5, 6. |

---

## L2 — PRE-WORKBOOK GATE

Run after Phase 6 is complete, before running extract_data.py.

| # | Check | Pass condition |
|---|---|---|
| L2-01 | All 6 phase .md files exist in Outputs/ | All present |
| L2-02 | All 6 phase headers identical to canonical above | Diff = zero across all 6 |
| L2-03 | Total rows across all 6 phases = 122 | Sum of L1-04 checks = 122 |
| L2-04 | All 9 mandatory Phase 4 tertiary CSVs exist in Outputs/CSV/ | All 9 present |
| L2-05 | No stale workbook_data.json exists from a previous run | File absent or explicitly deleted |
| L2-06 | extract_data.py CLIENT_NAME, AUDIT_DATE, AUDIT_DIR are set | No empty strings in config block |
| L2-07 | Production Plan [x] items match files that exist on disk | Every [x] verified against Outputs/ |
| L2-08 | All 9 mandatory Phase 4 export CSVs uploaded to Google Drive and Drive URLs recorded | 9 Drive URLs present in Sources column of Phase 4 .md file |

---

## L3 — POST-PIPELINE GATE

Run after generate_gsheet.py confirms the Google Sheet is created.

| # | Check | Pass condition |
|---|---|---|
| L3-01 | workbook_data.json is valid JSON | No parse exception |
| L3-02 | Row count in JSON = 122 | Confirmed by extract_data.py row count output |
| L3-03 | All 17 keys present in every JSON row | No missing keys in spot-check of 5 rows |
| L3-04 | Google Sheet URL saved to Workbook/workbook_url.txt | File present and contains a valid https://docs.google.com/spreadsheets/ URL |
| L3-05 | Google Sheet has correct tab names | Performances summary — Detailed Technical Audit — Schema Analysis — Sources — Glossary |
| L3-06 | Detailed Technical Audit tab: 19 columns, 123 rows (122 data + 1 header) | Confirmed by generate_gsheet.py output summary |

---

## L4 — POST-HTML GATE

Run after all 9 .html files are written to the HTML/ folder.

| # | Check | Pass condition |
|---|---|---|
| L4-01 | All 9 .html files exist in HTML/ folder | index.html + technical.html + ux.html + tools.html + on-site.html + off-site.html + geo.html + schema.html + methodology.html |
| L4-02 | No element codes in any .html file | Zero matches on [TUOCFG][0-9]{2} across all 9 files |
| L4-03 | No "Phase" references in any .html file | Zero matches on "Phase [0-9]" in any file |
| L4-04 | No automated-audit language in any .html file | Zero matches on "user confirmed", "user-provided", "user said" |
| L4-05 | All internal links use relative paths | No absolute file:// paths in any href or src attribute |
| L4-06 | All 8 section nav links present in every page header | Spot-check nav block on index.html and one section page |
| L4-07 | Executive summary on index.html contains no numbers | Spot-check exec-summary section — no digits, scores, or percentages |
| L4-08 | Each section page has breadcrumb linking back to index.html | Spot-check breadcrumbs on two section pages |
| L4-09 | workbook_data.json row count matches total dropdown items across all section pages | Exclude Data Missing and Not Applicable rows from count |
| L4-10 | Priority matrix present on index.html with 5–7 scatter dots | `.scatter-dot` elements: count between 5 and 7 inclusive. Each has a `href` attribute pointing to a section page. Each has a `.dot-tooltip` child with non-empty text. |
| L4-11 | HTML files generated via scripts/generate_html.py — not manually | All 9 pages contain consistent Tailwind CDN `<script>` tag and `font-headline` class in `<head>`. Pages generated manually will have inconsistent or missing Tailwind config. |

---

*CHECKS.md | seo-geo-technical-audit | Version 12 | April 2026*
