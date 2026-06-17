---
name: seo-geo-technical-audit / ASSETS.md
load: On demand — read before generating the workbook or HTML report.
---

# SEO & GEO Audit — Assets & Reference

Load this file alongside OUTPUTS-WORKBOOK.md or OUTPUTS-HTML.md when generating final outputs.

---

## USEFUL TOOL REFERENCE URLS

These URLs are for analyst use during scoring and for inclusion in the completeness report. They must NOT appear in the Sources column of client-facing output files — sources must reference specific exports or output reports only.

| Tool | URL |
|---|---|
| PageSpeed Insights | https://pagespeed.web.dev/ |
| GTmetrix | https://gtmetrix.com/ |
| WHOIS / DomainTools | https://whois.domaintools.com/ |
| DA Checker | https://www.dapachecker.org/ |
| DMCA / Lumen Database | https://lumendatabase.org/notices/search |
| Rich Results Test | https://search.google.com/test/rich-results |
| Schema Validator | https://validator.schema.org/ |
| Bing Webmaster Tools | https://www.bing.com/webmasters/ |
| Bing Places | https://www.bingplaces.com/ |
| SSL Checker | https://www.sslshopper.com/ssl-checker.html |
| Google Safe Browsing | https://transparencyreport.google.com/safe-browsing/search |
| W3C HTML Validator | https://validator.w3.org/ |
| Google Disavow spec | https://support.google.com/webmasters/answer/2648487 |
| SE Ranking | https://app.seranking.com/ |
| SE Ranking API docs | https://docs.seranking.com/ |
| Screaming Frog API docs | https://www.screamingfrog.co.uk/frog-api/ |
| Majestic API docs | https://developer.majestic.com/ |
| PageSpeed Insights API | https://developers.google.com/speed/docs/insights/v5/get-started |
| GSC API docs | https://developers.google.com/webmaster-tools |
| GA4 Data API docs | https://developers.google.com/analytics/devguides/reporting/data/v1 |
| Moz API docs | https://moz.com/help/links-api |
| WHOIS XML API | https://www.whoisxmlapi.com/documentation/making-api-calls.php |
| Google Sheets API docs | https://developers.google.com/sheets/api |
| Google Drive API docs | https://developers.google.com/drive/api/v3/about-sdk |
| Google Docs API docs | https://developers.google.com/docs/api |

---

## SITE-TYPE WEIGHT ADJUSTMENT RULES

Apply these automatically when site type warrants it. Flag each adjustment with [W-ADJ: reason] in the Comments column of the affected element row. Ask a clarifying question before adjusting any weight by more than one tier.

| Site type | Elements to weight up | Elements to weight down / Not Applicable |
|---|---|---|
| E-commerce | Product schema, PageSpeed mobile, reCAPTCHA, site search, reviews | Bing Places (unless local) |
| Local business | Bing Places, GMB/GBP, local schema, reviews, NAP consistency | Portfolio page |
| SaaS / B2B | Bing WMT, author pages, case studies/portfolio, B2B review platforms | Recipe schema |
| CPG / FMCG brand | Entity presence, social signals, community/reviews, recipe schema | Bing Places, hreflang |
| Media / Publisher | Author pages, article schema, TOC, content freshness, DMCA | Product schema |

---

## GEO SIGNALS — CURRENT AS OF Q1 2026

The following GEO/LLM elements reflect current best practices as of Q1 2026. Review and update quarterly:

- G01: AI Overview citation patterns — Google changing display frequency
- G02: ChatGPT/Perplexity citation methodology evolving — se-ranking-aivisibility.csv is the primary data source
- C10: LLM referral tracking in GA4 — new referral sources emerging monthly
- G12: LLM content structure requirements — updating as models evolve
- G26: Bing/ChatGPT integration deepening — weight may increase in future audits

---

## EXAMPLE FILES

For worked examples of correctly formatted output files, read the following. Load only the file relevant to the output currently being generated — do not load all example files at once.

| File | Path | Purpose |
|---|---|---|
| Audit workbook rows | examples/audit-workbook-example.csv | Correct row format and writing style for scoring table output |
| Title tag issues | examples/title-tag-issues-example.csv | Correct column structure and row format for tertiary issue files |
| Schema markup corrections | examples/schema-markup-example.csv | Correct column structure for schema sub-phase output |

---

*ASSETS.md | seo-geo-technical-audit | Last updated: April 2026*
