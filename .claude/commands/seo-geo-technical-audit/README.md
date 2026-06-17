# seo-geo-technical-audit-v13

A Claude Code skill for running structured SEO and GEO (AI visibility) audits. The skill guides Claude through a six-phase audit, produces scored output tables per phase, generates tertiary CSV exports uploaded to Google Drive as Google Sheets, and creates a formatted Google Sheet workbook as the final deliverable. API connections to Screaming Frog, SE Ranking, PageSpeed Insights, Google Search Console, GA4, Moz, Majestic, and WHOIS are configured via service account and API keys stored in `~/.config/digitad/.env`.

---

## Audit phases

| Phase | Family | Elements |
|---|---|---|
| 1 | Technical | Indexation, crawlability, speed, security, schema entity |
| 2 | UX | Mobile, Core Web Vitals, navigation, accessibility, engagement |
| 3 | Tools & Configuration | Analytics, tag management, domain, pixels, rich results |
| 4 | On-Site SEO | Meta tags, headings, content, media, URL structure, internal linking |
| 5 | Off-Site | Backlinks, brand mentions, reviews, social presence, digital PR |
| 6 | GEO / AI Visibility | LLM citation signals, entity clarity, structured content, AI crawl access |

---

## Running a new audit

**Step 1 — Set up environment credentials**

Copy `.env.example` to `~/.config/digitad/.env` and fill in all required keys (Google service account JSON path, Drive folder IDs, SE Ranking API key, Screaming Frog host, etc.). See `.env.example` for the full list.

**Step 2 — Set up the client folder**

Create a folder for the client with this structure:

```
client_audit/
  Outputs/
  Outputs/CSV/
  Workbook/
```

**Step 3 — Initialise the session**

Run the session initialiser to test API connections and write the session config file:

```bash
python3 scripts/init_session.py
```

This tests all API connections and writes `audit-session-config.json` to the skill root. Resolve any FAIL results before proceeding.

**Step 4 — Score each phase with Claude**

Open Claude Code with this skill active. Claude will run Phase 0 (intake), then score Phases 1–6 in sequence, writing one `.md` scoring table per phase to `Outputs/`. After each phase, Claude runs the post-phase checklist and exports any required CSV files to Google Drive as Google Sheets.

**Step 5 — Validate each phase**

After each phase file is written, run:

```bash
python3 scripts/validate_phase.py "Outputs/ClientName - Phase N - Month Year.md" [expected_rows]
```

Exit 0 = pass. Exit 1 = formatting errors that will break the workbook.

**Step 6 — Run the pipeline**

Open `scripts/extract_data.py` and set the variables at the top, then run:

```bash
python3 scripts/extract_data.py
python3 scripts/generate_gsheet.py
```

`extract_data.py` parses all phase `.md` files and writes `Workbook/workbook_data.json`. `generate_gsheet.py` reads the JSON, creates the Google Sheet in Drive, and saves the URL to `Workbook/workbook_url.txt`.

**Requirements:** Python 3 and `pip install gspread google-api-python-client google-auth-httplib2 google-auth-oauthlib requests`.

---

## File directory

### Core instruction files
| File | Purpose |
|---|---|
| `CLAUDE.md` | Auto-loaded by Claude at session start. All permanent audit rules live here. |
| `SKILL.md` | Full audit workflow — Phase 0 intake through session close. Read this to understand how an audit runs. |
| `CHECKS.md` | Validation gate checklists (L0–L3) and the pre-/compact save protocol. |

### Reference files (loaded on demand)
| File | Purpose |
|---|---|
| `REFERENCE-1.md` | Element definitions and scoring criteria for Phases 1–3. |
| `REFERENCE-2.md` | Element definitions and scoring criteria for Phases 4–6. |
| `REFERENCE-SCHEMA.md` | JSON-LD schema markup templates per page type (homepage, product, FAQ, etc.). |
| `ASSETS.md` | Phase 0 intake checklist — what data to collect from the client before scoring begins. |

### Output templates
| File | Purpose |
|---|---|
| `FORMS-EXPORTS-MANDATORY.md` | Templates for the 9 required Phase 4 CSV files and the Executive Summary. |
| `FORMS-EXPORTS-CONDITIONAL.md` | Templates for conditional files triggered by specific findings (disavow, sitemap delta, etc.). |
| `FORMS-INTERNAL.md` | Internal session tracker templates — Production Plan and Session Log (not client deliverables). |
| `OUTPUTS-WORKBOOK.md` | Workbook column spec, tab structure, and formatting rules. Load before running the pipeline. |
| `OUTPUTS-HTML.md` | HTML report generation spec — page layout, component specs (including priority matrix scatter plot), CSS rules, and dot selection guidance. Load before generating the HTML report. |

### Scripts
| File | Purpose |
|---|---|
| `scripts/api_clients.py` | Shared authentication module — imported by all other scripts, never run directly. |
| `scripts/init_session.py` | Tests API connections, prompts for session config, writes `audit-session-config.json`. Run before Phase 0. |
| `scripts/fetch_data.py` | Auto-fetches data sources via API — Screaming Frog, SE Ranking, PSI, GSC, GA4, Moz, WHOIS. Run on demand per source. |
| `scripts/extract_data.py` | Parses all phase `.md` files and writes `workbook_data.json`. Run before generate_gsheet.py. |
| `scripts/generate_gsheet.py` | Reads `workbook_data.json` and creates the Google Sheet in Drive. Primary workbook deliverable. |
| `scripts/upload_exports.py` | Uploads a CSV or .txt file to Google Drive as a Google Sheet or Google Doc. Run after each Phase 4 export. |
| `scripts/generate_workbook.py` | Reads `workbook_data.json` and builds a local `.xlsx` workbook. Optional backup — not required for standard audits. |
| `scripts/validate_phase.py` | Checks a phase `.md` file for formatting errors before pipeline runs. |
| `scripts/build_schema_tab.py` | Adds the Schema Analysis tab to the workbook if a schema CSV is present. |
| `scripts/activity_log.py` | Generates the audit activity log from the Claude session file. Run last. |

### Examples
| File | Purpose |
|---|---|
| `examples/` | Reference output files showing expected format for workbook tabs and CSV exports. |

---

## API Configuration

All API credentials are stored in `~/.config/digitad/.env` — never inside the skill or audit directory. Copy `.env.example` to that path and fill in:

- `GOOGLE_SERVICE_ACCOUNT_JSON` — absolute path to your Google service account JSON file
- `GDRIVE_MAIN_DIR_ID`, `GDRIVE_EXPORTS_DIR_ID`, `GDRIVE_HTML_DIR_ID` — Google Drive folder IDs
- `SF_HOST`, `SF_PORT` — Screaming Frog API host and port (default: localhost:8775)
- `SE_RANKING_API_KEY` — SE Ranking REST API key (for scripted fetch_data.py; MCP handles interactive use)
- `PSI_API_KEY` — Google PageSpeed Insights API key
- `GSC_SITE_URL` — Google Search Console property URL
- `GA4_PROPERTY_ID` — GA4 property ID
- `MOZ_ACCESS_ID`, `MOZ_SECRET_KEY` — Moz Links API credentials
- `MAJESTIC_API_KEY` — Majestic API key
- `WHOIS_API_KEY` — WHOIS XML API key

Run `python3 scripts/init_session.py` to verify all connections before starting an audit.
