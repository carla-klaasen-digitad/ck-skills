---
name: digitad-tech-recommendations
description: Produces Digitad client-facing technical recommendations Google Docs from SEO audit spreadsheets. Use when user mentions any Danone USA brand (Evian, Light+Fit, Danone North America, Oikos, International Delight, SToK, Too Good, Silk, Happy Family, Activia, Dannon, YoCrunch, Danimals, Dunkin Creamers, So Delicious, Follow Your Heart) alongside "technical recommendations", "dev team report", or a report type (Indexation, Canonical/404/301, Meta-tags, Structured Data, Performance, Images, Links, About Page).
allowed-tools: Read, Write, Edit
---

# Digitad Technical Recommendations Skill

Produces client-facing technical recommendations Google Docs for Danone USA brands from Digitad SEO audit spreadsheets. Reports are sent to the client's development team for implementation.

## Requirements

- Google OAuth2 credentials in `/Users/carlaklaasen/claude_code/.env`: `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_REFRESH_TOKEN`, `GOOGLE_TOKEN_URI`
- Scopes required: Google Docs API (documents), Google Sheets API (spreadsheets), Google Drive API (drive.file for creating docs)
- Reference write script: `/Users/carlaklaasen/claude_code/write_activia_doc.py`

## When This Skill Activates

- User provides a brand name and a list of issues to address
- User says "write the dev team report for [brand]"
- User references a report type from the production plan
- User references any Danone USA brand (Evian, Light+Fit, Danone North America, Oikos, International Delight, SToK, Too Good, Silk, Happy Family, Activia, Dannon, YoCrunch, Danimals, Dunkin Creamers, So Delicious, Follow Your Heart)

## Inputs Required

1. **Brand name** — used to look up the correct audit spreadsheet (see CLIENT-REGISTRY.md)
2. **Issue list** — the user provides a list of issue names to cover (e.g. "Sitemap.xml, Robots.txt, WordPress Admin Security, Canonical/404"). This is the primary input. If not provided, ask: "Which issues should this report cover?"
3. **Quarter** — Q1, Q2, Q3, or Q4. Derive from the current date if not stated (Jan–Mar = Q1, Apr–Jun = Q2, Jul–Sep = Q3, Oct–Dec = Q4). Confirm with user if ambiguous.
4. **Target Google Doc ID** — the doc to write to. If not provided, auto-create one (see Phase 1, step 4).
5. **Supplementary sheets** — linked in audit column Q (Sources). Do not ask upfront — request only when a specific row's source is needed and not yet available.

## Phase 1 — Identify Inputs

1. **Auto-load brand from CLIENT-REGISTRY.md the moment a brand name is mentioned.** Do not wait for the user to provide the spreadsheet URL — look it up immediately. If the brand is in the registry with a valid spreadsheet ID, proceed. If the registry shows TBD or the brand is missing, tell the user: "I don't have the audit spreadsheet for [Brand] — can you share the URL?"
2. **Accept the user's issue list as primary input.** The user will name the issues to cover (e.g. "Sitemap.xml, Robots.txt, WordPress Admin Access Security Issue, Redirection Plan: Canonical URLs & 404 Errors"). Map each issue name to the corresponding report type in REPORT-TYPES.md. If the user has not provided an issue list, ask: "Which issues should this report cover?"
3. **Confirm quarter.** Derive from the current date (Jan–Mar = Q1, Apr–Jun = Q2, Jul–Sep = Q3, Oct–Dec = Q4). State the derived quarter to the user and confirm before proceeding.
4. **Confirm target Google Doc ID.** If the user has not provided one, auto-create a new Google Doc:
   - Name: `[Brand] — Technical Recommendations — Q[N] [YYYY]` (e.g. "Dannon — Technical Recommendations — Q2 2026")
   - Parent folder: the brand's Output Folder ID from CLIENT-REGISTRY.md
   - Method: exchange refresh token for access token (see Phase 4 write method), then POST to `https://www.googleapis.com/drive/v3/files` with body `{"name": "[doc name]", "mimeType": "application/vnd.google-apps.document", "parents": ["[folderID]"]}`
   - Record the returned `id` as the target doc ID for all subsequent write steps.
   - After token exchange: if the exchange returns an error, surface "Google token exchange failed — verify GOOGLE_REFRESH_TOKEN in .env is current" and do not proceed.
5. Note any supplementary sheet URLs the user has already provided. Do not ask for supplementary sheets upfront — request them only when a specific row's column Q references a sheet you don't have.

## Phase 2 — Read Audit Data

1. Call the Sheets API to list sheet names and confirm the audit tab name (the file is always a Google Sheet even if the user says "doc"). Common names: "Detailed Technical Audit", "All Phases".
2. Read the audit tab header rows (A1:S5) to confirm exact column positions — do not assume the standard layout. Column positions vary across brands.
3. **For each issue in the user's list**, find the matching audit row: search Column F (Analyzed Element) for a case-insensitive partial match to the issue name. One issue may map to multiple rows (e.g. "Redirection Plan" covers Canonical Tags, 404 Errors, and Redirect Chains rows separately).
4. For each matched row, extract:
   - **Score Explanation column** (confirmed position from step 2) — primary source for the Problem section
   - **Sources column** (confirmed position from step 2; typically Col Q or Col R) — contains the links to include in the doc. Include all URLs from this cell as hyperlinks in the relevant section.
   - **How to correct column** (typically Col O or Col P) — primary source for the Fix section
5. If Score Explanation is blank for a row, fall back in order: Description column (Col G) → How to correct column → note the data gap in Phase 5.
6. For supplementary sheets: read A1:Z30 first to understand structure, then extend if needed.
7. Read in chunks of ~50 rows on large tabs to avoid token limits.

### Audit tab column layout (standard — always verify from header row)

Standard: A=blank, B=Status, C=Family, D=Category, E=Sub-Category, F=Analyzed Element, G=Description, H=Score, I=Score Explanation, J/K=Weight, L=Score (numeric), M=Priority, N=Who's in charge, O=How to correct, P=Comments, Q=Sources

Note: some audits (e.g. Dannon) use a different layout where Score Explanation is in Col L and Sources is in Col R. Always read the header row first.

### Shared tab structure (all brands)

🗂️ SUMMARY · 📊 Performances · Detailed Technical Audit (gid=1138767468) · Glossary · ⚙️ Sources · Schema Markup Implementation

## Phase 3 — Ask Clarifying Questions

Before writing, always ask:

1. **Scope** — which pages/issues are in scope? Are any findings being deferred to a separate report?
2. **Supplementary docs** — column Q references correction plans, page lists, etc. Ask for any not yet provided.
3. **Technical depth** — descriptive only, or include code/config examples?
4. **Cross-report references** — confirm what to include here vs. cross-reference to another report.

See REPORT-TYPES.md for report-type-specific clarifying questions.

## Phase 4 — Write the Document

### Document structure

1. **Title** — H1, first paragraph of the document
2. **Audit cross-reference** — second line (italic): `*Complete SEO and GEO Audit:*` — user will add the link
3. **H2 sections** — one per major issue area; structure varies by report type (see REPORT-TYPES.md)
4. Each section uses a three-part structure (SR-18): **Problem:** what the issue is | **Impact:** why it matters for SEO/performance | **Fix:** numbered action list, or italic placeholder if the fix is a linked document. Only the label word is bolded. **Fix:** replaces any separate Recommended Actions list.

Before writing, run through CHECKS.md.

### Write method — Google Docs API via Python

Use the Google Docs API directly with OAuth2 credentials from `/Users/carlaklaasen/claude_code/.env`. The MCP tool `replaceDocumentWithMarkdown` is not available in this environment.

**Steps:**
1. Load `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_REFRESH_TOKEN`, `GOOGLE_TOKEN_URI` from `.env`
2. Exchange refresh token for an access token via POST to `GOOGLE_TOKEN_URI`
3. GET `https://docs.googleapis.com/v1/documents/{DOC_ID}` to find current `endIndex`
4. DELETE content from index 1 to `endIndex - 1` via `deleteContentRange` batchUpdate
5. INSERT all paragraph text at index 1 in a single `insertText` request; track each paragraph's start/end offset
6. Apply formatting via subsequent `batchUpdate` requests: `updateParagraphStyle` for heading levels (HEADING_1, HEADING_2, HEADING_3, NORMAL_TEXT), `updateTextStyle` for bold labels and italic/linked lines, `createParagraphBullets` for Fix numbered lists (preset: `NUMBERED_DECIMAL_ALPHA_ROMAN`) and guideline bullets (preset: `BULLET_DISC_CIRCLE_SQUARE`)
7. Batch format requests in groups of 50

A working reference script: `/Users/carlaklaasen/claude_code/write_activia_doc.py`

### Mandatory style rules (full list in STYLE-RULES.md)

- **No links** in Light+Fit and Happy Family reports — user adds manually. For other brands, keep links unless told otherwise. Confirm per project.
- **No Expected Outcome sections** — never include; always removed by user.
- **Audit cross-reference at top** — `*Complete SEO and GEO Audit:*` as first italic line after title.
- **Cross-reference other reports** with italic placeholder: `*See [Report Name] for details.*` — do not re-explain content.
- **Short overviews** — lead with the key metric/finding; skip preamble.
- **Short recommended actions** — 2–4 items maximum; highest-impact only.
- **"the website"** — never use the domain name in prose (e.g. "pages on the website" not "pages on lightandfit.com").
- **Examples in italics** — e.g. `*https://www.lightandfit.com/nonfat-yogurt/*`
- **Absolute URLs** — always cite full URLs in examples, not relative paths.
- **Tightly scoped** — if a finding belongs in another report, remove it and cross-reference instead.
- **Fewer reference links per section** — pick the most directly actionable source; do not over-reference.
- **Robots.txt additions** — bold only the NEW disallow rules, not existing ones.
- **Under 3 em-dashes per document** — replace excess with semicolons, colons, parentheses, or restructuring. (SR-16)
- **Sitemap Maintenance Guidelines** — every section covering sitemap or indexation must include a "Sitemap Maintenance Guidelines" bullet list after Fix items. Cover: URL eligibility (200 + self-referencing canonical + no noindex), keeping sitemap current, removing 404/redirected URLs promptly, https + trailing slash consistency, re-submitting to GSC after structural changes. This is a unique element — do not reformat into Problem/Impact/Fix. (SR-17)
- **No full URL lists** — never list individual affected URLs in Fix. Describe the pattern, state the count, and provide an italic placeholder for the spreadsheet link. (SR-19)
- **No text after a hyperlink on the same line** — always make the hyperlink the last element on its line. (SR-15)

## Phase 5 — Report Output

After writing:
1. Report the section structure to the user.
2. Note any data gaps (supplementary sheets not provided, missing audit data).
3. Note any cross-report placeholders left for the user to fill in.

## Phase 6 — Update Production Plan

After the doc is written and confirmed:
1. Open the production plan: spreadsheet ID `1o526Qv4UzP_Qfe-cjrfvcA7jRUi6zUtd9Ecp2WPMIhQ`, tab `Technical Recommendations ` (note: trailing space in tab name — quote it in range notation).
2. **Always do a fresh row lookup — never cache row positions.** Read Column A from row 1 to the end of the sheet to find the brand. Brands span multiple rows; locate the first row where Col A is non-empty and matches the brand name (case-insensitive). Row positions can change as brands are added or removed.
3. Write the Google Doc URL to the quarter column of the brand's first row:
   - Q2 → Column G
   - Q3 → Column I
   - Q4 → Column K
4. Use the Sheets API `batchUpdate` with `valueInputOption: "RAW"`.
5. Confirm the write to the user: "Production plan updated — Q[N] link written to [Brand] row."

## Supporting Files

- **REPORT-TYPES.md** — section structure, audit rows, clarifying questions, and worked examples for each of the 8 report types
- **CLIENT-REGISTRY.md** — audit spreadsheet IDs for all active Danone USA brands
- **STYLE-RULES.md** — complete stylistic rules with rationale
- **CHECKS.md** — pre-write checklist
