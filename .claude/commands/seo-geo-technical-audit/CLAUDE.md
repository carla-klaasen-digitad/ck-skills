# CLAUDE.md — seo-geo-technical-audit
# Auto-loaded by Claude Code at every session start.
# Do not delete or move. Do not paste these rules manually — they are already active.

---

## SESSION SAFETY RULES — APPLY BEFORE ANY AUDIT WORK

These rules are permanent and apply to every session, every audit, every phase. They exist because the most common audit failures — context crashes, lost files, invisible agent failures — are all caused by violating them. No exception.

**Rule S1 — Write tool verification**: Before any audit work begins, write a test file: `Outputs/test-write-check.md` with the single word OK. Also write a test CSV: `Outputs/test-write-check.csv`. Confirm both were written successfully before proceeding. If either fails, stop immediately and resolve write permissions. Do not continue.

`init_session.py` and `audit-session-config.json` are required when: (a) workbook format is Google Sheet, or (b) any API-fetched data source is needed. If workbook format is local .xlsx and all sources are manual, `init_session.py` can be skipped. When Google Sheet is chosen in Step 3, validate Drive access immediately via `python3 scripts/init_session.py --validate-drive-only` before Phase 1 begins.

**Rule S2 — Write before print**: After scoring each phase, write the full scoring table to a .md file in Outputs/ before printing anything to chat. Never print phase output to the terminal before the file is saved to disk. Only print out a phase summary. 

**Rule S3 — One phase at a time**: Never batch multiple phases in a single prompt. Score one phase, write it to disk, compact, then move to the next. This is mandatory regardless of which efficiency option was selected at session start.

**Rule S4 — Never background file-writing tasks**: Any task that produces a file runs in the foreground, one file at a time, with explicit confirmation between each file. Background agents are permitted only for read-only tasks (file parsing, competitor spot-checks) or fetching a live url. 

**Rule S5 — Proactive /compact after every phase**: Run /compact after every phase completes. Never wait for a context limit warning before compacting. 

**Rule S7 — session-state.md before /compact (hard dependency)**: Write `Outputs/session-state.md` before every /compact, no exceptions. Do not run /compact without writing this file first. session-state.md captures PROMPT USER answers, W-ADJ adjustments, DATA MISSING declarations, COMP tags, and Production Plan status — these are permanently lost after /compact if not saved. This rule applies after every phase, including Phase 6 and after the Executive Summary. The full L1 sequence is: write phase .md → run L1 checks → update Production Plan → write session-state.md → **watchdog Phase 4 + Phase 5 (if active)** → /compact.

If skill-watchdog is active this session: immediately after writing session-state.md, and before calling /compact, run the watchdog's Phase 4 end-of-session checkpoint summary and Phase 5 registry update. Writing session-state.md is the pre-/compact signal — the watchdog must close before context is cleared. Do not call /compact until the watchdog Phase 5 registry write is confirmed. 

**Rule S8 — Never write HTML files individually**: HTML client report files must never be written individually or manually. Always use `scripts/generate_html.py` from the skill scripts directory. The script reads `workbook_data.json` and generates all 9 files in one pass using the correct Tailwind design system. Writing HTML files individually bypasses the design system, produces inconsistent output, ignores the client logo setup, and requires an unacceptable number of tool calls.

**Rule S6 — File naming conventions**: Two naming patterns apply — use the correct one per file type:
- **Main deliverables** (phase .md files, workbook, executive summary, session log, activity log): `[Client Name] - [Description] - [Month Year]` — e.g. `YoCrunch - SEO GEO Audit - April 2026` (no file extension for Google Sheet display names in Drive)
- **Tertiary export files** (all CSVs, .txt reports, conditional outputs): `[CLIENT_NAME]-[report-name].[ext]` — CLIENT_NAME in ALL CAPS, report name in lowercase-hyphenated — e.g. `YOCRUNCH-title-tag-issues.csv`, `YOCRUNCH-disavow.txt`, `YOCRUNCH-robots-txt-recommendation.txt`

Confirm the exact filename with the user before writing every output file. Never write a file and name it without asking.

**Rule S9 — API failure handling**: If any API call during `fetch_data.py` or `init_session.py` returns an error or timeout, declare DATA MISSING for the affected element immediately — do not silently skip or substitute a default value. Record the failed source in `session-state.md` under Data Availability with the error message. Do not advance to the affected phase until either the data is fetched successfully or DATA MISSING is explicitly confirmed by the user.

---

## TOKEN EFFICIENCY RULES — READ FIRST, APPLY ALWAYS

1. Tables only — all audit output is structured table rows, written in complete sentences
2. No repeated definitions — element descriptions live in REFERENCE-1.md and REFERENCE-2.md, never re-stated in output
3. Phase gates are mandatory — always stop and confirm before advancing to next phase
4. All elements must appear — every element in the phase must appear in the output table, either scored or marked DATA MISSING. Silent omission is not permitted.
5. Comment format: specific finding — impact — solution
6. Competitor tags: inline `[COMP: competitor does X better]` — rolled up at session end
7. W-ADJ inline: when a weight adjustment applies to a specific element row, add `[W-ADJ: reason]` in that row's Comments cell
8. Phase count accuracy: phase-end summary must account for every element (scored + DATA MISSING + Not Applicable = total elements in phase)
9. Confidence level: always state audit completeness % before each phase output
10. Ask before generating — confirm "Ready for Phase N?" before proceeding
11. All URLs must be absolute — every URL in every output file must begin with https:// and include the full domain. Never use relative paths.
12. No emoji anywhere in output — use text labels only.
13. Every element row must be fully self-contained — never write "same as above", "see above", or any cross-reference within a table. Write the complete problem statement for every element, every time.
14. Write in full sentences — no fragments. Score Explanation and How to Correct fields must contain complete sentences with subject, verb, and specific detail.
15. Never write a pipe character ( | ) inside cell content in phase .md scoring tables. Use an em dash ( — ) instead.  This applies to quoted page title examples, URL formats, and any other cell content.
16. Show output preview before generating — before beginning any phase or output file, state one sentence describing what is about to be produced. Do not reprint corrected content line-by-line after making a change — confirm only what changed.
17. PROMPT USER questions must be asked verbatim — copy the exact question from REFERENCE-1.md or REFERENCE-2.md without paraphrasing. Do not approximate or summarise PROMPT USER questions. Paraphrased questions produce incomplete or mismatched answers and cause elements to be mis-scored.
18. Pre-write scan — before writing any phase .md file, scan every Sources and Comments cell for element codes (T01, G09, etc.) and erase them. These are the two highest-risk columns for element code leakage. Replace any element code cross-reference with descriptive plain language (e.g. "the speed element scored Weak" not "T14 scored Weak").
19. No URL lists in Score Explanation — never list individual URLs in the Score Explanation cell. State the count and finding only, then refer to the export (e.g. "24 URLs returning 404 errors were identified — full breakdown is in the 404 Errors export."). URL lists always belong in the export file, never in the cell. This applies to Score Explanation, How to Correct, and Comments — any cell where individual URL lists would clutter the column.

---

## MANDATORY PROCESS RULES

**One phase at a time**: Score one phase, write it to disk, run /compact, then move to the next. Never score two phases in a single prompt.

**Write before print**: The phase .md file must be written to disk before any output is printed to chat. This is Rule S2 — it applies every phase, every time.

**No background file writing**: Any task that produces a file runs in the foreground with explicit confirmation. Background agents for file-writing tasks are prohibited.

**No column format override**: Do not specify column formats or column structures in the opening prompt. The skill defines all schemas — FORMS-EXPORTS-MANDATORY.md, FORMS-EXPORTS-CONDITIONAL.md, FORMS-INTERNAL.md, and OUTPUTS-WORKBOOK.md are authoritative. An opening prompt that overrides column schemas silently degrades all output files.

**Phase element counts — compaction-proof reference**: Use these to verify phase-end summaries after /compact. Scored + DATA MISSING + Not Applicable must equal the total for that phase.

| Phase | Family | Element count |
|---|---|---|
| Phase 1 | Technical | 27 (T01–T27) |
| Phase 2 | User Experience | 14 (U01–U14) |
| Phase 3 | Tools & Configuration | 10 (C01–C11; C08 removed — moved to T27) |
| Phase 4 | On-Site SEO | 25 (O01–O26; O09 removed — moved to G36) |
| Phase 5 | Off-Site | 11 (F01–F11) |
| Phase 6 | GEO / AI Visibility | 36 (G01–G03, G05–G37; G04 removed) |
| **Total** | | **123** |

**Phase 6 scoring methodology — compaction-proof reference**: Phase 6 uses the same score labels and weight scale as all other phases. Score labels: Not Present (1) | Weak (2) | Medium (3) | High (4) | Excellent (5). Weight scale: 2.5 = Secondary | 5 = Standard | 7.5 = Important | 10 = Critical. Priority Score per row = Score × Weight (identical formula to all phases). After scoring all Phase 6 elements, calculate and report the Phase GEO Score: sum(Score × Weight) / sum(5 × Weight) × 100. This normalised percentage is Phase 6 specific and is in addition to the standard per-row Priority Score. Importance Tier labels: 10 = Critical | 7.5 = Important | 5 = Standard | 2.5 = Secondary.

**Phase scoring table column format — compaction-proof reference**: Every phase .md scoring table must use this exact 17-column header. This rule survives /compact. Do not deviate. Do not reorder. Do not add or remove columns.

`| Status | Family | Category | Sub-Category | Analyzed Element | Description | Score | Weight/Importance (Numeric) | Importance Tier | Priority Score | Priority | Who's in charge? | Score Explanation | Data Analyzed | How to correct? | Comments | Sources |`

Column position index (0-based): 0=Status · 1=Family · 2=Category · 3=Sub-Category · 4=Analyzed Element · 5=Description · 6=Score · 7=Weight/Importance (Numeric) · 8=Importance Tier · 9=Priority Score · 10=Priority · 11=Who's in charge? · 12=Score Explanation · 13=Data Analyzed · 14=How to correct? · 15=Comments · 16=Sources

**Phase .md (17 cols) vs Google Sheet (19 cols)**: Phase .md files always use the 17-column format above. The Google Sheet output uses 19 columns (A–S): A=blank spacer, then B–R map to the 17 .md columns with Score Explanation reordered to column L and Data Analyzed included as column O, and S=Comments for Claude (always empty from the script — user-filled post-delivery). extract_data.py and generate_gsheet.py handle this remapping automatically. Never add a "Comments for Claude" column to phase .md files.

Status values — allowed values only (use these exact strings — no other values are valid):
- **Issue Found** — element has a problem that requires action (HIGH or MEDIUM priority)
- **Passing** — element meets standard, no action needed (LOW or MONITOR priority)
- **Opportunity** — element is functional but has clear room for improvement
- **Data Missing** — required source data was not provided (leave Priority blank)
- **Not Applicable** — element does not apply to this site type (leave Priority blank)
- **Manual Verification Required** — a definitive score cannot be assigned without additional access

Do not use "Complete," "Done," "OK," "Pass," "Fail," or any other value. The validator will reject all non-listed values.

**Two-script workbook pipeline**: Workbook generation requires the two-script pipeline. Run `extract_data.py` to parse all phase .md files and write `workbook_data.json`, then run `generate_gsheet.py` to read the JSON and create the Google Sheet in Drive. `generate_workbook.py` (.xlsx) is retained as a local backup only — use it only when Google Drive access is unavailable. Do not hardcode audit row data as Python string literals in a generation script — this approach fails at 50+ rows due to context exhaustion.

**Proactive New Report Rule**: During scoring and file generation, stop and ask the user before creating any additional output file triggered by these conditions:
- A "How to Correct" field contains more than 2 URLs → ask before splitting into a separate export
- Sitemap changes are identified → ask before writing a sitemap-delta.csv
- robots.txt changes are needed → ask before writing a robots-txt-recommendation.txt
- Toxic backlinks warrant disavowal → ask before writing a disavow.txt
- Phase 4 scoring reveals both internal and external linking issues → ask whether to generate both reports
- Word count data is available → ask before generating a word-count-report.csv

Do not wait until the session close gate. Raise the question at the point the condition is met, then continue immediately after the user responds.

**GSC always takes precedence over Screaming Frog**: For all elements that can be scored using both GSC Coverage data and Screaming Frog crawl data — specifically indexation errors (T01), 404 errors (T06), redirect chains (T07), and canonical tags (T05) — GSC Coverage is the primary data source. Screaming Frog is supplementary. SF only discovers URLs reachable from the current internal link graph; GSC discovers URLs from all sources (external backlinks, historical visits, old sitemaps, prior crawls). When the two conflict, GSC wins. Always re-evaluate any SF-based score when GSC data is provided later. If an element was scored from SF alone and GSC data arrives mid-audit, the element must be rescored from GSC first.

**GSC Coverage — full report required at Phase 0**: In Phase 0 Step 4, the GSC data source request must explicitly ask for the FULL GSC Coverage report download (all discovered URLs, not just submitted URL inspection). The full Coverage report includes URL categories: Not found (404), Page with redirect, Crawled — currently not indexed, Duplicate without user-selected canonical, Duplicate — Google chose different canonical, Excluded by noindex, Alternate page with proper canonical tag, and Blocked due to unauthorized request. This full report is required for accurate T01, T06, T07, and T05 scoring. Failure to request it at Phase 0 is a data gap that causes under-scoring of indexation and redirect elements. Add to the Phase 0 data source table: "GSC Coverage — full report | gsc-coverage-full.csv | T01, T05, T06, T07 | Manual only."

**Neutral language rule — no automated-audit language**: Never write "the user confirmed," "user-provided," "user said," or any language that reveals the audit involved a chat interaction. Replace all such constructions with neutral verification language: "verified," "confirmed by site owner," "manually verified," or state the finding as fact without attribution. This applies to every text field in every output file — scoring tables, CSVs, executive summary, and session log.

**Contradiction detection rule — hard stop**: When scoring any phase, if you encounter data or a finding that directly contradicts a PROMPT USER answer recorded in an earlier phase, stop immediately before scoring the affected element. Present the contradiction in chat:

```
CONTRADICTION DETECTED — [Element name]

Earlier answer ([Phase N], [element name]): [what the earlier answer stated]
Current data shows: [what this phase's data indicates]

These cannot both be correct. Please confirm which is accurate before I continue:
- [ ] Earlier answer is correct — current data is misleading or context-specific
- [ ] Current data is correct — earlier answer was incomplete or wrong
- [ ] Both are true in different contexts — please explain
```

Do not score the affected element until the user resolves the contradiction. Once resolved:
1. Record the outcome in session-state.md under a "Contradictions resolved" section.
2. If the earlier phase score needs updating based on the resolution, open the relevant phase .md file and correct it before continuing.
3. Note the contradiction and resolution in the Comments column of the current element.

This rule applies across all six phases. The most common pattern is a Phase 1 PROMPT USER answer contradicted by Phase 4 or Phase 6 data (example: user said "no rating system" in Phase 1, but Phase 4 discovers an active third-party review widget).

**Sources column rule — deliverables and verifiable references only**: The Sources column must contain only: (1) client-facing deliverable files generated during the audit (e.g. ACTIVIA-title-tag-issues.csv) with their Google Drive links in the format "FILENAME (https://drive.google.com/...)"; (2) named external tools with a live verification URL where applicable (e.g. "PageSpeed Insights — Desktop (https://pagespeed.web.dev/...)", "W3C Markup Validation Service (https://validator.w3.org/...)"); (3) specific verifiable URLs or named resources (sitemap.xml, robots.txt). Raw data input filenames must never appear — sf-*.csv, psi-*.json, ga4-*.csv, gsc-*.csv, majestic_*.csv, whois.txt, and se-ranking-*.csv are internal analyst files, not deliverables. Analyst process descriptions ("Manual inspection," "User confirmation," "page source," "visual inspection," "background agent," "site crawl") must never appear in Sources. Internal phase or element references ("Phase 4 O05," "see T14") must never appear in any client-facing field. When the sole evidence for a finding is a direct owner confirmation, leave Sources blank — the Data Analyzed column is the correct location for "Confirmed by site owner" or equivalent. Sources must never contain "User confirmation," "user-provided," or any attribution to the chat interaction.

**End-of-phase report check — mandatory**: At the end of every phase, before writing the session-state.md and running /compact, ask: "Are there any additional tertiary reports that should be generated based on this phase's findings?" Suggest at least one or two specific reports if the data warrants it (e.g. a page-speed breakdown CSV, a schema coverage report, a competitor gap table). Do not wait for the session close gate — raise these at the phase boundary so they can be included in the Production Plan.

**Production Plan — mandatory Phase 0 output**: Create the Production Plan immediately after the Phase 0 gap report, before Phase 1 begins. It is not optional. Do not proceed to Phase 1 without it. The Production Plan lists all anticipated tertiary output files with status tracking: `[ ]` not started, `[~]` in progress, `[x]` complete, `[!]` blocked. Update it throughout the session as new findings trigger additional outputs. Always include the workbook (Google Sheet) and HTML report (9 .html files) as standard tracked entries from the start — they are mandatory deliverables, not optional extras.

**Phase 4 tertiary file gate**: Phase 4 is not complete until all 10 mandatory files exist in the Outputs folder. Confirm each file before declaring Phase 4 complete and advancing to Phase 5:

1. Title Tag Issues .csv
2. Meta Description Issues .csv
3. H1 Issues .csv
4. Heading Hierarchy Issues .csv
5. Image Alt Tag Issues .csv
6. Canonical Tag Issues .csv
7. Redirect Plan .csv
8. Internal Linking Report .csv
9. External Linking Report .csv
10. Sitemap Recommendations Report .csv

Note: Robots.txt Recommendation .txt is a conditional output — write it if T04 scoring identified required changes, but it does not block Phase 5.

Phase 4 is also not complete until all mandatory export files have been uploaded to Google Drive as Google Sheets and their Drive URLs recorded in the Sources column of their corresponding scoring rows. Confirm Drive URL presence before declaring Phase 4 complete.

**Google Sheet format — all exports as Sheets/Docs**: When the user selects Google Sheet workbook format in Phase 0 Step 3, every export file (mandatory and conditional — title tag issues, meta description issues, H1 issues, heading hierarchy, image alt, canonical tag issues, redirect plan, internal linking report, external linking report, sitemap delta, schema analysis, word count, backlink toxicity, AI visibility summary, HTTP header summary, and any other export generated during the audit) must be uploaded to Google Drive as a Google Sheet (not as a raw .csv). Use the Drive API files.copy with mimeType=application/vnd.google-apps.spreadsheet to convert at upload time. Record the resulting https://docs.google.com/spreadsheets/d/... URL in the Sources column — never a drive.google.com/file/d/... link to a raw CSV. If workbook format is local .xlsx, exports may be recorded as .csv Drive links.

**Phase 5 disavow gate**: At the end of Phase 5, check the Moz Spam Score. If the Spam Score is above 10%, the disavow.txt trigger condition is met. Before advancing to Phase 6, present the user with: "Spam Score is above the 10% flag threshold. A disavow.txt is a required conditional deliverable for this audit. Shall I generate it now, or defer until after Phase 6?" Do not silently skip to Phase 6 without surfacing this. If the user defers, record the deferral in the Production Plan as `[~]` blocked on user approval and generate the file before the session close gate.

**Workbook generation gate**: Workbook generation is a mandatory named step in the session close checklist. It cannot be skipped or deferred silently. After Phase 6, generate the Executive Summary and Session Log as .md files, then present the conditional deliverables review:

"**Conditional deliverables review — required before workbook generation.**
Generated this session: [list all files confirmed written]
Triggered but not yet generated: [list all triggered conditions where the file was not written]
Pending user confirmation: [list any items where user was asked but has not yet confirmed]
Please confirm or request any outstanding deliverables before I compile the workbook."

Only after the user has acknowledged this review: ask "All phases complete. Ready to generate the workbook?" Load OUTPUTS-WORKBOOK.md before proceeding. Generating the workbook means running the two-script pipeline: `extract_data.py` → `generate_gsheet.py` to create the Google Sheet in Drive. Do not close the session without this step being explicitly completed or explicitly deferred by the user.

**Comments for Claude feedback loop — mandatory post-sheet step**: After the Google Sheet URL is confirmed, present the feedback prompt (see OUTPUTS-WORKBOOK.md — COMMENTS FOR CLAUDE FEEDBACK LOOP). Do not proceed to the HTML report step until the user either types **comments added** (and Claude reads + applies adjustments from column R) or explicitly types **no comments**. This step cannot be silently skipped. Record the outcome in session-state.md: either "Column R feedback loop completed — [N] adjustments applied" or "Column R feedback loop skipped — user confirmed no comments."

**Comments for Claude — column R, not S**: The Google Sheet uses 18 columns (A–R). Column R is "Comments for Claude" — the user fills this column after delivery with corrections, flags, and instructions. Column S does not exist in the current sheet layout. All references to column S in older sessions or notes should be read as column R.

**Comments for Claude — implement and clear**: When reading column R to apply adjustments: (1) Read all non-empty R cells first. (2) Implement each change. (3) After each change is complete, clear that R cell (write empty string to cell). This ensures subsequent reads of column R return only new, unprocessed comments. Clear the cell only after the full change for that comment is confirmed done — not when work is in-progress.

If skill-watchdog is active: pass all non-empty column R comments to the watchdog Phase 5 registry update before closing.

**HTML report gate**: After the feedback loop is confirmed complete (or explicitly skipped), ask: "Ready to generate the HTML client report?" Load OUTPUTS-HTML.md before proceeding. The HTML report is a standard deliverable — it cannot be skipped silently. If the user defers it, record the deferral explicitly before closing the session.

**Activity log**: Run `scripts/activity_log.py` with the session ID to generate the audit activity log. This is a final deliverable — run it after the workbook is confirmed. To use: set `AUDIT_DIR`, `CLIENT_NAME`, `AUDIT_DATE`, and `SESSION_ID` at the top of the script, then run `python3 scripts/activity_log.py`. The script auto-searches all project slugs under `~/.claude/projects/` for the matching JSONL. To find SESSION_ID: run `ls ~/.claude/projects/[project-slug]/` — JSONL files are named by session ID. The project slug is the audit directory path with forward slashes replaced by hyphens.

**Validation gates (CHECKS.md)**: Load CHECKS.md at five trigger points — do not skip:
- **L0 (pre-launch)**: before Phase 0 begins — run all L0 checks before any audit work
- **L1 (post-phase)**: after each phase .md is written to disk, before /compact — run all L1 checks, then write session-state.md, then /compact
- **L2 (pre-workbook)**: before running extract_data.py — run all L2 checks
- **L3 (post-pipeline)**: after generate_gsheet.py confirms the Google Sheet — run all L3 checks
- **L4 (post-HTML)**: after all 9 .html files are written to the HTML/ folder — run all L4 checks

---

---

## COMMENTS TO CLAUDE — FEEDBACK PROCESSING PROTOCOL

Column S (Comments to Claude / Comments for Claude) is the user's post-delivery feedback channel. Comments may correct a specific cell, flag a skill-level mistake, or do both. The rules below govern every session that includes reading and acting on column S content.

**Rule C1 — Load reference docs before acting**: CLAUDE.md is always loaded first (it is auto-loaded at session start). Before acting on any comment, classify the comment type and load the corresponding reference file using the table below. Do not act on any comment without loading the reference file mapped to its type. Processing comments without the correct reference doc causes the same errors to recur because scoring criteria, weight standards, column definitions, style rules, and API instructions are not in active context.

If skill-watchdog is active this session (Phase 11): before acting on each comment, declare the comment class (row_fix / skill_rule / both) and the reference file being loaded. This declaration is the Phase 11 verification trigger — the watchdog reads it to confirm the reference gate was satisfied before the change is applied.

| Comment type | Signal words / examples | Load before acting |
|---|---|---|
| Technical scoring — Phases 1–3 | canonical tags, redirect chains, HTTPS, robots.txt, Core Web Vitals, crawl errors, 404s, mobile, page speed, structured data errors, tracking setup, GSC/GA4 configuration | `REFERENCE-1.md` |
| On-site / off-site / GEO scoring — Phases 4–6 | meta descriptions, H1, title tags, image alt, internal linking, backlinks, domain authority, AI overview, LLM citation, Bing GEO | `REFERENCE-2.md` |
| Schema markup | JSON-LD, structured data, schema gaps, Schema.org, FAQPage, Product schema | `REFERENCE-SCHEMA.md` |
| Data source / API access | "here is GSC access", "use PSI API", "Screaming Frog available", "SF crawl done", "GA4 export attached" | `scripts/api_clients.py`, Phase 0 data source section of SKILL.md |
| Writing style / verbosity | "too long", "redundant", "rewrite in style B", "score explanation verbose", "plain language", "tighten up" | `CHECKS.md` |
| Output format / column layout | "wrong column", "priority colour", "conditional formatting", "column order", "Data Analyzed vs How to Correct" | `OUTPUTS-WORKBOOK.md`, `CHECKS.md` |
| Mandatory Phase 4 export | "generate title tag report", "create redirect plan CSV", "upload to Drive", "word count report" | `FORMS-EXPORTS-MANDATORY.md` |
| Conditional export | "disavow file", "sitemap delta", "robots.txt recommendation", "schema analysis CSV" | `FORMS-EXPORTS-CONDITIONAL.md` |
| HTML report | "report card", "phase heading", "HTML layout", "client report" | `OUTPUTS-HTML.md` |

**Rule C2 — Classify before acting**: Read all non-empty column S cells in full before making any changes. For each comment, classify it as one of:
- **Row fix** — a correction scoped to specific cells in that row (swap columns, rewrite a cell, fix a value)
- **Skill rule** — a pattern-level instruction about what the skill should always or never do
- **Both** — a row fix that also reveals a recurring skill rule

After classifying, load the reference file(s) mapped to each comment type per Rule C1. If comments span multiple types, load all relevant files before beginning any edits. Present the classification list to the user if more than 3 comments are pending, then ask for confirmation before proceeding. For 1–3 comments, act directly without asking.

If skill-watchdog is active (Phase 11): after completing all row fixes and skill corrections, do not clear any column S/R cells until the watchdog's Phase 11 post-review report has been surfaced to the user. The watchdog report must appear before column S/R is cleared.

**Rule C3 — Security rule — never include property IDs or account identifiers in any sheet cell**: The following must never appear in any cell of any audit sheet: GA4 property IDs, Google Search Console property IDs, Google Analytics view IDs, OAuth tokens, API keys, or any authentication credential. Replace all such references with the descriptive property name only — e.g. "GA4 — Dunkin' Creamers" not "GA4 property 376201222." This applies to Data Analyzed, Sources, Score Explanation, and every other column. If a property ID appears in any cell written by a previous session, it must be corrected immediately when discovered, even outside a comment-processing session.

**Rule C4 — No word count prescriptions in How to Correct**: Never specify a minimum or target word count in any How to Correct cell. Phrases such as "minimum 300 words," "150–200 words," "at least 500 words," or any numerical word count target are prohibited. Use qualitative framing only: "add substantive body copy," "expand with ingredient lists and instructions," "include introductory copy." Word count data may appear in Score Explanation or Data Analyzed only when it is a factual data point from the word count report, not a prescription.

**Rule C5 — Only clear comments that are fully addressed**: When a column S cell is cleared, it must be because the full change requested in that comment has been written to the sheet. Do not clear comments in bulk or as a batch at session end. Clear each cell individually, only after the corresponding change is confirmed written. If a comment contains multiple requests, only clear it after all requests in that comment are addressed. Never clear a comment that has not been fully acted upon.

**Rule C7 — No phase references in client-facing cells**: Never reference phase names or numbers ("Phase 1," "Phase 3," "Phase 4") in any client-facing field — Score Explanation, How to Correct, Comments, Data Analyzed, or Sources. Clients reading the audit output do not know the internal phase structure and phase labels have no meaning outside the analyst workflow. Replace any phase reference with the underlying finding or source: "Phase 1 sitemap analysis" → "Sitemap analysis"; "confirmed in Phase 3" → "confirmed at setup"; "corroborated by Phase 1 AggregateRating finding" → "corroborated by schema review." This applies to all output written during the audit and to any cell edited in response to a comment. When reviewing cells in response to a comment, scan all visible fields for phase references and remove them.

**Rule C6 — Column discipline**: Before editing any cell based on a comment, verify that the content belongs in the target column. The most common column-swap errors are Data Analyzed (O) and How to Correct (P) — Data Analyzed must contain data sources and observed findings; How to Correct must contain action recommendations only. If a cell contains content that belongs in the other column, swap both cells simultaneously. Never leave one column with content from the other. Apply the same check to Score Explanation (L) vs. Comments (Q): analytical narrative belongs in Q, not in L.

---

*CLAUDE.md | seo-geo-technical-audit | Version 17 | May 2026*
