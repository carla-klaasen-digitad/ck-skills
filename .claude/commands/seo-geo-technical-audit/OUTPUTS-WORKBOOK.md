---
name: seo-geo-technical-audit / OUTPUTS-WORKBOOK.md
load: On demand — read before generating the final workbook (Google Sheet).
---

# SEO & GEO Audit — Workbook Generation Spec

---

## WORKBOOK GENERATION — REQUIRED APPROACH

Workbook generation requires the two-script pipeline. Do not hardcode audit row data as Python string literals inside a generation script — this approach fails at 50+ rows due to context exhaustion.

Required approach:
1. Run `scripts/extract_data.py` to parse all phase .md files and write `{AUDIT_DIR}/Workbook/workbook_data.json`
2. Run `scripts/generate_gsheet.py` to read the JSON and create the Google Sheet in Google Drive

Both scripts are in `scripts/`. Only `CLIENT_NAME`, `AUDIT_DATE`, `AUDIT_DIR`, and `PHASE_SCORES` need to be updated at the top of `extract_data.py`. Set only `AUDIT_DIR` at the top of `generate_gsheet.py`. All parsing and formatting logic is reusable without modification.

`generate_workbook.py` (.xlsx) is retained as an optional local backup only. It is not the primary deliverable and does not need to be run for a standard audit.

---

## PRE-GENERATION CHECKLIST

Before generating the workbook:
1. All phase .md scoring files are written to disk and confirmed complete
2. All Phase 4 tertiary issue files are written to disk (confirmed via FORMS.md Phase 4 checklist and check if more files should be generated for the report)
3. Schema sub-phase output is written to disk (if applicable)
4. /compact has been run
5. Read examples/audit-workbook-example.csv to calibrate tone of voice and writing style only — it demonstrates the correct level of specificity, sentence structure, and plain-language framing. Do not use it to infer column structure or column order. For non-negotiable column rules, this file (OUTPUTS-WORKBOOK.md) and CLAUDE.md are the authoritative sources.
6. Confirm all Phase 4 tertiary export CSVs have been uploaded to Google Drive as Google Sheets and their Drive URLs are recorded in the Sources column of each scoring row.
7. Ask user: "All phases reviewed. Confirm any last adjustments before I generate the workbook."

Do not generate the workbook until the user confirms the format and gives explicit approval to proceed.
Give an example of the first 10 rows for user to validate before creating the whole file. 
The workbook is a mandatory deliverable — it cannot be bypassed or deferred silently.

---

## TAB STRUCTURE

| Tab # | Tab Name | Contents |
|---|---|---|
| 1 | Performances summary | Overall health score, audit completeness %, domain expiry warning if within 90 days, element count by priority level, top 3 critical issues |
| 2 | Detailed Technical Audit | All 6 phases consolidated into one table. Rows grouped by Family/Phase first (matching the PHASES list order: Technical → UX → Tools & Config → On-Page → Off-Site → GEO), then sorted by Category within each phase group, then by Sub-Category within each Category. Phase grouping always takes precedence over alphabetical Category sorting. Auto-filter enabled on all columns. Uses 16-column layout (Data Analyzed excluded — see COLUMN STRUCTURE note). |
| 3 | Schema Analysis | Full schema sub-phase output per page type — current markup, errors, corrected JSON-LD |
| 4 | Sources | Links to all tertiary export Google Sheets and Google Docs generated during the audit, with a brief description of each |
| 5 | Glossary | Definitions of all scoring terms, priority labels, and column headings |

---

## COLUMN STRUCTURE — ALL SCORING TABS

Phase .md scoring files use 17 columns. The Google Sheet uses 19 columns (A–S). Column A is a blank spacer, Score Explanation moves to column L (after Priority Score), Data Analyzed is now included as column O, and column S (Comments for Claude) is always empty when written by the script — it is filled by the user post-delivery as part of the feedback loop. Do not reorder or add columns to the phase .md files — extract_data.py and generate_gsheet.py handle all remapping.

Google Sheet column order (19 columns A–S):
`A(blank) | B(Status) | C(Family) | D(Category) | E(Sub-Category) | F(Analyzed Element) | G(Description) | H(Score) | I(Weight/Importance Numeric) | J(Importance Tier) | K(Priority Score) | L(Score Explanation) | M(Priority) | N(Who's in charge?) | O(Data Analyzed) | P(How to correct?) | Q(Comments) | R(Sources) | S(Comments for Claude)`

Column rules — apply to every scoring tab:

- **A (blank)**: Empty spacer column — no data, no header. Visual padding only.
- **Status**: To do (fixed value for all rows in the workbook — the client uses this column to track remediation progress. The audit-phase status values — "Issue Found," "Passing," "Opportunity," etc. — live only in the phase .md scoring files and are overridden to "To do" by extract_data.py during workbook generation). **Column B must have dropdown validation** — generate_gsheet.py applies a ONE_OF_LIST data validation rule on column B (rows 2–200) with these values: Issue Found, Passing, Opportunity, Data Missing, Not Applicable, Manual Verification Required, To do. This is mandatory so the client can update status using a dropdown.
- **Family**: Phase label — Technical, UX, Tools & Configuration, On-Site SEO, Off-Site, GEO / AI Visibility
- **Category**: Element grouping within family — e.g. Indexation, Security, Speed, Schema. Elements in the same Category must be grouped together in row order.
- **Sub-Category**: Specific sub-grouping where applicable — e.g. Mobile Speed, Desktop Speed
- **Analyzed Element**: Full element name only — no element code, no phase reference. E.g. "Indexation Errors" not "T01 — Indexation Errors"
- **Description**: Full element description in plain language — written for a client audience. No element codes. No phase references. No cross-references to other rows.
- **Score**: Written in full — Not Present / Weak / Medium / High / Excellent / Not Applicable / DATA MISSING
- **Weight/Importance (Numeric)**: 10 / 7.5 / 5 / 2.5
- **Importance Tier**: Critical / High / Medium / Low (matching numeric weight)
- **Priority Score**: Score Value × Weight (lower = more urgent). Leave blank for DATA MISSING rows.
- **Score Explanation**: Descriptive explanation of the score. Full sentences. The problem description lives here — not in How to Correct. This should be easy to understand but still aimed at a technical and knowledgeable audience. **Never list individual URLs in Score Explanation** — state the count, the finding, and the category summary only, then reference the export for details (e.g. "24 URLs returning 404 errors were identified — full breakdown is in the 404 Errors export."). URL lists belong in the export file, not in this cell.
- **Priority**: HIGH / MEDIUM / LOW / MONITOR / Manual Verification Required. No emoji. No shorthand. Write "Manual Verification Required" when a score cannot be confirmed without further verification.
- **Who's in charge?**: Write only "Digitad" or "Technical Team" — no client team references, no individual names
- **Data Analyzed**: Raw data observations recorded before scoring — what was measured, counted, or found in the source exports (e.g. "Screaming Frog crawl: 45 of 51 URLs under 300 words"). This separates observed data from editorial commentary. Leave blank for DATA MISSING or Not Applicable rows.
- **How to correct?**: Step-by-step solution only — no problem restatement (that belongs in Score Explanation). Format: each step on a new line beginning with a bullet (•). If the field contains more than 2 URLs, ask the user whether to create a separate export for those URLs and replace them with a short summary.
- **Comments**: Plain language source attribution only. No element codes (T01, G09, etc.), no phase references, no cross-links to other elements. [COMP:] tags and [W-ADJ:] flags are permitted. If a reviewer reads only one row, the Comments cell must make sense without any other context.
- **Sources**: Solution-oriented references only — output reports and remediation files generated during the audit (e.g. "Title Tag Issues Report," "Redirect Plan"). Raw data exports (Screaming Frog CSVs, Majestic exports, etc.) belong in the Data Analyzed column, not Sources. Leave Sources blank when: (1) the element is passing or monitor with no remediation needed; (2) the sole evidence is a direct owner confirmation — "User confirmation" is not a valid Source entry; (3) no remediation report was generated for this element. Do not list generic tool URLs, external website links, or any attribution to the chat interaction.
- **Comments for Claude**: User-filled post-delivery. Leave empty when writing the sheet. Claude reads this column after the user adds comments and applies the requested adjustments. Skill-watchdog also reads this column for skill improvement signals. See COMMENTS FOR CLAUDE — FEEDBACK LOOP section below.
- **Priority column (M) — user-filled**: Column M is left blank by the script. generate_gsheet.py writes a dropdown (High / Medium / Low / Monitor / Manual Verification Required) and conditional formatting rules so colours + bold apply automatically when the user selects a value. Claude does not pre-fill Priority values in the sheet.
- **Who's in charge? column (N) — user-filled**: Column N is left blank by the script. generate_gsheet.py writes a dropdown (Digitad / Technical Team). Claude does not pre-fill this column.
- **Priority special cases** (for phase .md scoring files — not the sheet):
  - If a score cannot be confirmed without manual verification: write "Manual Verification Required" in the phase .md
  - If an element is not applicable for this site type: write Not Applicable in Score and leave Priority blank
  - If a row scores Excellent (rating value 5), the Priority label in the phase .md must be LOW or MONITOR — never HIGH or MEDIUM.

---
## Brand Identity — Digitad

All deliverables follow the Digitad brand guidelines:

**Typography:** Poppins
**Primary color:** Red `#9b1e22` (R:155, G:30, B:34) | Hover: `#8f0015` | Light: `#fce8eb`
**Neutrals:** Black `#000000` | Grays: `#1a1a1a`, `#666666`, `#999999`, `#e5e5e5`, `#f5f5f5` | White `#ffffff`

**Export formatting (Google Sheets / CSV deliverables):**
- Top banner row with brand color
- Header row: red background (`#9b1e22` — RGB 0.608, 0.118, 0.133 in 0–1 scale for Google Sheets API), white bold text
- Clean data rows below
- Font: Poppins where possible

Priority colour fills in the Google Sheets API use 0–1 RGB scale (not hex). See generate_gsheet.py for the correct RGB values for HIGH, MEDIUM, LOW, MONITOR, and Manual Verification Required rows.

---

## WORKBOOK FORMATTING

| Setting | Value |
|---|---|
| Font | Poppins — fallback to Arial (Google Sheets default) |
| Header row | Bold, frozen (row 1), auto-filter enabled on every column |
| Column widths | Auto-fitted to content — minimum 15 characters wide |
| Text wrapping | Enabled on Description, Score Explanation, How to correct, Comments, Sources columns |
| How to correct formatting | Each bullet point (•) on a new line within the cell |

---

## EXECUTIVE SUMMARY TAB CONTENT

```
EXECUTIVE SUMMARY — [Site] Technical & GEO Audit
Prepared by: Digitad | Date: [date]

OVERALL HEALTH: [score/100] — [one-sentence verdict in plain language]

WHAT IS WORKING WELL
1. [Element name in plain language]: [plain language strength — no element codes, no phase references]
2. [Element name in plain language]: [plain language strength]
3. [Element name in plain language]: [plain language strength]

WHAT NEEDS IMMEDIATE ATTENTION
1. [Element name in plain language]: [plain language problem] — [plain language fix] — [business impact]
2. [Element name in plain language]: [plain language problem] — [plain language fix] — [business impact]
3. [Element name in plain language]: [plain language problem] — [plain language fix] — [business impact]
4. [Element name in plain language]: [plain language problem] — [plain language fix] — [business impact]
5. [Element name in plain language]: [plain language problem] — [plain language fix] — [business impact]

AI & SEARCH VISIBILITY
[2–3 sentences on LLM readiness, AI Overview presence, entity optimisation status — written for a non-technical client]

SCHEMA MARKUP
[1–2 sentences on overall schema health and biggest gap — no technical jargon without explanation]
```

---

## GOOGLE SHEETS BUILD PROCESS (gspread)

Build the Google Sheet from `workbook_data.json`. Do not re-score. Do not modify any scores.

**IMPORTANT — large file reading**: Before reading any phase .md file, check its size first: `wc -c [filename]`. If the file is over 40KB, use bash sed chunking to read it in sections. Example: `sed -n '1,100p' phase4.md` then `sed -n '101,200p' phase4.md`. Never attempt a direct Read on a phase file — large phases will exceed the token limit.

Run order:
1. `python3 scripts/extract_data.py` — parses all phase .md files, writes `Workbook/workbook_data.json`
2. `python3 scripts/generate_gsheet.py` — reads the JSON, creates the Google Sheet, moves it to the correct Drive folder, prints the Sheet URL

Set `AUDIT_DIR` at the top of both scripts before running. `generate_gsheet.py` reads Drive folder IDs from `audit-session-config.json` — ensure `init_session.py` has been run first.

The script uses `api_clients.py` for authenticated Google Sheets and Drive access via the service account. On completion, the Sheet URL is saved to `Workbook/workbook_url.txt`.

---

---

## FILE NAMING — TERTIARY EXPORTS

All tertiary export files (CSVs, .txt reports, conditional outputs) follow this convention:

`[CLIENT_NAME]-[report-name].[ext]`

- CLIENT_NAME: all caps (e.g. YOCRUNCH, NOVABITE, ACMECORP)
- report-name: lowercase, hyphen-separated (e.g. title-tag-issues, disavow, robots-txt-recommendation)
- No date in export filenames — date is reserved for main deliverables only

Examples: `YOCRUNCH-title-tag-issues.csv` · `YOCRUNCH-disavow.txt` · `YOCRUNCH-internal-linking-report.csv`

Main deliverables (workbook, executive summary, session log, phase .md files) keep the existing convention: `[Client Name] - [Description] - [Month Year].[ext]`

**Google Sheet and Google Doc display names** — when uploading to Google Drive (via upload_exports.py or generate_gsheet.py), use the main deliverable convention for the Drive display name:
- Workbook (Google Sheet): `[Client Name] - SEO GEO Audit - [Month Year]`
- Tertiary export sheets: `[CLIENT_NAME] - [Report Name] - [Month Year]` (CLIENT_NAME in caps, report name title-cased)
- Google Docs (robots.txt, disavow): `[Client Name] - [Document Name] - [Month Year]`

---

## SHEET INPUT — CREATE NEW VS WRITE TO EXISTING

At workbook generation time (after Phase 6), ask the user:

"How would you like the workbook delivered?
  (a) Create a new Google Sheet — I'll create a fresh spreadsheet in your Drive folder.
  (b) Write to an existing Google Sheet — paste the Sheet ID and the tab name to write into.
Which do you prefer?"

**If (a) Create new:**
1. Confirm the Drive folder ID (from `audit-session-config.json` or ask now).
2. Leave `SHEET_ID` empty in `generate_gsheet.py`. Set `AUDIT_DIR` only.
3. The script creates a new spreadsheet titled `[Client Name] - SEO GEO Audit - [Month Year]`.

**If (b) Write to existing:**
1. Ask: "Paste the Sheet ID (the string between /d/ and /edit in the URL) and the tab name to write audit data into."
2. Set `SHEET_ID` and `TAB_NAME` at the top of `generate_gsheet.py` before running.
3. The script opens the existing spreadsheet, finds or creates the named tab, and writes all audit data into it.
4. All other tabs (Performances summary, Schema Analysis, Sources, Glossary) are also written to the same spreadsheet.

---

## COMMENTS FOR CLAUDE — FEEDBACK LOOP

This step runs after the Google Sheet is delivered to the user. Do not skip it — it is a required post-delivery checkpoint.

**Step 1 — Prompt the user:**
After confirming the sheet URL, present:
"The Google Sheet is ready. Please open column S (Comments for Claude) in the audit tab and add any notes for rows you'd like me to revise — for example: 'Score should be High not Medium', 'Expand the fix steps', or 'This does not apply here'. Type **comments added** when done, or **no comments** to skip."

**Step 2 — Read column S:**
After user confirms, read column S from the sheet using `mcp__google-sheets__readSpreadsheet`. Request the full audit tab range (e.g. `Technical Audit!A1:S200`). Identify every row where column S (index 18) is non-empty.

**Step 3 — Apply adjustments:**
For each non-empty column S row:
- Parse the comment to identify the type of adjustment (score, priority, explanation, how-to, etc.).
- Apply the change directly to the corresponding cell in the sheet using the Google Sheets MCP write tools.
- Simultaneously, locate the matching row in the corresponding phase .md source file (match on Analyzed Element text, element codes stripped) and apply the same change to that file. This keeps the phase .md and the sheet in sync.
- If a comment is ambiguous, ask for clarification before making a change.

After all adjustments are applied to both the sheet and the phase .md files, offer to re-run the full pipeline:
"All column S adjustments have been applied to the sheet and the source .md files. Would you like me to re-run the pipeline (extract_data.py → generate_gsheet.py) to regenerate workbook_data.json and refresh all sheet tabs with the updated data?"
- If yes: run `python3 scripts/extract_data.py` then `python3 scripts/generate_gsheet.py` from the skill directory with the client's AUDIT_DIR set, and confirm the updated sheet URL.
- If no: note in the session-state.md that column S adjustments were applied manually and the pipeline was not re-run this session.

After the pipeline decision, ask: "Would you like to clear the column S comments now that they have been applied?" If yes, blank each adjusted cell in column S using the Google Sheets MCP write tools.

**Step 4 — Output a summary:**
After applying all adjustments:

```
COMMENTS FOR CLAUDE — ADJUSTMENTS APPLIED — [Site] — [Date]

| Analyzed Element | Comment | Adjustment Made | Phase .md Updated | Sheet Cell Updated |
|---|---|---|---|---|
```

If no comments were added: "No column S comments found. Proceeding to HTML report."

**Step 5 — Watchdog signal (if active):**
If skill-watchdog is active this session, pass all non-empty column S values to the watchdog Phase 5 registry update. These are logged as skill improvement signals — patterns in the comments (e.g. repeated score corrections in a specific phase, recurring tone feedback) indicate where scoring logic or reference thresholds should be updated in future versions.

---

*OUTPUTS-WORKBOOK.md | seo-geo-technical-audit | Version 14 | May 2026*
