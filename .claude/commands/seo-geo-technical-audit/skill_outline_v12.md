# SEO & GEO Technical Audit — Skill Outline v12

**Skill name:** seo-geo-technical-audit
**Version:** 12
**Invoke with:** `/seo-geo-technical-audit`
**Skill directory:** `/Users/carlaklaasen/claude_code/all_skills/seo-geo-technical-audit-v12/`
**Last updated:** April 2026

---

## What This Skill Does

Runs a structured 6-phase SEO and GEO (AI visibility) audit on any website. Produces scored output tables per phase, mandatory and conditional tertiary CSV reports, and a formatted Excel workbook and HTML client report as the final deliverables. Built for Digitad.

---

## Audit Structure

| Phase | Family | Elements | Key data sources |
|---|---|---|---|
| 0 | Intake & Data Inventory | — | All client exports |
| 1 | Technical | 26 (T01–T26) | Screaming Frog, PageSpeed, GTmetrix, WHOIS |
| 2 | User Experience | 14 (U01–U14) | GSC Core Web Vitals, Screaming Frog, manual |
| 3 | Tools & Configuration | 11 (C01–C11) | GSC, GA4, GTM, WHOIS, Moz |
| 4 | On-Site SEO | 26 (O01–O26) | Screaming Frog (titles, meta, H1/H2, images, schema, URLs) |
| 5 | Off-Site | 11 (F01–F11) | Moz/Majestic/Ahrefs, Lumen, competitor URLs |
| 6 | GEO / AI Visibility | 26 (G01–G26) | SE Ranking, manual AI data, entity review |
| **Total** | | **114 elements** | |

---

## Output Files

### Main Deliverables (naming: `[Client Name] - [Description] - [Month Year].[ext]`)
- `[Client] - Phase 1 Technical - [Month Year].md` through Phase 6
- `[Client] - Executive Summary - [Month Year].md`
- `[Client] - Session Log - [Month Year].md`
- `[Client] - SEO GEO Audit - [Month Year].xlsx` (4-tab workbook)
- `[Client] - Audit Activity Log - [Month Year].md`
- `Outputs/production-plan.md` (internal)
- `Outputs/session-state.md` (internal, pre-/compact save)

### HTML Client Report (naming: `[report-name].html` inside `HTML/` folder)
| File | Content |
|---|---|
| `index.html` | Overview — overall score, priority matrix, exec summary |
| `technical.html` | Phase 1 — Technical findings |
| `ux.html` | Phase 2 — User Experience findings |
| `tools.html` | Phase 3 — Tools & Configuration findings |
| `on-site.html` | Phase 4 — On-Site SEO findings |
| `off-site.html` | Phase 5 — Off-Site findings |
| `geo.html` | Phase 6 — GEO / AI Visibility findings |
| `schema.html` | Schema markup corrections |
| `methodology.html` | Audit methodology |

**Generated via:** `scripts/generate_html.py` — never write HTML files individually.

### Mandatory Phase 4 Exports (naming: `[CLIENT_NAME]-[report-name].csv`)
| File | Source |
|---|---|
| `[CLIENT_NAME]-title-tag-issues.csv` | sf-titles.csv |
| `[CLIENT_NAME]-meta-description-issues.csv` | sf-meta.csv |
| `[CLIENT_NAME]-h1-issues.csv` | sf-h1.csv |
| `[CLIENT_NAME]-heading-hierarchy-issues.csv` | sf-h2.csv |
| `[CLIENT_NAME]-image-alt-issues.csv` | sf-alt.csv |
| `[CLIENT_NAME]-canonical-tag-issues.csv` | sf-canonicals.csv |
| `[CLIENT_NAME]-redirect-plan.csv` | sf-4xx.csv |
| `[CLIENT_NAME]-internal-linking-report.csv` | sf-internal-links.csv |
| `[CLIENT_NAME]-external-linking-report.csv` | sf-external-urls.csv |

### Conditional Exports (triggered by findings — naming: `[CLIENT_NAME]-[report-name].[ext]`)
| File | Trigger condition |
|---|---|
| `[CLIENT_NAME]-robots-txt-recommendation.txt` | T04 scoring identifies required robots.txt changes |
| `[CLIENT_NAME]-disavow.txt` | Moz Spam Score > 10% or toxic backlinks identified |
| `[CLIENT_NAME]-backlink-toxicity-review.csv` | Phase 5 backlink review finds flagged domains |
| `[CLIENT_NAME]-sitemap-delta.csv` | Sitemap gaps identified during audit |
| `[CLIENT_NAME]-word-count-report.csv` | sf-content-all.csv provided and thin content flagged |
| `[CLIENT_NAME]-http-header-summary.csv` | sf-headers.csv provided and security header issues found |
| `[CLIENT_NAME]-protocol-relative-resources.csv` | Protocol-relative URLs identified |
| `[CLIENT_NAME]-schema-analysis.csv` | Schema Sub-Phase completed with corrections |
| `[CLIENT_NAME]-ai-visibility-summary.csv` | GEO data manually provided and Phase 6 complete |

---

##Directory Breakdown: 

seo-geo-technical-audit-v8/
├── CLAUDE.md
├── SKILL.md
├── README.md
├── CHECKS.md
├── REFERENCE-1.md
├── REFERENCE-2.md
├── REFERENCE-SCHEMA.md
├── ASSETS.md
├── FORMS-EXPORTS-MANDATORY.md
├── FORMS-EXPORTS-CONDITIONAL.md
├── FORMS-INTERNAL.md
├── OUTPUTS-HTML.md
├── OUTPUTS-WORKBOOK.md
├── DESIGN.md
└── scripts/
	└── extract_data.py
	└── generate_workbook.py
	└── generate_html.py
	└── validate_phase.py
	└── build_schema_tab.py
	└── activity_log.py
└── examples/
	└── 404-redirection-plan-example.csv
	└── audit-workbook-example.csv
	└── canonical-tag-redirection-plan-example - Sheet1.csv
	└── executive-summary-example.csv
	└── overview-tab-example.png
	└── robots.txt-recommendation-example.csv.txt
	└── schema-markup-example.csv
	└── title-tag-issues-example.csv
	└── html-preview/
		└── index.html
		└── methodology.html
		└── schemaexample.html
		└── technical.html
	


## File Directory

| File | Purpose | Load when |
|---|---|---|
| `CLAUDE.md` | All permanent rules — auto-loaded first | Always, before any audit work |
| `SKILL.md` | Full audit workflow — Phase 0 through session close. Contains 5 Modes: A. New Audit, B. Re-Audit, C. Schema Deep Dive Only, D. Executive Summary Only, E. HTML Report Only | Always |
| `CHECKS.md` | Validation gate checklists L0–L4 and pre-/compact save protocol | L0/L1/L2/L3/L4 trigger points |
| `REFERENCE-1.md` | Element definitions and scoring criteria for Phases 1–3 | Before scoring Phase 1, 2, or 3 |
| `REFERENCE-2.md` | Element definitions and scoring criteria for Phases 4–6 | Before scoring Phase 4, 5, or 6 |
| `REFERENCE-SCHEMA.md` | JSON-LD schema templates per page type | Before Schema Sub-Phase or Mode C |
| `ASSETS.md` | Site-type weight adjustment table, Phase 0 intake checklist | Before Phase 0 or workbook generation |
| `FORMS-EXPORTS-MANDATORY.md` | 9 required Phase 4 CSVs and Executive Summary templates | Before generating any mandatory export |
| `FORMS-EXPORTS-CONDITIONAL.md` | Conditional export file schemas | Before generating any conditional export |
| `FORMS-INTERNAL.md` | Production Plan and Session Log templates | Phase 0, and when updating the Session Log |
| `OUTPUTS-WORKBOOK.md` | Workbook column spec, tab structure, formatting, naming rules | Before running the workbook pipeline |
| `OUTPUTS-HTML.md` | HTML report generation instructions — uses generate_html.py | Before generating HTML report |
| `DESIGN.md.rtf` | Design system authority — colour tokens, typography, elevation, component rules | Before generating HTML report (reference only) |

### Scripts
| Script | Purpose | When to run |
|---|---|---|
| `scripts/validate_phase.py` | Validates a phase .md file against the 17-column spec | After each phase is written (L1 gate) |
| `scripts/extract_data.py` | Parses all 6 phase .md files → writes workbook_data.json | L2 gate (before workbook) |
| `scripts/generate_workbook.py` | Reads workbook_data.json → builds .xlsx | After extract_data.py confirms 114 rows |
| `scripts/generate_html.py` | Reads workbook_data.json → generates all 9 HTML files in one pass | L4 gate (after workbook confirmed) |
| `scripts/build_schema_tab.py` | Adds Schema Analysis tab to workbook if schema CSV exists | Optional, after workbook pipeline |
| `scripts/activity_log.py` | Generates audit activity log from Claude session JSONL | After workbook is confirmed |

---

## Validation Gates

| Gate | Trigger | What it checks |
|---|---|---|
| L0 — Pre-launch | Before Phase 0 begins | Skill files present, scripts pass syntax check, write-check complete |
| L1 — Post-phase | After each phase .md written, before /compact | 17 columns, correct row count, no element codes, valid Status values, conditional outputs on disk, schema sub-phase offered if triggered |
| L2 — Pre-workbook | Before running extract_data.py | All 6 phases present, all 9 Phase 4 CSVs present, JSON config set, Production Plan [x] items verified |
| L3 — Post-pipeline | After generate_workbook.py | JSON has 114 rows, .xlsx has 4 correct tabs |
| L4 — Post-HTML | After all 9 .html files written | All 9 files present, no element codes, no Phase references, correct nav, generated via script |

---

## Key Rules (Quick Reference)

| Rule | Description |
|---|---|
| S1 | Write-check test before any audit work — both .md and .csv |
| S2 | Write phase .md to disk before printing to chat |
| S3 | One phase at a time — no batching |
| S4 | No background file writing; no WebFetch in background agents |
| S5 | /compact after every phase — never wait for context limit |
| S6 | Two-tier file naming — main deliverables use `[Client] - [Desc] - [Date].[ext]`; exports use `[CLIENT_NAME]-[report-name].[ext]` |
| S7 | Write session-state.md before every /compact — hard dependency, no exceptions |
| S8 | Never write HTML files individually — always use scripts/generate_html.py |

---

## What Changed in v12 (from v11)

| Area | Change |
|---|---|
| **Schema Sub-Phase gate** | Explicit prompt added to Phase 4 gate: if schema overview scored Weak, Not Present, or Opportunity, Claude must ask about Schema Sub-Phase before advancing to Phase 5. Previously schema sub-phase was documented but had no trigger gate. |
| **Conditional outputs L1 gate** | L1-16 added to CHECKS.md: any conditional output referenced in phase scoring must exist on disk before /compact. Closes the gap where outputs were scored but not written until a later session. |
| **Contradiction detection** | New hard-stop rule in CLAUDE.md: if any phase finding contradicts an earlier PROMPT USER answer, Claude stops, presents the contradiction with three resolution options, and waits for user confirmation before scoring continues. Phase .md updated if needed before proceeding. |
| **CHECKS.md frontmatter** | Load trigger updated from "L0/L1/L2/L3" to "L0/L1/L2/L3/L4" — L4 was added in v11 but frontmatter was not updated. |
| **validate_phase.py path** | Path example in CHECKS.md L1 path rule corrected from v9 to v12. |
| **skill_outline** | This file — updated from v9 to v12 with all current state including HTML deliverables, generate_html.py, S7/S8 rules, and L4 gate. |
|Schema Generation Report Criteria created in SKILL.md

---

*skill_outline_v12.md | seo-geo-technical-audit | Version 12 | April 2026*
