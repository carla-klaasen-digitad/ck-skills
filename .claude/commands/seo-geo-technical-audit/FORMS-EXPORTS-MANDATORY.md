---
name: seo-geo-technical-audit / FORMS-EXPORTS-MANDATORY.md
load: On demand — read before generating any mandatory Phase 4 export file or the Executive Summary. Read only the section for the file you are about to write.
---

# SEO & GEO Audit — Mandatory Export File Schemas

---

## WRITING PROCESS — ALL EXPORT FILES

Step 1: Write the file as .md using pipe-delimited table syntax. Save to Outputs/.
Step 2: Convert to .csv and save to Outputs/CSV/. Do this in the same operation — do not defer.
Step 3: Upload the CSV to Google Drive as a Google Sheet using:
    python3 scripts/upload_exports.py --file Outputs/CSV/[filename].csv --type sheet --folder [GDRIVE_EXPORTS_DIR_ID] --name [display_name]
Step 4: Record the returned Google Drive URL in the Sources column of the corresponding scoring row in the phase .md file.

**Google Sheet format enforcement**: When the user selected Google Sheet workbook format in Phase 0 Step 3, every export file must be uploaded to Google Drive as a Google Sheet within the same tool call sequence that writes the .csv. Do not leave any export file in local-only state — a local .csv with no Drive URL in the Sources column is an incomplete deliverable. Phase 4 is not complete until all 9 mandatory files are confirmed uploaded with Google Drive URLs recorded in their corresponding Sources cells. Do not declare Phase 4 complete or advance to Phase 5 without verifying every Drive URL is present.

Formatting rules that apply to every file:
- All fields containing commas must be wrapped in double quotes
- All URLs must be absolute (https://...) — never relative paths
- One row per URL per issue — never aggregate multiple issues into one row
- Claude-generated text fields must be written in full — never left blank, never marked TBD
- Priority values: HIGH / MEDIUM / LOW only — no shorthand, no emoji
- Notes field: leave blank if nothing substantive to add — never write N/A or None
- Never reference phases, phase numbers, or element codes in any field
- Every row must be fully self-contained — never write "same as above" or cross-reference another row

---

## FILE NAMING — EXPORT FILES

All export files use this naming convention: `[CLIENT_NAME]-[report-name].[ext]`
- CLIENT_NAME: all caps (e.g. YOCRUNCH, NOVABITE)
- report-name: lowercase, hyphen-separated
- No date in export filenames

---

## MANDATORY PHASE 4 COMPLETION CHECKLIST

Phase 4 is not complete until all of the following files exist on disk. Confirm each before declaring Phase 4 complete and advancing to Phase 5.

1. [CLIENT_NAME]-title-tag-issues.csv
2. [CLIENT_NAME]-meta-description-issues.csv
3. [CLIENT_NAME]-h1-issues.csv
4. [CLIENT_NAME]-heading-hierarchy-issues.csv
5. [CLIENT_NAME]-image-alt-issues.csv
6. [CLIENT_NAME]-canonical-tag-issues.csv
7. [CLIENT_NAME]-redirect-plan.csv
8. [CLIENT_NAME]-internal-linking-report.csv
9. [CLIENT_NAME]-external-linking-report.csv

If a file cannot be generated because the required source data is missing, mark it as DATA MISSING in the checklist and note which source file is needed. Do not silently skip it.

Phase 4 is also not complete until all 9 mandatory export files have been uploaded to Google Drive as Google Sheets and their Drive URLs recorded in the Sources column of their corresponding scoring rows in the phase .md file. Confirm all Drive URLs are present before declaring Phase 4 complete.

---

## FILE 1 — Title Tag Issues

Source: sf-titles.csv
Filename: [CLIENT_NAME]-title-tag-issues.csv

Column order (exact):
`Address, Title 1, Title 1 Length, Title 1 Duplicate, Title 1 Occurrences, Issue Type, Recommended Title, Priority, Notes`

| Column | Source | Notes |
|---|---|---|
| Address | SF export | Full absolute URL |
| Title 1 | SF export | Current title tag text — blank if missing |
| Title 1 Length | SF export | Character count |
| Title 1 Duplicate | SF export | Yes / No flag from SF |
| Title 1 Occurrences | SF export | Include if present in export — leave blank if column not present |
| Issue Type | Claude-generated | One of: Missing, Too Long, Too Short, Duplicate, Not Descriptive, Keyword Missing |
| Recommended Title | Claude-generated | Full corrected title tag — 50–60 characters, keyword near start |
| Priority | Claude-generated | HIGH / MEDIUM / LOW |
| Notes | Claude-generated | Analyst comment — leave blank if no additional context needed |

Before writing this file, read examples/title-tag-issues-example.csv to verify column structure and row format.

---

## FILE 2 — Meta Description Issues

Source: sf-meta.csv
Filename: [CLIENT_NAME]-meta-description-issues.csv

Column order (exact):
`Address, Meta Description 1, Meta Description 1 Length, Meta Description 1 Duplicate, Issue Type, Recommended Meta Description, Priority, Notes`

| Column | Source | Notes |
|---|---|---|
| Address | SF export | Full absolute URL |
| Meta Description 1 | SF export | Current meta description text — blank if missing |
| Meta Description 1 Length | SF export | Character count |
| Meta Description 1 Duplicate | SF export | Yes / No flag from SF |
| Issue Type | Claude-generated | One of: Missing, Too Long, Too Short, Duplicate, Generic, No CTA, Auto-Generated |
| Recommended Meta Description | Claude-generated | Full corrected meta description — 140–160 characters, includes CTA |
| Priority | Claude-generated | HIGH / MEDIUM / LOW |
| Notes | Claude-generated | Analyst comment — leave blank if no additional context needed |

---

## FILE 3 — H1 Issues

Source: sf-h1.csv
Filename: [CLIENT_NAME]-h1-issues.csv

Column order (exact):
`Address, H1-1, H1-1 Length, H1-2, H1 Count, Issue Type, Recommended H1, Priority, Notes`

| Column | Source | Notes |
|---|---|---|
| Address | SF export | Full absolute URL |
| H1-1 | SF export | Primary H1 text — blank if missing |
| H1-1 Length | SF export | Character count of H1-1 |
| H1-2 | SF export | Second H1 if multiple exist — blank if only one |
| H1 Count | SF export | Total number of H1 tags on the page |
| Issue Type | Claude-generated | One of: Missing, Multiple H1s, Duplicate Across Pages, Not Descriptive, Matches Title Tag Exactly, Brand Tagline Only |
| Recommended H1 | Claude-generated | Full corrected H1 — descriptive, keyword-relevant, unique |
| Priority | Claude-generated | HIGH / MEDIUM / LOW |
| Notes | Claude-generated | Analyst comment — leave blank if no additional context needed |

---

## FILE 4 — Heading Hierarchy Issues

Source: sf-h2.csv (cross-referenced with sf-h1.csv)
Filename: [CLIENT_NAME]-heading-hierarchy-issues.csv

Column order (exact):
`Address, H2-1, H2-2, H2-3, Issue Type, Recommended Fix, Priority, Notes`

| Column | Source | Notes |
|---|---|---|
| Address | SF export | Full absolute URL |
| H2-1 | SF export | First H2 on the page |
| H2-2 | SF export | Second H2 — blank if fewer than 2 |
| H2-3 | SF export | Third H2 — blank if fewer than 3 |
| Issue Type | Claude-generated | One of: Skipped Level (H1 to H3), Missing H2, H2 Used as Navigation, Non-Descriptive H2, Heading Used as Styling Only |
| Recommended Fix | Claude-generated | Specific structural change or corrected heading text |
| Priority | Claude-generated | HIGH / MEDIUM / LOW |
| Notes | Claude-generated | Analyst comment — leave blank if no additional context needed |

---

## FILE 5 — Image Alt Tag Issues

Source: sf-alt.csv
Filename: [CLIENT_NAME]-image-alt-issues.csv

Column order (exact):
`Page URL, Image Source, Alt Text, Issue Type, Recommended Alt Text, Priority, Notes`

| Column | Source | Notes |
|---|---|---|
| Page URL | SF export — "Address" column | The page where the image appears — full absolute URL |
| Image Source | SF export — "Image Source" or "Src" column | The image file URL — full absolute URL |
| Alt Text | SF export | Current alt text — blank if missing |
| Issue Type | Claude-generated | One of: Missing, Filename Used, Generic Text (e.g. "image", "photo"), Decorative Not Empty |
| Recommended Alt Text | Claude-generated | Descriptive alt text — keyword-relevant for product images, [empty — decorative] for decorative images |
| Priority | Claude-generated | HIGH / MEDIUM / LOW |
| Notes | Claude-generated | Analyst comment — leave blank if no additional context needed |

---

## FILE 6 — Canonical Tag Issues

Source: sf-canonicals.csv
Filename: [CLIENT_NAME]-canonical-tag-issues.csv

Column order (exact):
`Address, Canonical Link Element 1, Canonical Match, Issue Type, Recommended Canonical, Priority, Notes`

| Column | Source | Notes |
|---|---|---|
| Address | SF export | The page URL — full absolute URL |
| Canonical Link Element 1 | SF export | The canonical URL currently declared — blank if missing |
| Canonical Match | SF export | Self / Different Page / Missing — as reported by SF |
| Issue Type | Claude-generated | One of: Missing, Points to Redirect (3xx), Points to 404, Conflicting, Chain, Incorrect Consolidation |
| Recommended Canonical | Claude-generated | The correct canonical URL this page should declare — full absolute URL |
| Priority | Claude-generated | HIGH / MEDIUM / LOW |
| Notes | Claude-generated | Analyst comment including consolidation rationale where Issue Type is Incorrect Consolidation |

---

## FILE 7 — Redirect Plan

Source: sf-4xx.csv (cross-referenced with sf-internal-links.csv and backlinks-export.csv)
Filename: [CLIENT_NAME]-redirect-plan.csv

Column order (exact):
`Broken URL, Status Code, Inbound Internal Links, Inbound External Backlinks, Redirect Type, Destination URL, Priority, Notes`

| Column | Source | Notes |
|---|---|---|
| Broken URL | SF export — "Address" column | The broken page URL — full absolute URL |
| Status Code | SF export | 404, 410, or other 4xx code as reported by SF |
| Inbound Internal Links | SF export / sf-internal-links.csv | Count of internal pages linking to this broken URL — 0 if none |
| Inbound External Backlinks | Backlink export | Yes (with count) e.g. "Yes (3)" or No. Mark DATA MISSING if no backlink export provided |
| Redirect Type | Claude-generated | 301 (permanent), 302 (temporary — only if content is genuinely returning), Remove (no inbound links and not in sitemap) |
| Destination URL | Claude-generated | The live 200-response URL this broken URL should redirect to — full absolute URL. Ask user if no clear match exists. |
| Priority | Claude-generated | HIGH (has external backlinks or high internal link count), MEDIUM (internal links only), LOW (no inbound links) |
| Notes | Claude-generated | Rationale for the redirect destination |

Before writing this file, read examples/404-redirection-plan-example.csv to verify column structure and row format.

---

## FILE 9 — Internal Linking Report

Source: sf-internal-links.csv
Filename: [CLIENT_NAME]-internal-linking-report.csv

Column order (exact):
`Page URL, Inbound Internal Links, Linking Pages (Sample), Issue Type, Recommendation, Priority, Notes`

| Column | Source | Notes |
|---|---|---|
| Page URL | SF export | Full absolute URL of the page being analysed |
| Inbound Internal Links | SF export | Total count of internal links pointing to this page |
| Linking Pages (Sample) | SF export | Up to 3 example pages linking to this URL — full absolute URLs |
| Issue Type | Claude-generated | One of: No Inbound Links (orphan page), Low Inbound Links (fewer than 2), Poor Anchor Text, Only Navigational Links |
| Recommendation | Claude-generated | Specific action — e.g. "Add 2–3 contextual internal links from blog articles to this product page using keyword-relevant anchor text" |
| Priority | Claude-generated | HIGH / MEDIUM / LOW |
| Notes | Claude-generated | Additional context — leave blank if no additional context needed |

---

## FILE 10 — External Linking Report

Source: sf-external-urls.csv (cross-referenced with source code spot-checks)
Filename: [CLIENT_NAME]-external-linking-report.csv

Column order (exact):
`Page URL, External Link URL, Anchor Text, Opens New Tab, Has noopener, Issue Type, Recommendation, Priority, Notes`

| Column | Source | Notes |
|---|---|---|
| Page URL | SF export | Full absolute URL of the page containing the external link |
| External Link URL | SF export | The external destination URL — full absolute URL |
| Anchor Text | SF export | The visible anchor text of the link |
| Opens New Tab | SF export / spot-check | Yes / No — whether target="_blank" is set |
| Has noopener | Spot-check | Yes / No — whether rel="noopener noreferrer" is present |
| Issue Type | Claude-generated | One of: Missing noopener, Raw URL as Anchor, Low-Quality Domain, No New Tab on External Link, Keyword Stuffed Anchor |
| Recommendation | Claude-generated | Specific corrective action |
| Priority | Claude-generated | HIGH / MEDIUM / LOW |
| Notes | Claude-generated | Additional context — leave blank if no additional context needed |

---

## FILE 19 — Executive Summary

Trigger: Mandatory. Generated after Phase 6 is complete, before workbook generation begins.
Filename: [CLIENT] - Executive Summary - [Month Year].md

The Executive Summary is a standalone .md file used as input to the workbook Overview tab and as a client-readable plain-language summary. Write it once — do not regenerate per phase. Content is drawn from scoring data across all 6 phases.

Template:

```
# Executive Summary — [CLIENT] — [Month Year]
Prepared by: Digitad | Audit Date: [date]

## Overall Health Score
[Score]/100 — [one-sentence plain-language verdict on the site's overall SEO and GEO health]

## What Is Working Well
1. [Element name in plain language]: [plain-language strength — no element codes, no phase references]
2. [Element name in plain language]: [plain-language strength]
3. [Element name in plain language]: [plain-language strength]

## What Needs Immediate Attention
1. [Element name in plain language]: [plain-language problem] — [plain-language fix] — [business impact]
2. [Element name in plain language]: [plain-language problem] — [plain-language fix] — [business impact]
3. [Element name in plain language]: [plain-language problem] — [plain-language fix] — [business impact]
4. [Element name in plain language]: [plain-language problem] — [plain-language fix] — [business impact]
5. [Element name in plain language]: [plain-language problem] — [plain-language fix] — [business impact]

## AI & Search Visibility
[2–3 sentences on LLM readiness, AI Overview presence, and entity optimisation status — written for a non-technical client]

## Schema Markup
[1–2 sentences on overall schema health and biggest gap — no technical jargon without explanation]
```

Rules:
- No element codes anywhere in this file
- No phase references anywhere in this file
- Written in the style confirmed at Phase 0 — plain language (Style B) by default
- The Overall Health Score matches the workbook Overview tab value
- "What Is Working Well" draws from LOW or MONITOR priority rows with Excellent or High scores
- "What Needs Immediate Attention" draws from the 5 highest-priority HIGH rows by Priority Score ascending

---

*FORMS-EXPORTS-MANDATORY.md | seo-geo-technical-audit | Version 10 | April 2026*
