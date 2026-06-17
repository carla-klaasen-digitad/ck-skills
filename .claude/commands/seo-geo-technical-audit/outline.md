# SEO & GEO Technical Audit — Skill Architecture
**Version:** 14.0 | **Last updated:** May 2026

This document maps every component of the skill: .md files and when they load, the script data pipeline, and all external integrations (MCP connectors + API keys via .env).

---

## Diagram 1 — .md File Architecture

Shows which files are loaded, by whom, and at what trigger point.

```mermaid
flowchart TD
    CC["🖥 Claude Code\nSession Start"]

    subgraph ALWAYS["Always Loaded at Session Start"]
        CL["CLAUDE.md\n─────────────────\nSession safety rules S1–S9\nToken efficiency rules 1–18\nMandatory process rules\nPhase element counts (compaction-proof)\nColumn format spec (compaction-proof)"]
        SK["SKILL.md\n─────────────────\nSkill entry point\nOperating modes A–E\nPhase 0 intake workflow\nScoring engine\nPhase workflow (Phases 1–6)\nMissing data detection rules"]
    end

    subgraph ONDEMAND["Loaded On Demand — by trigger"]
        direction TB

        subgraph VALIDATION["Validation Gates"]
            CH["CHECKS.md\n─────────────\nL0 before Phase 0\nL1 after each phase .md\nL2 before extract_data.py\nL3 after generate_gsheet.py\nL4 after all 9 HTML files"]
        end

        subgraph SCORING["Scoring Reference"]
            R1["REFERENCE-1.md\nBefore Phases 1–3\n(Technical / UX / Tools)"]
            R2["REFERENCE-2.md\nBefore Phases 4–6\n(On-Site / Off-Site / GEO)"]
            RS["REFERENCE-SCHEMA.md\nMode C or Schema sub-phase\n(JSON-LD deep-dive)"]
        end

        subgraph FORMS["Export Schemas"]
            FM["FORMS-EXPORTS-MANDATORY.md\nBefore any Phase 4\nmandatory CSV export\n(10 required files)"]
            FC["FORMS-EXPORTS-CONDITIONAL.md\nBefore any conditional export\n(sitemap-delta, disavow,\nrobots.txt, word count)"]
            FI["FORMS-INTERNAL.md\nBefore Production Plan\nor Session Log creation"]
        end

        subgraph OUTPUTS["Output Generation"]
            AS["ASSETS.md\nBefore workbook\nor HTML report"]
            OW["OUTPUTS-WORKBOOK.md\n─────────────────\n19-column sheet spec A–S\nComments for Claude feedback loop\nSheet input — create new vs existing\ngspread pipeline spec"]
            OH["OUTPUTS-HTML.md\nBefore HTML report\n(9 files via generate_html.py)"]
            DE["DESIGN.md\nBefore HTML report\nDesign system authority\n(colour tokens, Tailwind,\ntypography, components)"]
        end
    end

    CC --> CL
    CC --> SK

    SK -->|"L0/L1/L2/L3/L4\nvalidation"| CH
    SK -->|"Before Phase 1–3"| R1
    SK -->|"Before Phase 4–6"| R2
    SK -->|"Mode C or schema flag"| RS
    SK -->|"Phase 4 mandatory exports"| FM
    SK -->|"Sitemap / disavow / robots"| FC
    SK -->|"Production Plan / Session Log"| FI
    SK -->|"Workbook or HTML step"| AS
    SK -->|"After Phase 6\nworkbook gate"| OW
    SK -->|"After workbook confirmed"| OH
    OH -->|"Design authority"| DE
```

---

## Diagram 2 — Script Data Pipeline

Shows how Python scripts connect, what each produces, and what the next step consumes.

```mermaid
flowchart TD
    subgraph PHASE0["Phase 0 — Session Setup"]
        INI["init_session.py\n─────────────────\nTests all API connections\nCollects client name + URL\nValidates Drive folder\nWrites audit-session-config.json"]
        CFG[("audit-session-config.json\ngdrive_main_dir_id\ngdrive_exports_dir_id\ngdrive_html_dir_id")]
    end

    subgraph DATAFETCH["Data Fetching"]
        FD["fetch_data.py\n─────────────────\n--source [source]\n--domain [domain]\n--output [path]\n\nFetches: sf-* exports,\ngsc-coverage/performance/mobile,\nga4-traffic/events,\npsi-desktop/mobile,\nbacklinks-majestic/moz,\nwhois"]
        CSVS[("CSV / JSON exports\ngsc-coverage.csv\ngsc-performance.csv\ngsc-mobile.csv\nga4-traffic.csv\npsi-desktop.json\nsf-*.csv ... etc")]
    end

    subgraph VALIDATION["Phase Validation"]
        VP["validate_phase.py\n─────────────────\nRun at L1 after each phase\npython3 validate_phase.py\n  [phase_file] [expected_rows]\nChecks: column count, row count,\nstatus values, element codes"]
    end

    subgraph SCORING["Phase Scoring (.md files)"]
        PHM[("Phase 1–6 .md files\n─────────────────\n17-column scoring tables\nStatus·Family·Category·\nSub-Category·Analyzed Element·\nDescription·Score·Weight·Tier·\nPriority Score·Priority·Who·\nScore Explanation·Data Analyzed·\nHow to correct·Comments·Sources")]
    end

    subgraph WORKBOOK["Workbook Pipeline"]
        EX["extract_data.py\n─────────────────\nParses all 6 phase .md files\nNormalises scores + family labels\nStrips element codes\nApplies TECHNICAL_TEAM_ELEMENTS\nWrites workbook_data.json"]
        WBJ[("workbook_data.json\n{client, audit_date,\n rows[], phase_scores,\n exec_summary}")]
        GS["generate_gsheet.py\n─────────────────\nReads workbook_data.json\nCreates OR writes to\nexisting Sheet (SHEET_ID+TAB_NAME)\n19-column layout A–S\nBuilds 5 tabs:\n  1. Performances summary\n  2. Detailed Technical Audit\n  3. Schema Analysis\n  4. Sources\n  5. Glossary\nWrites workbook_url.txt"]
        BST["build_schema_tab.py\n─────────────────\nOptional schema tab builder\nParsed from schema-analysis.csv"]
        SHEETURL[("Google Sheet URL\nworkbook_url.txt")]
    end

    subgraph EXPORTS["Phase 4 Drive Uploads"]
        UPL["upload_exports.py\n─────────────────\n--file [path]\n--type sheet\n--folder [gdrive_id]\n--name [display_name]\nUploads CSV → Google Sheet\nReturns Drive URL for Sources col"]
        DRIVEEXPORTS[("Google Drive\nExports folder\n10 mandatory CSVs\n+ conditional files")]
    end

    subgraph HTML["HTML Client Report"]
        GH["generate_html.py\n─────────────────\nReads workbook_data.json\nGenerates 9 HTML files\nusing Tailwind design system\nfrom DESIGN.md tokens\n\nFiles: index.html,\n technical.html, ux.html,\n tools.html, onsite.html,\n offsite.html, geo.html,\n schema.html, about.html"]
        HTMLFILES[("9 HTML files\n/HTML/ directory")]
    end

    subgraph ACTLOG["Session Close"]
        AL["activity_log.py\n─────────────────\nReads session JSONL\nfrom ~/.claude/projects/\nGenerates audit activity log .md\nFinal deliverable"]
        ACTOUT[("Activity Log .md\nFinal deliverable")]
    end

    subgraph SHARED["Shared Module"]
        AC["api_clients.py\n─────────────────\nShared API client factory\nImported by all scripts\nthat need external APIs\n\nExposes:\nget_sf_client()\nget_se_ranking_client()\nget_majestic_client()\nget_google_sheets_client()\nget_google_drive_client()\nget_google_docs_client()\nget_google_sheets_service()\nget_psi_client()\nget_gsc_client()\nget_moz_client()"]
    end

    INI --> CFG
    FD --> CSVS
    CSVS --> PHM
    PHM --> VP
    PHM --> EX
    EX --> WBJ
    WBJ --> GS
    WBJ --> GH
    GS --> SHEETURL
    GS -.->|"optional"| BST
    GH --> HTMLFILES
    PHM --> UPL
    UPL --> DRIVEEXPORTS
    CFG --> GS
    CFG --> UPL
    AL --> ACTOUT

    AC -.->|"imported by"| FD
    AC -.->|"imported by"| INI
    AC -.->|"imported by"| GS
    AC -.->|"imported by"| UPL
```

---

## Diagram 3 — External Integrations

Shows all MCP connectors (used by Claude directly) and Python API keys (used by scripts via api_clients.py).

```mermaid
flowchart LR
    subgraph CLAUDE_MCP["MCP Connectors — used by Claude directly"]
        direction TB

        subgraph GSC_MCP["Google Search Console"]
            MG1["mcp__gsc__\n─────────────────\nPhase 0 Part 0\nProperty access check\nlist_properties\nperformance_overview\nsearch_analytics\nindexing_coverage\ninspect_url"]
            MG2["mcp__gsc2__\n─────────────────\nFallback if mcp__gsc__\ndoes not find property\nSame tools available"]
        end

        subgraph SHEETS_MCP["Google Sheets"]
            MS["mcp__google-sheets__\n─────────────────\nreadSpreadsheet\n→ reads column S\n  (Comments for Claude)\n  during feedback loop\nwriteSpreadsheet\n→ applies adjustments\n  from column S comments"]
        end

        subgraph DOCS_MCP["Google Docs / Drive"]
            MD["mcp__google-docs__\n─────────────────\nlistDriveFiles\nsearchDriveFiles\nreadDocument\n(reference use)"]
            MGD["mcp__gdrive__\n─────────────────\nsearch\n(file lookup)"]
        end

        subgraph GA4_MCP["Google Analytics"]
            MGA["mcp__ga4__\n─────────────────\nga4_run_report\nga4_realtime_report\nga4_performance_overview\n(reference — primary source\nis fetch_data.py API)"]
        end

        subgraph SER_MCP["SE Ranking"]
            MSE["mcp__claude_ai_SE_Ranking__\n─────────────────\nDATA_getDomainKeywords\nDATA_getSerpResults\nDATA_getAiOverview\nPROJECT_getGoogleSearchConsole\nPROJECT_getAuditReport\n(interactive use for\nG01–G02, G07, G26\nSE Ranking AI Visibility)"]
        end
    end

    subgraph PYTHON_API["Python API Clients — scripts/api_clients.py + .env"]
        direction TB

        subgraph SF_API["Screaming Frog REST API"]
            SF["SF_API_URL\n(default: localhost:8775)\n─────────────────\nUsed by: fetch_data.py\ninit_session.py\n\nEndpoints:\n/crawl/start\n/crawl/status\n/export/[tab]"]
        end

        subgraph GOOGLE_API["Google APIs — Service Account"]
            GSA["GOOGLE_SERVICE_ACCOUNT_JSON\n─────────────────\nOne JSON key file\nauthorises all 4 Google services:\n\n• Google Sheets API v4\n  (gspread + batchUpdate)\n• Google Drive API v3\n  (file move, folder, upload)\n• Google Docs API v1\n  (robots.txt, disavow docs)\n• Google Search Console API\n  (coverage, performance, CWV)"]
            GSCENV["GSC_CLIENT_SECRETS_JSON\nGSC_PROPERTY_URL\n─────────────────\nOAuth credentials for\nGSC API (fetch_data.py)\nused when service account\ndoes not have GSC access"]
            DRIVEIDS["Drive Folder IDs\n─────────────────\nGDRIVE_MAIN_DIR_ID\n→ workbook destination\nGDRIVE_EXPORTS_DIR_ID\n→ Phase 4 CSV exports\nGDRIVE_HTML_DIR_ID\n→ HTML report files"]
        end

        subgraph GA4_API["Google Analytics 4"]
            GA4["google.analytics.data_v1beta\n─────────────────\nClient: BetaAnalyticsDataClient\nAuth: service account JSON\nUsed by: fetch_data.py\n\nFetches:\nga4-traffic.csv\nga4-events.csv"]
        end

        subgraph PSI_API["PageSpeed Insights"]
            PSI["PSI_API_KEY\n─────────────────\nGoogle PageSpeed Insights\nAPI v5\nUsed by: fetch_data.py\n\nFetches:\npsi-desktop.json\npsi-mobile.json"]
        end

        subgraph BACKLINKS_API["Backlink APIs"]
            MAJ["MAJESTIC_API_KEY\n─────────────────\nMajestic API\nDomain metrics,\nbacklink counts,\ntrust/citation flow"]
            MOZ["MOZ_ACCESS_ID\nMOZ_SECRET_KEY\n─────────────────\nMoz Links API v2\nHMAC auth\nDomain Authority,\nSpam Score,\nbacklinks-moz export"]
        end

        subgraph SEO_API["SEO Data APIs"]
            SER["SE_RANKING_API_KEY\n─────────────────\nSE Ranking REST API\nUsed by: fetch_data.py\n\nFetches:\nse-ranking-aio.csv\nse-ranking-aivisibility.csv"]
            WHO["WHOIS_API_KEY\n─────────────────\nWHOIS REST API\nUsed by: fetch_data.py\n\nFetches:\nwhois.txt\n(domain age, registrar,\nDNSSEC, expiry)"]
        end
    end

    subgraph PHASE0T["Phase 0 — Trigger Points"]
        P0["Part 0: GSC check\n→ MCP first"]
        P0B["Step 4 inventory\n→ Scripts for missing data"]
    end

    P0 --> MG1
    MG1 -.->|"fallback"| MG2
    P0B --> SF
    P0B --> GSA
    P0B --> GA4
    P0B --> PSI
    P0B --> MAJ
    P0B --> MOZ
    P0B --> SER
    P0B --> WHO
```

---

## Diagram 4 — End-to-End Session Flow

A condensed view showing the full audit journey from session start to final deliverables.

```mermaid
flowchart TD
    START(["Session Start\n/seo-geo-technical-audit"]) --> AUTO

    subgraph AUTO["Auto-loaded"]
        CL2["CLAUDE.md"] --- SK2["SKILL.md"]
    end

    AUTO --> P0T

    subgraph P0T["Phase 0 — Intake"]
        GSC_CHECK["GSC MCP check\n(mcp__gsc__ / mcp__gsc2__)"]
        SF_CHECK["Screaming Frog\nconnection check"]
        INVENTORY["Data source inventory\n+ completeness report"]
        PP["Production Plan .md"]
        GSC_CHECK --> SF_CHECK --> INVENTORY --> PP
    end

    P0T --> PHASES

    subgraph PHASES["Phases 1–6 — Scoring Loop"]
        PH["Load REFERENCE-1 or 2\n↓\nAsk PROMPT USER questions\n↓\nScore all elements\n↓\nWrite phase .md (Rule S2)\n↓\nRun validate_phase.py (L1)\n↓\nWrite session-state.md\n↓\nWatchdog Phase 4+5 checkpoint\n↓\n/compact (Rule S5)"]
    end

    PHASES --> P4GATE

    subgraph P4GATE["Phase 4 Gate"]
        MANDATORY["10 mandatory CSV exports\n+ upload to Drive"]
        SCHEMA_Q["Schema sub-phase?\n(if schema scored Weak/NP)"]
    end

    P4GATE --> P6END

    subgraph P6END["After Phase 6"]
        EXECSUM["Executive Summary .md\n+ Session Log .md"]
        CDR["Conditional deliverables review"]
    end

    P6END --> WB

    subgraph WB["Workbook Pipeline"]
        MODE["Ask: create new sheet\nOR write to existing\n(Sheet ID + Tab Name)"]
        EXP["extract_data.py\n→ workbook_data.json"]
        GSH["generate_gsheet.py\n→ Google Sheet (19 cols A–S)"]
    end

    WB --> FBLOOP

    subgraph FBLOOP["Comments for Claude Feedback Loop"]
        PROMPT2["Prompt user:\nadd notes in column S"]
        WAIT2["Wait for 'comments added'\nor 'no comments'"]
        READ2["mcp__google-sheets__readSpreadsheet\n→ read column S"]
        APPLY2["Apply adjustments\nto sheet cells"]
        WD_S["Watchdog reads column S\n→ skill improvement signals"]
        PROMPT2 --> WAIT2 --> READ2 --> APPLY2 --> WD_S
    end

    FBLOOP --> HTML

    subgraph HTML["HTML Report"]
        GH2["generate_html.py\n→ 9 HTML files"]
    end

    HTML --> CLOSE

    subgraph CLOSE["Session Close"]
        ACT["activity_log.py\n→ audit activity log"]
        WD_CLOSE["Watchdog Phase 4+5\n→ update evolution registry\n→ generate proposals"]
    end

    CLOSE --> DONE(["Deliverables Complete"])
```

---

## Quick Reference — File Load Matrix

| File | Loaded by | Trigger | Contents |
|---|---|---|---|
| CLAUDE.md | Claude Code | Auto (session start) | Safety rules, token rules, process rules, column spec |
| SKILL.md | Claude Code | Auto (session start) | Main workflow, scoring engine, modes, phase flow |
| CHECKS.md | SKILL.md | L0/L1/L2/L3/L4 gates | Validation checklists at 5 pipeline points |
| REFERENCE-1.md | SKILL.md | Before Phase 1, 2, or 3 | Element scoring guides for Technical / UX / Tools |
| REFERENCE-2.md | SKILL.md | Before Phase 4, 5, or 6 | Element scoring guides for On-Site / Off-Site / GEO |
| REFERENCE-SCHEMA.md | SKILL.md | Mode C or schema flag | Schema JSON-LD deep-dive spec |
| FORMS-EXPORTS-MANDATORY.md | SKILL.md | Before any Phase 4 export | 10 mandatory CSV schemas (title tags, redirects, etc.) |
| FORMS-EXPORTS-CONDITIONAL.md | SKILL.md | Before conditional export | Sitemap-delta, disavow, robots.txt, word count schemas |
| FORMS-INTERNAL.md | SKILL.md | Production Plan or Session Log | Internal tracking file schemas |
| ASSETS.md | SKILL.md | Before workbook or HTML | Site-type weight table, brand assets, score matrix |
| OUTPUTS-WORKBOOK.md | SKILL.md | Workbook generation gate | 19-column spec, feedback loop, sheet input options |
| OUTPUTS-HTML.md | SKILL.md | HTML report gate | HTML report structure, 9-file spec |
| DESIGN.md | OUTPUTS-HTML.md | Before HTML generation | Tailwind tokens, typography, component rules |
| README.md | Human only | Reference | Operator guide, setup instructions |

---

## Quick Reference — Script Dependency Matrix

| Script | Imports | Reads | Writes | External API |
|---|---|---|---|---|
| api_clients.py | os, requests, dotenv | .env file | — | All APIs (factory) |
| init_session.py | api_clients, json, os | .env, CLI args | audit-session-config.json | SF, Google Drive, GSC, GA4 |
| fetch_data.py | api_clients, csv, json | .env, --source args | CSV/JSON exports | SF, SE Ranking, PSI, GSC, GA4, Majestic, Moz, WHOIS |
| validate_phase.py | json, re, os | phase .md file | validation report | None |
| extract_data.py | json, re, os | phase 1–6 .md files | workbook_data.json | None |
| generate_gsheet.py | api_clients, gspread, json | workbook_data.json, audit-session-config.json | Google Sheet, workbook_url.txt | Google Sheets API, Drive API |
| build_schema_tab.py | csv, json | schema-analysis.csv | schema tab in sheet | Google Sheets API |
| upload_exports.py | api_clients | CSV files | Google Drive (Sheets) | Google Drive API, Sheets API |
| generate_html.py | json, os, re | workbook_data.json | 9 HTML files | None |
| activity_log.py | json, os, re | JSONL session files | activity log .md | None |

---

## Quick Reference — API Key / .env Variables

| Variable | Used by | Service | Purpose |
|---|---|---|---|
| GOOGLE_SERVICE_ACCOUNT_JSON | api_clients.py | Google APIs | Path to service account JSON — authorises Sheets, Drive, Docs, GSC |
| GSC_CLIENT_SECRETS_JSON | init_session.py, fetch_data.py | Google Search Console | OAuth fallback for GSC API |
| GSC_PROPERTY_URL | fetch_data.py | Google Search Console | Target property for data fetches |
| GDRIVE_MAIN_DIR_ID | generate_gsheet.py | Google Drive | Folder ID for workbook |
| GDRIVE_EXPORTS_DIR_ID | upload_exports.py | Google Drive | Folder ID for Phase 4 CSV exports |
| GDRIVE_HTML_DIR_ID | upload_exports.py | Google Drive | Folder ID for HTML report |
| SF_API_URL | api_clients.py | Screaming Frog | REST API base URL (default: localhost:8775) |
| SE_RANKING_API_KEY | api_clients.py | SE Ranking | API key for keyword + AI visibility data |
| MAJESTIC_API_KEY | api_clients.py | Majestic | Backlink domain metrics |
| MOZ_ACCESS_ID | api_clients.py | Moz Links API v2 | Domain Authority, Spam Score |
| MOZ_SECRET_KEY | api_clients.py | Moz Links API v2 | HMAC auth partner key |
| PSI_API_KEY | api_clients.py | PageSpeed Insights | Core Web Vitals + performance scores |
| WHOIS_API_KEY | api_clients.py | WHOIS REST API | Domain age, registrar, DNSSEC |

---

*outline.md | seo-geo-technical-audit | Version 14 | May 2026*
