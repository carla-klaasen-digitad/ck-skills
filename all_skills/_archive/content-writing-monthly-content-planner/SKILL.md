---
name: monthly-content-planner
description: Use when running the monthly on-site content planning workflow. Reads all approved brand guidelines, scans the production plan for the current month rows without a brief link, creates a Neuronwriter brief via API, generates a pre-populated Google Doc content brief from the brand template, writes both links back to the production plan, and emails a search landscape summary to the analyst. Runs automatically on the first Monday of each month. Trigger phrases: "run content planner", "monthly content plan", "create this month briefs", "fill production plan", "run the content workflow".
allowed-tools: Bash, Read, Write, Edit
---

# Monthly On-Site Content Planner

You are a senior SEO content strategist at Digitad. Your job is to run the monthly on-site content brief creation workflow for all approved brands. This skill runs automatically on the first Monday of each month and can also be triggered manually.

**Always invoke `/skill-watchdog monthly-content-planner` in parallel at the start of this skill.**

---

## Configuration

```
ENV_FILE           = /Users/carlaklaasen/claude_code/.env
GUIDELINES_DIR     = /Users/carlaklaasen/claude_code/all_skills/content-writing/guidelines
SCRIPTS_DIR        = /Users/carlaklaasen/claude_code/.claude/commands/monthly-content-planner/scripts
PRODUCTION_PLAN_ID = 13ZKd5UVG_OcvRS9Wri8c8XSbwqiCguiJBDvUuUN9hbg
```

---

## Phase 0 — Pre-flight and Brand Scan

### 0.1 — Determine current month context

```bash
python3 -c "
from datetime import date
t = date.today()
print('MONTH_NAME=' + t.strftime('%B'))
print('YEAR=' + str(t.year))
print('FOLDER_LABEL=' + t.strftime('%B %Y'))
print('DOC_MONTH=' + t.strftime('%Y-%m'))
"
```

Store: MONTH_NAME (e.g. May), YEAR (e.g. 2026), FOLDER_LABEL (e.g. May 2026), DOC_MONTH (e.g. 2026-05).

If a manual override is passed (e.g. `month=April year=2026`), use those values instead.

### 0.2 — Load environment variables

```bash
python3 SCRIPTS_DIR/sheets_helper.py load_env ENV_FILE
```

Required: NEURONWRITER_API_KEY, GOOGLE_SERVICE_ACCOUNT_FILE.

### 0.3 — Scan brand guidelines for approved brands

```bash
python3 SCRIPTS_DIR/sheets_helper.py scan_brands GUIDELINES_DIR
```

Parse each .md file in GUIDELINES_DIR (exclude general_legal.md). For each file extract:
- brand_key: filename without .md (e.g. activia)
- brand_label: uppercase brand name (e.g. ACTIVIA)
- website_url: field 1
- status: field 2 — include brand only if matches /appro/i
- tab_name: field 4
- folder_url: field 5 — extract Drive folder ID from URL
- template_doc_url: field 6 — extract Doc ID from URL
- nw_project_url: field 7 — extract project ID (segment after /project/view/)

Log: "[N] approved brands found: [list]"
If zero approved brands: log INFO and exit cleanly.

---

## Phase 1 — Production Plan Read (per brand)

For each approved brand:

```bash
python3 SCRIPTS_DIR/sheets_helper.py read_rows \
  --sheet-id PRODUCTION_PLAN_ID \
  --tab "{tab_name}" \
  --month "{MONTH_NAME}" \
  --year "{YEAR}"
```

Reads the sheet tab. Filters rows where:
- col D (Month) == MONTH_NAME (case-insensitive)
- col E (Year) == YEAR (as string or int)
- col N (Content) is blank or empty

Returns JSON list of eligible rows. Each row:
  row_index, col_k (Heading), col_l (Target keyword),
  col_m (Secondary keywords), col_n (Content link),
  col_p (URL), col_q (Brief link)

Skip rows where col_l is blank.
Log: "[brand] — [N] eligible rows for [MONTH_NAME] [YEAR]"

---

## Phase 2 — Neuronwriter Brief Creation (per row)

For each eligible row:

### 2.1 Create NW analysis via API

```bash
python3 SCRIPTS_DIR/neuronwriter_api.py create_analysis \
  --project-id "{nw_project_id}" \
  --keyword "{col_l}" \
  --secondary "{col_m}" \
  --title "{col_k}" \
  --country "us" \
  --language "en"
```

Returns: analysis_url (https://app.neuronwriter.com/analysis/view/ID), analysis_id.

If API call fails: log [WARN] and set analysis_url to empty string. Do not block the row.

### 2.2 Update meta in NW (title and keywords)

If analysis_id is available:

```bash
python3 SCRIPTS_DIR/neuronwriter_api.py update_meta \
  --analysis-id "{analysis_id}" \
  --title "{col_k}" \
  --target-keyword "{col_l}" \
  --secondary-keywords "{col_m}"
```

### 2.3 Write NW URL to col Q in production plan

```bash
python3 SCRIPTS_DIR/sheets_helper.py write_cell \
  --sheet-id PRODUCTION_PLAN_ID \
  --tab "{tab_name}" \
  --row {row_index} \
  --col Q \
  --value "{analysis_url}"
```

Log: "[brand] row {row_index} — NW brief: {analysis_url}"

---

## Phase 3 — Google Doc Brief Creation (per row)

### 3.1 Ensure monthly folder exists

Folder name pattern: "{BRAND_LABEL} - {FOLDER_LABEL}"
Examples: "ACTIVIA - May 2026", "OIKOS - May 2026"

```bash
python3 SCRIPTS_DIR/gdocs_helper.py ensure_folder \
  --parent-id "{folder_id}" \
  --name "{BRAND_LABEL} - {FOLDER_LABEL}"
```

Returns: monthly_folder_id, created (true/false).

### 3.2 Copy template into monthly folder

Document name pattern: "{BRAND_LABEL} - {DOC_MONTH} - {col_k}"
Example: "ACTIVIA - 2026-05 - Peach Yogurt Drink"

```bash
python3 SCRIPTS_DIR/gdocs_helper.py copy_template \
  --template-id "{template_doc_id}" \
  --dest-folder-id "{monthly_folder_id}" \
  --title "{BRAND_LABEL} - {DOC_MONTH} - {col_k}"
```

Returns: new_doc_id, doc_url.

### 3.3 Populate Editorial Information table

```bash
python3 SCRIPTS_DIR/gdocs_helper.py populate_brief \
  --doc-id "{new_doc_id}" \
  --keyword "{col_l}" \
  --secondary "{col_m}" \
  --heading "{col_k}" \
  --url "{col_p}" \
  --nw-link "{analysis_url}" \
  --brand "{brand_key}"
```

Fields populated in the Editorial Information table:
- Keyword row: col_l
- Secondary Keyword row: col_m
- Title row: col_k
- URL row: col_p
- NEURONWRITER LINK/BRIEF line: analysis_url

Meta-title and meta description rows are left blank for the writer to complete.
The Quality Check table rows are left blank.

### 3.4 Write Google Doc URL to col N in production plan

```bash
python3 SCRIPTS_DIR/sheets_helper.py write_cell \
  --sheet-id PRODUCTION_PLAN_ID \
  --tab "{tab_name}" \
  --row {row_index} \
  --col N \
  --value "{doc_url}"
```

Log: "[brand] row {row_index} — Brief doc: {doc_url}"

### 3.5 Update status in col C to "Writing (Digitad)"

```bash
python3 SCRIPTS_DIR/sheets_helper.py write_cell \
  --sheet-id PRODUCTION_PLAN_ID \
  --tab "{tab_name}" \
  --row {row_index} \
  --col C \
  --value "Writing (Digitad)"
```

---

## Phase 4 — SE Ranking and GSC Data Pull

For each processed row, pull keyword search landscape data using SE Ranking GSC integration.

```bash
python3 SCRIPTS_DIR/sheets_helper.py pull_keyword_data \
  --keyword "{col_l}" \
  --website "{website_url}"
```

This calls the SE Ranking API (DATA_getSerpResults and PROJECT_getGoogleSearchConsole).
Returns: position, clicks_28d, impressions_28d.

If no data: use "-" for all fields. Never block on missing data.

Store all results in memory for Phase 5.

---

## Phase 5 — Analyst Email

Compile one email after all brands are processed.

### 5.1 Build summary per brand

For each brand, list every brief created this month:
| Brand | Heading | Target Keyword | Brief Doc | NW Brief | Position | Clicks | Impressions |

### 5.2 Send email via Gmail

```bash
python3 SCRIPTS_DIR/email_helper.py send \
  --subject "Content Briefs Ready — {MONTH_NAME} {YEAR}" \
  --brand-json "{summary_json}"
```

Email is sent to the analyst address configured in email_helper.py.
If send fails: log [WARN] and write summary to run log only.

---

## Phase 6 — Run Summary

Output to chat after completion:

  Monthly Content Planner — {MONTH_NAME} {YEAR}
  Brands processed:   N
  Total rows scanned: N
  Briefs created:     N
  Rows skipped:       N (already had link)
  NW API errors:      N
  Email sent:         YES / NO / FAILED

  Per brand:
    [brand] — N briefs
      [Heading] → [doc_url]

---

## Error Handling

Never stop the entire run due to a single brand or row failure.

| Scenario | Action |
|---|---|
| Brand file missing required logistical fields | Skip brand, log WARN |
| Production plan tab not found | Skip brand, log WARN |
| No eligible rows for brand | Log INFO, continue |
| NW API failure | Leave col Q blank, continue to doc creation |
| Google Doc copy failure | Log FLAG, skip row |
| GSC data unavailable | Use "-" values |
| Email send failure | Log WARN, do not block completion |

---

## Manual Trigger

Run for current month:
  /monthly-content-planner

Run for a past month (back-fill):
  /monthly-content-planner month=April year=2026

---

## Schedule Registration

This skill runs on the first Monday of each month at 9:00 AM.
Cron expression: 0 9 * * 1#1

To check schedule status: /schedule list
To re-register: run /schedule and follow prompts
