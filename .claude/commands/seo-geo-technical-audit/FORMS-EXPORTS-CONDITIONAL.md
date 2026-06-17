---
name: seo-geo-technical-audit / FORMS-EXPORTS-CONDITIONAL.md
load: On demand — read before generating any conditional export file. Read only the section for the file you are about to write. Writing process rules are in FORMS-EXPORTS-MANDATORY.md.
---

# SEO & GEO Audit — Conditional Export File Schemas

---

## PROACTIVE NEW REPORT RULE

When any of the following conditions occur during scoring or file generation, stop and ask the user whether they want a new dedicated output file created before continuing:

- A "How to Correct" field contains more than 2 URLs → Ask: "There are [N] URLs in this recommendation. Would you like me to create a separate export with just these URLs and a short summary left in the How to Correct field?"
- Sitemap changes are identified → Ask: "I've identified URLs to add and remove from your sitemap. Shall I write a sitemap-delta.csv file with these?"
- robots.txt changes are needed → Ask: "I have a robots.txt recommendation. Shall I write a robots-txt-recommendation.txt file with the current and updated version?"
- Toxic backlinks warrant disavow action → Ask: "Some of these backlinks warrant disavowal. Shall I write a disavow.txt file in Google Disavow format?"
- Phase 4 scoring reveals both internal and external linking issues → Ask: "I can generate both an Internal Linking Report and an External Linking Report. Shall I proceed with both?"
- Word count data is available → Ask: "I have word count data from sf-content-all.csv. Shall I generate a word-count-report.csv?"
- robots.txt recommendation Google Doc created → record the Google Doc URL in the Sources column of the robots.txt scoring row

Do not wait for the session close gate to raise these. Raise them at the point the condition is met.

---

## FILE 8 — Backlink Toxicity Review

Source: backlinks-export.csv (Moz / Ahrefs / Semrush)
Filename: [CLIENT_NAME]-backlink-toxicity-review.csv

Column order (exact):
`Domain, DA/DR, Spam Score, Risk Level, Issue, Recommendation, Notes`

| Column | Source | Notes |
|---|---|---|
| Domain | Backlink export | Referring domain — root domain only |
| DA/DR | Backlink export | Domain Authority (Moz) or Domain Rating (Ahrefs) — note which tool in header |
| Spam Score | Backlink export | Percentage as reported by tool |
| Risk Level | Claude-generated | LOW (spam under 30%), MEDIUM (30–60%), HIGH (above 60%) |
| Issue | Claude-generated | Brief description of why the domain is flagged |
| Recommendation | Claude-generated | One of: Monitor, Disavow, Request Removal |
| Notes | Claude-generated | Additional context |

Upload the CSV to Google Drive as a Google Sheet per the writing process rules in FORMS-EXPORTS-MANDATORY.md and record the Drive URL in the Sources column of the corresponding scoring row.

---

## FILE 11 — Protocol Relative Resource Report

Source: sf-headers.csv / source code review
Filename: [CLIENT_NAME]-protocol-relative-resources.csv

Column order (exact):
`Page URL, Resource URL, Resource Type, Issue, Recommendation, Priority`

| Column | Source | Notes |
|---|---|---|
| Page URL | SF export / spot-check | Full absolute URL of the page containing the resource |
| Resource URL | SF export / spot-check | The resource URL as implemented — e.g. //cdn.example.com/script.js |
| Resource Type | Claude-generated | One of: Script, Stylesheet, Image, Font, iFrame |
| Issue | Claude-generated | Protocol-relative URL — will inherit HTTP or HTTPS from the page, creating mixed content risk on HTTP pages |
| Recommendation | Claude-generated | Replace //cdn.example.com/... with https://cdn.example.com/... |
| Priority | Claude-generated | HIGH / MEDIUM / LOW |

Upload the CSV to Google Drive as a Google Sheet per the writing process rules in FORMS-EXPORTS-MANDATORY.md and record the Drive URL in the Sources column of the corresponding scoring row.

---

## FILE 12 — HTTP Header Summary

Source: sf-headers.csv
Filename: [CLIENT_NAME]-http-header-summary.csv

Column order (exact):
`Page URL, Header, Current Value, Issue Type, Recommended Value, Priority, Notes`

| Column | Source | Notes |
|---|---|---|
| Page URL | SF export | Full absolute URL |
| Header | SF export | Header name — e.g. Content-Security-Policy, X-Frame-Options, Strict-Transport-Security |
| Current Value | SF export | Current header value — blank if header is missing |
| Issue Type | Claude-generated | One of: Missing Security Header, Misconfigured Header, Deprecated Header, Overly Permissive Policy |
| Recommended Value | Claude-generated | The correct header value and directive — written out in full |
| Priority | Claude-generated | HIGH / MEDIUM / LOW |
| Notes | Claude-generated | Analyst comment — leave blank if no additional context needed |

Upload the CSV to Google Drive as a Google Sheet per the writing process rules in FORMS-EXPORTS-MANDATORY.md and record the Drive URL in the Sources column of the corresponding scoring row.

---

## FILE 13 — Sitemap Delta

Trigger: Generated when sitemap scoring identifies URLs to add or remove.
Ask user before writing: "I've identified URLs to add and remove from your sitemap. Shall I write a sitemap-delta.csv file with these?"
Filename: [CLIENT_NAME]-sitemap-delta.csv

Column order (exact):
`Action, URL, Reason`

| Column | Notes |
|---|---|
| Action | Add / Remove |
| URL | Full absolute URL |
| Reason | Brief explanation — e.g. "URL not in sitemap but indexed" or "404 URL still listed in sitemap" |

Upload the CSV to Google Drive as a Google Sheet per the writing process rules in FORMS-EXPORTS-MANDATORY.md and record the Drive URL in the Sources column of the corresponding scoring row.

---

## FILE 14 — Robots.txt Recommendation

Trigger: Generated when robots.txt scoring identifies required changes.
Ask user before writing: "I have a robots.txt recommendation. Shall I write a robots-txt-recommendation.txt file with the current and updated version?"
Filename: [CLIENT_NAME]-robots-txt-recommendation.txt

File structure:
```
## CURRENT ROBOTS.TXT
[paste current robots.txt content exactly as-is]

## RECOMMENDED ROBOTS.TXT
[corrected robots.txt]

## CHANGE LOG
[one line per change — what was changed and why]
```

Before writing this file, read examples/robots.txt-recommendation-example.csv.txt to verify file structure and format.

After writing the .txt file to Outputs/, upload it to Google Drive as a Google Doc using:
    python3 scripts/upload_exports.py --file Outputs/[CLIENT_NAME]-robots-txt-recommendation.txt --type doc --folder [GDRIVE_EXPORTS_DIR_ID] --name "[CLIENT NAME] - Robots.txt Recommendation - [Month Year]"

Record the returned Google Drive URL in the Sources column of the robots.txt scoring row in the phase .md file.

---

## FILE 15 — Disavow File

Trigger: Generated when backlink scoring identifies domains that warrant disavowal. Also triggered when Moz Spam Score exceeds 10% — see Phase 5 disavow gate in CLAUDE.md.
Ask user before writing: "Some of these backlinks warrant disavowal. Shall I write a disavow.txt file in Google Disavow format?"
Filename: [CLIENT_NAME]-disavow.txt

Format follows Google Disavow specification:
```
# Disavow file — [CLIENT] — [Month Year]
# Generated by Digitad
# Upload via: GSC → Links → Disavow Links
# One domain per line using domain: prefix to disavow entire domain

domain:spammy-example.com
domain:link-farm-site.ru
```

Rules:
- Use domain: prefix to disavow the entire domain (preferred over individual URL disavowal for pattern spam)
- Use full URL only when a single URL from an otherwise clean domain must be disavowed
- Include a comment block at the top with client name, date, and upload instructions
- List each domain on its own line — no trailing spaces or special characters

After writing [CLIENT_NAME]-disavow.txt to Outputs/, upload it to Google Drive as a Google Doc using:
    python3 scripts/upload_exports.py --file Outputs/[CLIENT_NAME]-disavow.txt --type doc --folder [GDRIVE_EXPORTS_DIR_ID] --name "[CLIENT NAME] - Disavow File - [Month Year]"

---

## FILE 16 — Word Count Report

Trigger: Generated when sf-content-all.csv is available and content quality is being scored.
Ask user before writing: "I have word count data from sf-content-all.csv. Shall I generate a word-count-report.csv?"
Filename: [CLIENT_NAME]-word-count-report.csv

Process:
1. Use sf-content-all.csv as the source file — preserve all existing columns and formatting exactly as-is
2. Add one row at the bottom of the file:
   - In the URL column: write "SITE AVERAGE"
   - In the Word Count column: write the calculated average word count across all URLs (rounded to nearest whole number)
   - Leave all other columns blank for this row
3. Do not modify any other rows or columns

Upload the CSV to Google Drive as a Google Sheet per the writing process rules in FORMS-EXPORTS-MANDATORY.md and record the Drive URL in the Sources column of the corresponding scoring row.

---

*FORMS-EXPORTS-CONDITIONAL.md | seo-geo-technical-audit | Version 10 | April 2026*
