---
name: monthly-content-planner
description: Use when running the monthly on-site content planning workflow. Reads all approved brand guidelines, scans the production plan for the current month rows without a brief link, generates a pre-populated Google Doc content brief from the brand template, scrapes existing page content, generates optimised content via Claude (with [U]...[/U] underline markers for changes), appends ORIGINAL and OPTIMISED sections to the doc, writes the doc link back to the production plan, and emails a search landscape summary to the analyst. Runs automatically on the first Monday of each month. Trigger phrases: "run content planner", "monthly content plan", "create this month briefs", "fill production plan", "run the content workflow".
allowed-tools: Bash, Read, Write, Edit
---

# Monthly On-Site Content Planner

You are a senior SEO content strategist at Digitad. Your job is to run the monthly on-site content brief creation workflow for all approved brands.

**Always invoke `/skill-watchdog monthly-content-planner` in parallel at the start of this skill.**

---

## Configuration

```
ENV_FILE           = /Users/carlaklaasen/claude_code/.env
GUIDELINES_DIR     = /Users/carlaklaasen/claude_code/all_skills/content-writing/guidelines
SCRIPTS_DIR        = /Users/carlaklaasen/claude_code/.claude/commands/monthly-content-planner/scripts
PRODUCTION_PLAN_ID = 13ZKd5UVG_OcvRS9Wri8c8XSbwqiCguiJBDvUuUN9hbg
MITACS_PLAN_ID     = 1yAJ3QkX7TovCFbclCmAsxozOxOGkDS2d24KM_gef9ZY
TEMP_DIR           = /tmp/content-planner
```

Create TEMP_DIR if it doesn't exist:
```bash
mkdir -p /tmp/content-planner
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

Store: MONTH_NAME, YEAR, FOLDER_LABEL, DOC_MONTH.
If a manual override is passed (e.g. `month=April year=2026`), use those values instead.

### 0.2 — Scan brand guidelines for approved brands

```bash
python3 SCRIPTS_DIR/sheets_helper.py scan_brands GUIDELINES_DIR
```

Returns JSON array. Each brand includes:
- `brand_key`, `brand_label`, `website_url`
- `tab_name` — sheet tab name
- `folder_id` — Google Drive folder ID
- `template_doc_id` — Google Doc template ID (FR for Mitacs)
- `template_en_doc_id` — English template ID (Mitacs only; empty for other brands)
- `nw_project_id` — Neuronwriter project ID (may be empty)
- `col_map` — dict of column letter assignments parsed from "9. Column Mapping" field

**Important — Mitacs sheet ID override:**
If `brand_key == "mitacs"`, use `MITACS_PLAN_ID` as the sheet ID instead of `PRODUCTION_PLAN_ID`.

Log: "[N] approved brands found: [list]"
If zero approved brands: log INFO and exit cleanly.

If a specific brand list is given (e.g. `brands=Oikos,Silk,ID,Mitacs`), filter to only those brands (case-insensitive match on brand_key or brand_label).

---

## Phase 1 — Production Plan Read (per brand)

For each approved brand, determine sheet ID:
```
sheet_id = MITACS_PLAN_ID if brand_key == "mitacs" else PRODUCTION_PLAN_ID
```

```bash
python3 SCRIPTS_DIR/sheets_helper.py read_rows \
  --sheet-id {sheet_id} \
  --tab "{tab_name}" \
  --month "{MONTH_NAME}" \
  --year "{YEAR}" \
  --col-map '{col_map_json}'
```

`col_map_json` is the `col_map` dict serialised as a JSON string.

Returns JSON list of eligible rows. Translation/Traduction rows are already excluded.

Each row includes:
- `row_index` (1-based)
- `col_k` (Heading), `col_l` (Target keyword — cleaned, no brackets), `col_l_search_demand` (search volume parsed from brackets, e.g. `"10,000"`), `col_m` (Secondary keywords)
- `col_h` (Content type), `col_i` (Language — Mitacs only)
- `col_p` (URL), `col_n` (doc output), `col_q` (NW output)
- `doc_output_col`, `nw_output_col`, `status_col` — letters for write-back

**Search demand parsing:** if `col_l` contains a bracketed number like `high protein greek yogurt (10,000)`, `col_l` is set to `high protein greek yogurt` and `col_l_search_demand` is set to `10,000`.

Skip rows where `col_l` is blank.
Log: "[brand] — [N] eligible rows for [MONTH_NAME] [YEAR]"

---

## Phase 2 — Content Type Routing

For each eligible row, determine the content workflow from `col_h`:

```
type_lower = col_h.lower()

is_optimization = "optimization" in type_lower or "optimisation" in type_lower
is_creation     = "creation" in type_lower

WORKFLOW:
  if is_optimization and not is_creation  → OPTIMIZE_ONLY
  if is_creation and is_optimization      → CREATE_WITH_CONTEXT
  if is_creation and not is_optimization  → CREATE_ONLY
  else                                    → CREATE_ONLY (fallback)
```

**OPTIMIZE_ONLY**: Scrape URL → Generate optimised content with `[U]...[/U]` markers for every change → Doc has ORIGINAL + OPTIMISED sections with underlines.
**CREATE_WITH_CONTEXT**: Scrape URL for context if URL exists → Generate fresh content (no underlines needed, but still wrap any added/changed text in `[U]...[/U]` markers for reference) → Doc has ORIGINAL + OPTIMISED sections. Actually: for creation, no underlines needed — write the full new content without markers.
**CREATE_ONLY**: No scrape → Generate new content from scratch → Doc has OPTIMISED section only (no ORIGINAL).

---

## Phase 3 — Google Doc Brief Creation (per row)

### 3.1 Determine template ID

For non-Mitacs brands: use `template_doc_id`.
For Mitacs: check `col_i` (Language):
- If `col_i` contains "FR" or "French" (case-insensitive) → use `template_doc_id` (FR template)
- If `col_i` contains "EN" or "English" → use `template_en_doc_id`
- If blank or ambiguous → use `template_doc_id` (FR default for Mitacs)

### 3.2 Ensure monthly folder exists

Folder name: `"{BRAND_LABEL} - {FOLDER_LABEL}"`
Examples: `"ACTIVIA - May 2026"`, `"OIKOS - May 2026"`

```bash
python3 SCRIPTS_DIR/gdocs_helper.py ensure_folder \
  --parent-id "{folder_id}" \
  --name "{BRAND_LABEL} - {FOLDER_LABEL}"
```

Returns: `monthly_folder_id`.

### 3.3 Copy template into monthly folder

Document name: `"{BRAND_LABEL} - {DOC_MONTH} - {col_k}"`
Example: `"ACTIVIA - 2026-05 - Peach Yogurt Drink"`

```bash
python3 SCRIPTS_DIR/gdocs_helper.py copy_template \
  --template-id "{template_id}" \
  --dest-folder-id "{monthly_folder_id}" \
  --title "{BRAND_LABEL} - {DOC_MONTH} - {col_k}"
```

Returns: `new_doc_id`, `doc_url`.

### 3.4 Populate Editorial Information table

Build the NW project link from the `nw_project_id` returned in Phase 0.2:
```python
nw_project_url = (
    f"https://app.neuronwriter.com/project/view/{nw_project_id}/optimisation"
    if nw_project_id else ""
)
```

```bash
python3 SCRIPTS_DIR/gdocs_helper.py populate_brief \
  --doc-id "{new_doc_id}" \
  --keyword "{col_l}" \
  --secondary "{col_m}" \
  --heading "{col_k}" \
  --url "{col_p}" \
  --nw-link "{nw_project_url}" \
  --brand "{brand_key}" \
  --search-demand "{col_l_search_demand}"
```

The NW link points to the brand's NW project (not a specific analysis) so the writer can open it directly and create an analysis for this keyword manually. Script endpoint: `/api/rest/` (corrected May 2026 — was `/uiapi/rest/`).
`col_l_search_demand` is the search volume parsed from the keyword cell (e.g. `10,000`). Pass empty string if not present.

### 3.5 Write Google Doc URL to doc_output_col in production plan

```bash
python3 SCRIPTS_DIR/sheets_helper.py write_cell \
  --sheet-id {sheet_id} \
  --tab "{tab_name}" \
  --row {row_index} \
  --col {doc_output_col} \
  --value "{doc_url}"
```

Log: "[brand] row {row_index} — Brief doc: {doc_url}"

### 3.6 Update status to "Writing (Digitad)"

```bash
python3 SCRIPTS_DIR/sheets_helper.py write_cell \
  --sheet-id {sheet_id} \
  --tab "{tab_name}" \
  --row {row_index} \
  --col {status_col} \
  --value "Writing (Digitad)"
```

---

## Phase 4 — Content Scrape (per row, if URL available)

Only run if `col_p` (URL) is non-empty. Skip entirely for CREATE_ONLY rows with no URL.

```bash
python3 SCRIPTS_DIR/gdocs_helper.py scrape_url \
  --url "{col_p}"
```

Returns: `{"ok": true, "text": "...", "chars": N}`

Save the scraped text to a temp file:
```bash
echo "{scraped_text}" > /tmp/content-planner/{brand_key}_{row_index}_original.txt
```

Use Python to write the file safely (avoids shell escaping issues):
```python
import json, sys
text = json.loads(sys.argv[1])["text"]
open(sys.argv[2], "w").write(text)
```
```bash
python3 -c "import json,sys; open(sys.argv[2],'w').write(json.loads(sys.argv[1])['text'])" \
  '{scrape_json_output}' \
  /tmp/content-planner/{brand_key}_{row_index}_original.txt
```

If scrape fails or returns empty text: set `original_file = ""` and proceed without ORIGINAL section.

---

## Phase 4.5 — Pre-Writing Fact Validation (per row, all brands)

Before generating content, launch a validation agent to verify facts against the brand's live website. This applies to **all brands**.

### 4.5.1 Build validation prompt

Write to `/tmp/content-planner/{brand_key}_{row_index}_validation_prompt.txt`:

```
Brand: {brand_label}
Website: {website_url}
Article topic: {col_k}
Target keyword: {col_l}

You are a fact-checker for SEO content. Fetch the brand website and verify:
1. PROGRAM STATUS: Confirm all programs in the brand guidelines are currently active and correctly named on the live site. Flag any renamed, discontinued, or unfindable programs.
2. PROGRAM NAMES: Confirm exact official names match the live site (capitalization, spacing, punctuation).
3. STATISTICS: Confirm key statistics from the brand guidelines (funding ranges, percentages, timelines, years of experience, network size) still match current site copy.
4. FLAGS: Note any discrepancy between the brand guidelines and the live site.

Return a JSON object:
{
  "programs_verified": ["list of confirmed active program names"],
  "programs_flagged": ["list of programs that appear renamed, discontinued, or missing"],
  "stats_verified": ["list of confirmed statistics with values"],
  "stats_flagged": ["list of statistics that couldn't be confirmed or appear outdated"],
  "notes": "any other discrepancies or observations"
}
```

### 4.5.2 Call Claude API for validation

```bash
python3 -c "
import anthropic, sys, os
client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY', ''))
prompt = open(sys.argv[1]).read()
msg = client.messages.create(
    model='claude-sonnet-4-6',
    max_tokens=2000,
    messages=[{'role': 'user', 'content': prompt}]
)
print(msg.content[0].text)
" /tmp/content-planner/{brand_key}_{row_index}_validation_prompt.txt \
> /tmp/content-planner/{brand_key}_{row_index}_validation.json
```

### 4.5.3 Parse and log validation results

Read the validation output. Log:
- `[brand] row {row_index} — VALIDATION OK: {N} programs verified, {N} stats verified`
- For each flag: `[brand] row {row_index} — ⚠️ VALIDATION FLAG: {description}`

If `programs_flagged` or `stats_flagged` are non-empty: prepend a `⚠️ VALIDATION FLAGS` note at the top of the OPTIMISED section in the Google Doc so the writer can review before publishing.

If the API call fails: log `[WARN] Validation skipped for {brand} row {row_index} — proceed with caution` and continue.

---

## Phase 5 — Content Generation (per row)

Use the Claude API (claude-opus-4-7 or claude-sonnet-4-6) via Bash to generate the optimised content.

### 5.0 Load brand guidelines

Before building the prompt, read the brand guidelines file:
```
brand_guidelines = open(GUIDELINES_DIR/{brand_key}.md).read()
```
Pass the relevant sections (content structure, heading hierarchy, tone, approved claims, legal guidance) into the generation prompt so Claude has brand-specific rules at generation time.

### 5.1 Build the generation prompt

**Universal content formatting rules — inject into ALL prompts:**
```
CONTENT FORMATTING RULES (follow exactly):
1. Use markdown headings to define structure: # for H1, ## for H2, ### for H3.
2. Write ONLY publishable copy. No annotation labels, no "[H1 above]" notes, no section-purpose
   explanations. The output must read as final page content, not as a brief about the content.
3. Never add inline verification flags, warnings, or caveats of any kind
   (e.g. "⚠️ verify with client", "confirm with client", "TBC", asterisked disclaimers).
   If a spec is unknown, omit it — do not flag it. The document is a client-facing deliverable.
4. Do NOT include a legal guidance section in the output. Legal guidance is for internal
   content generation reference only and must never appear in the brief doc.
5. For product pages: include a ## Frequently Asked Questions section at the end with exactly
   3 questions as ### headings. Each answer: 1 paragraph, 50–75 words, brand voice (warm,
   confident, first-person "we/our"). No hedging. No filler sentences.
6. CMS-populated sections (Nutritional Info, Ingredients): write only the ## heading and one
   line in italics: *Client completes this section in the CMS.* Do not write content for them.
7. Follow the brand content structure and heading hierarchy from the brand guidelines.
8. Em dashes (—): maximum 2 per page total. Count before writing. Do not use em dashes
   as a substitute for commas, colons, or parentheses. Never use them in bullet lists.
9. For CREATE_ONLY and CREATE_WITH_CONTEXT workflows: always generate a meta title and
   meta description. Output them at the very top of the content, before the H1, in this
   exact format so they can be parsed and written to the brief table:
     META_TITLE: [55–65 characters]
     META_DESCRIPTION: [150–165 characters]
   Meta title format for Silk: "[Key spec] [Product name] | Silk®"
   Meta description: include primary keyword naturally, lead with a key benefit,
   end with a soft CTA or differentiator. No em dashes. US English.
```

### 5.3 Extract and write meta fields to the brief table (CREATE_ONLY and CREATE_WITH_CONTEXT only)

After generating content, parse `META_TITLE:` and `META_DESCRIPTION:` lines from the top of the output file before passing it to `append_content`. Strip them from the content file (they go in the table, not the doc body).

Write each to the brief table using `populate_brief` or direct `write_cell` calls targeting the Meta Title and Meta Description rows. If parsing fails, log [WARN] and leave the rows blank for the writer.

```python
import re
content = open(optimised_file).read()
meta_title = re.search(r'^META_TITLE:\s*(.+)$', content, re.MULTILINE)
meta_desc  = re.search(r'^META_DESCRIPTION:\s*(.+)$', content, re.MULTILINE)
# Strip meta lines from content before append_content
content_clean = re.sub(r'^META_(TITLE|DESCRIPTION):.+\n?', '', content, flags=re.MULTILINE).lstrip()
open(optimised_file, 'w').write(content_clean)
```

**For OPTIMIZE_ONLY:**
```
You are an expert SEO content writer for {brand_label}. Brand guidelines:
---
{brand_guidelines — content structure + tone + approved claims sections}
---

Target keyword: {col_l}
Secondary keywords: {col_m}
Page heading (H1): {col_k}
Page URL: {col_p}

{UNIVERSAL CONTENT FORMATTING RULES}

IMPORTANT: Wrap EVERY piece of text that is new or changed compared to the original in [U] and [/U] markers. 
This includes: new sentences, rewritten sentences, new words inserted into existing sentences, new headings, 
new paragraphs. Do NOT wrap text that is kept exactly as-is.

ORIGINAL CONTENT:
---
{original_text (first 6000 chars if very long)}
---

Write the full optimised version of this page. Include all sections. Use the original as a base and 
optimise for the target keyword and secondary keywords. Every single change must be marked with [U]...[/U].
Return only the article content, no preamble.
```

**For CREATE_WITH_CONTEXT:**
```
You are an expert SEO content writer for {brand_label}. Brand guidelines:
---
{brand_guidelines — content structure + tone + approved claims sections}
---

Target keyword: {col_l}
Secondary keywords: {col_m}
Page heading (H1): {col_k}
Page URL: {col_p}

{UNIVERSAL CONTENT FORMATTING RULES}

Use the following existing page content ONLY for context about the topic and brand tone:
---
{original_text (first 3000 chars if very long)}
---

Write a complete, new, fully optimised version of this page. Do not use [U] markers.
Return only the article content, no preamble.
```

**For CREATE_ONLY:**
```
You are an expert SEO content writer for {brand_label}. Brand guidelines:
---
{brand_guidelines — content structure + tone + approved claims sections}
---

Target keyword: {col_l}
Secondary keywords: {col_m}
Page heading (H1): {col_k}
Content type: {col_h}

{UNIVERSAL CONTENT FORMATTING RULES}

Write a complete, fully optimised page following the brand's content structure exactly.
Do not use [U] markers. Return only the article content, no preamble.
```

### 5.2 Call Claude API

Write the prompt to a temp file, then use the Claude CLI or Python SDK:

```bash
python3 -c "
import anthropic, sys, os
client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY', ''))
prompt = open(sys.argv[1]).read()
msg = client.messages.create(
    model='claude-opus-4-7',
    max_tokens=8000,
    messages=[{'role': 'user', 'content': prompt}]
)
print(msg.content[0].text)
" /tmp/content-planner/{brand_key}_{row_index}_prompt.txt \
> /tmp/content-planner/{brand_key}_{row_index}_optimised.txt
```

If API call fails: log [WARN], skip append_content, continue to next row.

---

## Phase 6 — Append Content to Google Doc (per row)

```bash
python3 SCRIPTS_DIR/gdocs_helper.py append_content \
  --doc-id "{new_doc_id}" \
  --type "{col_h}" \
  --original-file "/tmp/content-planner/{brand_key}_{row_index}_original.txt" \
  --optimised-file "/tmp/content-planner/{brand_key}_{row_index}_optimised.txt" \
  --heading "{col_k}"
```

The `--original-file` argument should be empty string (`""`) if no original was scraped.

The script:
- Appends a HEADING_1 "ORIGINAL" section with the raw scraped text (if available)
- Appends a HEADING_1 "OPTIMISED" section with the generated content
- For OPTIMIZE_ONLY workflows: converts `[U]...[/U]` markers to Docs underline formatting
- For creation workflows: no underlines applied

Log: "[brand] row {row_index} — Content appended to doc"

---

## Phase 7 — SE Ranking and GSC Data Pull

For each processed row, pull keyword search landscape data:

```bash
python3 SCRIPTS_DIR/sheets_helper.py pull_keyword_data \
  --keyword "{col_l}" \
  --website "{website_url}"
```

Returns: `position`, `clicks_28d`, `impressions_28d`.
If no data: use `"-"` for all fields. Never block on missing data.

Store all results in memory for Phase 8.

---

## Phase 8 — Analyst Email

Compile one email after all brands are processed.

### 8.1 Build summary JSON

Create `/tmp/content-planner/email_rows.json` containing an array of objects:
```json
[
  {
    "brand": "OIKOS",
    "heading": "Best High Protein Yogurt",
    "target_kw": "high protein yogurt",
    "nw_url": "",
    "doc_url": "https://docs.google.com/...",
    "position": "4",
    "clicks": "120",
    "impressions": "3400"
  }
]
```

### 8.2 Send email via Gmail

```bash
python3 SCRIPTS_DIR/email_helper.py send \
  /tmp/content-planner/email_rows.json \
  carla.klaasen@digitad.ca \
  "{MONTH_NAME} {YEAR}"
```

If send fails: log [WARN] and write summary to chat only.

---

## Phase 9 — Run Summary

Output to chat after completion:

```
Monthly Content Planner — {MONTH_NAME} {YEAR}
Brands processed:   N
Total rows scanned: N
Briefs created:     N
Rows skipped:       N (already had link or translation)
Content generated:  N
Scrape errors:      N
Email sent:         YES / NO / FAILED

Per brand:
  [brand] — N briefs
    [Heading] → [doc_url]
    Workflow: OPTIMIZE_ONLY / CREATE_WITH_CONTEXT / CREATE_ONLY
```

---

## Error Handling

Never stop the entire run due to a single brand or row failure.

| Scenario | Action |
|---|---|
| Brand file missing required logistical fields | Skip brand, log WARN |
| Production plan tab not found | Skip brand, log WARN |
| No eligible rows for brand | Log INFO, continue |
| Scrape failure or empty result | Skip ORIGINAL section, proceed with creation |
| No URL for optimization row | Skip scrape, generate from keyword/heading context only |
| Content generation failure | Log WARN FLAG, leave doc without content sections |
| Google Doc copy failure | Log FLAG, skip row |
| GSC data unavailable | Use "-" values |
| Email send failure | Log WARN, do not block completion |
| Mitacs EN template ID missing | Fall back to FR template, log WARN |

---

## Manual Trigger

Run for current month:
  `/monthly-content-planner`

Run for a past month (back-fill):
  `/monthly-content-planner month=April year=2026`

Run for specific brands only:
  `/monthly-content-planner brands=Oikos,Silk,ID,Mitacs`

Combined:
  `/monthly-content-planner month=May year=2026 brands=Oikos,Silk,ID,Mitacs`

---

## Schedule Registration

This skill runs on the first Monday of each month at 9:00 AM.
Cron expression: 0 9 * * 1#1

To check schedule status: `/schedule list`
To re-register: run `/schedule` and follow prompts
