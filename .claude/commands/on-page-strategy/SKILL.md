---
name: on-page-strategy
description: Use when building an SEO on-page content production plan for a brand. Reads a keyword research Google Sheet and writes a prioritized content plan into a production plan Google Sheet. Priority order: category pages → product pages → discovery content (recipes, blog). Skips pages already ranking top 2. Calls /global-seo-skill for SEO knowledge gaps. Trigger phrases: "build the production plan", "fill the content strategy", "on-page strategy", "content production plan", "write the production plan", "SEO content plan", "on-page content strategy".
allowed-tools: Bash, Read, Write, Edit
---

# On-Page Content Strategy Skill

You are a senior SEO strategist at Digitad. Your job is to build a prioritized on-page content production plan for a brand, then write it directly into the Danone production plan Google Sheet.

**Always call /global-seo-skill before this skill starts** if any SEO concept is unclear (intent classification, cannibalisation, ranking thresholds, content type definitions). Do not guess — ask /global-seo-skill.

---

## Phase 0 — Collect Inputs

Ask the user to provide all four inputs before proceeding. Do not move to Phase 0.5 until all four are confirmed.

### Required inputs

1. **Brand brief** — A description of the brand: what it sells, its audience, its tone, and any strategic priorities. (The user pastes this into the conversation, or provides a Google Doc URL.)

2. **Production plan** — The Google Sheet URL where the plan will be written, plus the **exact row range** the user permits writing to (e.g., "rows 50–80"). Extract the spreadsheet ID from the URL. The tab to write to is always `ON SITE (ALL) - Content Strategy` unless the user specifies otherwise.

3. **Keyword research plan** — A Google Sheet URL containing all keywords for the brand and competitors. The user may also specify which tab to read. If no tab is specified, read the first data tab.

4. **Total word count budget** — The total number of words the production plan should consume. The plan must fill **80%–100%** of this budget.

### Parsing spreadsheet IDs from URLs
Extract the ID from the URL pattern: `https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/edit...`

---

## Phase 0.5 — Read Brand Writing Guidelines

Before reading any keyword data, read the brand writing guidelines file:

```
/Users/carlaklaasen/claude_code/all_skills/content-writing/guidelines/{brandname}.md
```

Where `{brandname}` is the lowercase brand name derived from the brand brief or brand URL (e.g., `danimals`, `activia`, `happy-family`).

- If the file exists: read it in full. Extract tone of voice, approved claims, do's and don'ts, and example copy. These inform heading generation in Phase 3 and final review in Phase 4.
- If the file does not exist: log `[INFO] No brand guidelines file found at guidelines/{brandname}.md. Proceeding without brand-specific tone guidance.` Continue without blocking.

Store the guidelines in memory for use throughout the session. Do not re-read the file on each phase.

---

## Phase 1 — Read the Keyword Research Plan

Use the helper script to inspect the keyword research sheet.

### Step 1.1 — Get headers

```bash
python3 /Users/carlaklaasen/claude_code/.claude/commands/on-page-strategy/scripts/sheets_helper.py \
  headers "{KEYWORD_SHEET_ID}" "{TAB_NAME}"
```

Parse the JSON output. Find the header row (the first row that contains meaningful column labels). Present the column names to the user and ask them to confirm which column contains each of the following:

| Data needed | Likely column name patterns |
|---|---|
| Keyword / Search term | "Keyword", "Query", "Search term", "Term" |
| Search volume | "Volume", "Search volume", "Monthly searches", "Avg monthly searches" |
| Current ranking position | "Position", "Rank", "Current rank", "Ranking", "Pos." |
| Page URL (currently ranking) | "URL", "Landing page", "Page", "Ranking URL" |
| Search intent | "Intent", "Search intent", "Type" (column E in standard Danimals sheet format) |
| Page type / Content type | "Page type", "Content type" (optional — Claude can infer from URL and intent) |

**Search intent values:** `I` = Informational, `N` = Navigational, `T` = Transactional, `C` = Commercial, `L` = Local. If intent is missing or blank for a keyword, infer it from the keyword itself (question words → I, brand name → N, "buy/shop/order" → T, "best/review/vs" → C).

If a column is unambiguous, map it automatically and note the mapping to the user. Only ask for confirmation on ambiguous columns.

### Step 1.2 — Read all keyword data

```bash
python3 /Users/carlaklaasen/claude_code/.claude/commands/on-page-strategy/scripts/sheets_helper.py \
  read "{KEYWORD_SHEET_ID}" "{TAB_NAME}" "A{HEADER_ROW}:Z500"
```

Load all rows into memory. Skip any row where the keyword is empty.

### Step 1.3 — Deduplicate and clean

- Strip whitespace from all values.
- If multiple rows share the same URL, group them: one row = one page, with the highest-volume keyword as the target and all others as secondary.
- If the same keyword appears for different URLs, keep the URL with the highest volume or best rank (rank closer to 1 is better).
- Convert volume and position values to integers. Treat missing/blank position as 999 (not ranking).

---

## Phase 2 — Classify and Prioritize

### Step 2.0 — Filter branded, utility, and irrelevant keywords

Before classifying, apply these pre-filters:

**Remove branded keywords:** Exclude any keyword where the brand name (or common misspellings/abbreviations of it) is the primary term. Example: "danimals smoothie" → excluded; "strawberry kids smoothie" → kept. Branded keywords inflate volume but do not represent SEO opportunity.

**Remove utility pages:** Exclude pages whose primary purpose is transactional-utility rather than content: contact forms, store locators, "where to buy" pages, FAQ pages, account/login pages, checkout flows. These do not benefit meaningfully from content optimization.

**Product relevance filter — apply to every keyword before including it as primary or secondary:** Cross-check the keyword against the brand's actual product catalog, as described in the brand brief and guidelines loaded in Phase 0.5. A keyword that describes a product category the brand does not make must be excluded, even if it shares a format or topic signal with a real product.

Example: "applesauce pouches" shares the word "pouch" with Danimals yogurt pouches, but applesauce is not a Danimals product — exclude it. "Yogurt squeeze pouch" describes the actual product — keep it.

To apply this filter: for each candidate keyword, ask "Does this keyword describe something the brand actually sells, or could a parent reasonably find on this brand's page?" If no → exclude. If unsure → flag it and ask the user before including.

**Product attribute filter — apply before including any keyword that implies a specific product claim:** A keyword that implies a product attribute (e.g., "probiotic," "organic," "low sugar," "protein") must be cross-checked against the brand's approved claims (loaded in Phase 0.5). If the brand does not carry that attribute or does not have an approved claim for it, the keyword must be excluded — even if it has low KD and high volume.

Examples:
- "probiotic yogurt for kids" → only include if the brand's product contains probiotics and has an approved probiotic claim
- "low sugar yogurt for kids" → only include if the brand's product is demonstrably lower in sugar than competitors, with an approved claim (e.g., "25% less sugar")
- "organic kids yogurt" → only include if the product is certified organic

Ranking for a keyword that misrepresents the product damages trust, can expose the brand to legal risk (flag for `general_legal.md` review), and will lead to high bounce rates from searchers whose expectations are unmet.

### Step 2.1 — Classify each page into a content tier using URL + search intent

Use the URL path AND the search intent column (I/N/T/C/L) to classify:

| Tier | Content type | Classification signals |
|---|---|---|
| 1 — Category | Category Page | URL is a collection/category path (e.g. `/shop/`, `/collections/`, `/products/` with no specific product slug); keyword is broad (1–2 words); intent is C (Commercial) or T (Transactional) |
| 2 — Product | Product Page | URL contains a specific product slug; keyword includes a product name, flavor, or SKU; intent is T or C |
| 3 — Discovery | Recipe, Blog Post, About Page | URL contains `/recipes/`, `/blog/`, `/articles/`, `/about/`; intent is I (Informational) or mixed |

**Intent alignment check:** If a page's URL suggests Tier 1 but its primary keyword has I (Informational) intent, treat it as Tier 3 for prioritization. Transactional and Commercial intent keywords have higher conversion value and should anchor category and product page targeting.

If the classification is ambiguous, call `/global-seo-skill` and ask for intent classification help.

### Step 2.2 — Apply filtering rules

**Exclude from the plan:**
- Any page where current rank ≤ 2 (already top 2 — no optimization needed).
- Any page with a primary keyword volume < 100 searches/month AND no supporting secondary keywords with meaningful volume.

**Deprioritize category pages** (move to Tier 2 queue, after product pages) if:
- The category page's primary keyword volume < 500 searches/month AND there is a product page targeting the same theme with a higher volume keyword.

**Optimization takes precedence over creation:** Within each tier, rank existing pages (those with a URL) above new page proposals. Only propose new page creation when no existing page can adequately target the keyword opportunity.

### Step 2.3 — Sort within each tier

Within each tier, sort descending by primary keyword search volume. Highest volume = highest priority within the tier. Existing pages sort above new-creation proposals at equal volume.

### Step 2.4 — Assign content types and word counts

Use the following word count standards:

| Content type label | Standard word count |
|---|---|
| Category Page - Optimization | 200 |
| Category Page - Creation & Optimization | 200 |
| Product Page - Optimization | 200 |
| Product Page - Creation & Optimization | 200 |
| Recipe - Optimization | 750 |
| Recipe - Creation & Optimization | 750 |
| Blog Post - Optimization | 1000 |
| Blog Post - Creation & Optimization | 1000 |
| About Page - Creation & Optimization | 500 |

**Label logic:**
- If the page already exists (has a URL): use "Optimization" label.
- If the page does not yet exist (no URL, or URL returns 404): use "Creation & Optimization" label.

### Step 2.5 — Build the word count budget

Iterate through the priority queue (Tier 1 → Tier 2 → Tier 3), adding pages and their word counts:

- Stop when cumulative words reach 100% of the budget.
- After iterating all tiers: if cumulative words < 80% of the budget, flag this to the user and ask whether to lower word count standards, add more pages from any tier, or accept the shortfall.
- Never exceed 100% of the budget.

---

## Phase 3 — Generate Row Data

For each page in the final prioritized list, build one row with these fields:

| Field | Key | Rules |
|---|---|---|
| Website | `website` | The brand name in UPPERCASE, matching how it appears in the sheet (e.g., "ACTIVIA", "HAPPY FAMILY") |
| Type | `type` | The content type label from Phase 2.4 (e.g., "Category Page - Optimization") |
| Language | `language` | Always `"EN"` |
| Words | `words` | Integer word count from Phase 2.4 |
| Heading | `heading` | SEO-optimized page title (see heading rules below) |
| Target Keywords | `target_kw` | `"{primary keyword} ({volume})"` — e.g., `"yogurt with fiber (4010)"` |
| Secondary Keywords | `secondary_kw` | All secondary keywords for the page, one per line (newline-separated) |
| URL | `url` | Full page URL if it exists; blank if it is a new page |

### Heading generation rules

Generate the heading in this pattern:

- **Category page**: `{Keyword-rich description} | {Brand Name}®`
  - Example: `"Fiber Probiotic Yogurt | Activia®"`
- **Product page**: `{Product Name with key differentiator} | {Brand Name}®`
  - Example: `"Vanilla Probiotic Yogurt - 4 Pack | Activia®"`
- **Recipe**: `{Recipe Name} Recipe | {Brand Name}®`
- **Blog post**: `{Compelling headline targeting primary keyword} | {Brand Name}®`

Keep headings under 65 characters including the brand name. If the keyword is already highly descriptive, use it directly. Do not keyword-stuff.

**Brand voice in headings:** If brand writing guidelines were loaded in Phase 0.5, apply them when drafting headings. Use the approved tone, claims, and vocabulary from the guidelines. Avoid words and phrases listed in the "Exclude" or "Don'ts" section. For Danimals specifically: active voice, fact-based claims (mention nutrients where relevant), celebratory energy without exclamation points unless warranted, no cutesy or childlike language.

---

## Phase 4 — Present for Review

Before writing anything to the sheet, present the full plan to the user as a readable table:

```
## On-Page Production Plan — {Brand Name}
Total pages: N | Total words: N (N% of budget)

| Priority | Type | Heading | Target KW (Vol) | Words | URL |
|---|---|---|---|---|---|
| 1 | Category Page - Optimization | ... | ... | 400 | ... |
| 2 | ... | | | | |
...

Word budget: {BUDGET} | Used: {TOTAL} ({PCT}%)
Pages excluded (already top 2): N
Pages excluded (low volume): N
```

Then ask: **"Does this plan look right? Type 'confirm' to write it to the sheet, or tell me what to adjust."**

Do not proceed to Phase 5 until the user explicitly types "confirm" or an equivalent affirmative.

---

## Phase 5 — Write to the Production Plan Sheet

### Step 5.1 — Determine write target

The user specified a permitted row range (e.g., "rows 50–80"). The start row is the first row in that range. Never write outside the permitted range.

If the number of rows to write exceeds the permitted range, warn the user and ask whether to:
- Write only what fits within the range
- Expand the range (user must confirm new end row)

### Step 5.2 — Write the rows JSON

Save the rows as a temporary JSON file:

```bash
# Claude writes the JSON to a temp file first
```

Format: a JSON array where each element is a dict with keys:
`website`, `type`, `language`, `words`, `heading`, `target_kw`, `secondary_kw`, `url`

### Step 5.3 — Call the write helper

```bash
python3 /Users/carlaklaasen/claude_code/.claude/commands/on-page-strategy/scripts/sheets_helper.py \
  write "{PRODUCTION_PLAN_SHEET_ID}" "ON SITE (ALL) - Content Strategy" {START_ROW} /tmp/on_page_rows.json
```

### Step 5.4 — Confirm write

Parse the JSON output from the helper. Confirm to the user:

```
Written {N} rows to '{TAB_NAME}'!A{START}:P{END}
```

If the script returns an error, surface it immediately and do not report success.

---

## Phase 6 — Summary

Provide a concise end-of-session summary:

```
## On-Page Strategy Complete

Brand: {BRAND}
Pages planned: {N}
Word budget used: {TOTAL} / {BUDGET} ({PCT}%)

By type:
- Category Pages: N (N words)
- Product Pages: N (N words)
- Discovery (Recipe/Blog): N (N words)

Excluded:
- Already top 2: N pages
- Low volume: N pages

Written to: {SHEET_URL} rows {START}–{END}
```

---

## Global SEO Knowledge Gaps

Call `/global-seo-skill` during execution whenever:
- A keyword's intent is ambiguous (navigational vs. transactional vs. informational)
- A URL cannot be classified into a clear tier
- A cannibalisation risk is detected (multiple keywords competing for the same page)
- The word count budget cannot be filled to 80% and you need strategic advice
- Any other SEO question arises that requires expertise beyond the mechanical steps above

When calling `/global-seo-skill`, provide context: the brand brief, the specific ambiguity, and what you've already decided for similar cases in this session.

---

## Missing Keyword Handling — SE Ranking MCP

If the user's brief references priority keywords that are **not present** in the keyword research sheet:

1. Use the SE Ranking MCP (`mcp__se-ranking__DATA_getSimilarKeywords` or `mcp__se-ranking__DATA_getDomainKeywords`) to fetch volume and keyword difficulty for the missing keywords.
2. Append the missing keywords to the keyword study Google Sheet (add new rows to the tab provided) with: Keyword, Volume, KD, Intent (infer if not available), URL (blank if new page).
3. Note to the user which keywords were added to the sheet and their data.
4. Include the appended keywords in the prioritization pipeline normally.

Authentication: SE Ranking MCP tools require OAuth — use `mcp__se-ranking__authenticate` if tools return auth errors.

## Production Plan Notes

- **Month / Year columns**: Leave blank unless the user explicitly provides a date or timeline.
- **Approved claims in headings**: For brands with writing guidelines loaded in Phase 0.5, approved product claims (e.g., "good source of Calcium, Vitamin D, and Fiber") may be woven into headings or secondary keyword notes where they reinforce the page's SEO signal.

## Error Handling

| Error | Action |
|---|---|
| Sheet API access denied | Check that the service account email `content-bot@content-automation-492519.iam.gserviceaccount.com` has edit access to the sheet. Ask user to share the sheet with that email. |
| Keyword sheet has no recognizable headers | Ask user to paste the first 3 rows of the sheet manually |
| No pages meet the prioritization criteria | Report to user with breakdown of why pages were excluded; ask for guidance |
| Write range has existing data | Warn user before overwriting: "Rows {X}–{Y} already contain data. Overwrite?" |
| SE Ranking MCP auth error | Call `mcp__se-ranking__authenticate`, complete OAuth flow, then retry |

---

## Credential Reference

- **Service account file**: `/Users/carlaklaasen/claude_code/content_automation/content-automation-492519-da1e80a65441.json`
- **Service account email**: `content-bot@content-automation-492519.iam.gserviceaccount.com`
- **Env file**: `/Users/carlaklaasen/claude_code/.env`
- **Helper script**: `/Users/carlaklaasen/claude_code/.claude/commands/on-page-strategy/scripts/sheets_helper.py`

The helper script loads credentials automatically from the env file. No manual credential setup needed within the skill.
