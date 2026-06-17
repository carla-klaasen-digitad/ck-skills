---
name: seo-geo-technical-audit / FORMS-INTERNAL.md
load: On demand — read before creating the Production Plan (Phase 0) or updating the Session Log. These files are internal session-management tools and are not client deliverables.
---

# SEO & GEO Audit — Internal Session Files

These files are never shared with the client. They exist to manage session continuity, track deliverable status, and capture analyst decisions throughout the audit.

---

## FILE 17 — Production Plan

Trigger: Mandatory. Created immediately after the Phase 0 Audit Completeness Report, before Phase 1 begins. Do not proceed to Phase 1 without it.
Filename: [CLIENT] - Production Plan - [Month Year].md

The Production Plan is a live tracker of all anticipated output files for the session. Create it before Phase 1 and keep it updated throughout — it is not a retrospective.

Status markers:
- `[ ]` not started
- `[~]` in progress
- `[x]` complete
- `[!]` blocked (note reason inline)

Template:

```
# Production Plan — [CLIENT] — [Month Year]

Created: [date] | Audit URL: [url] | Model: [model]

## Mandatory Phase 4 Outputs
- [ ] Title Tag Issues .csv
- [ ] Meta Description Issues .csv
- [ ] H1 Issues .csv
- [ ] Heading Hierarchy Issues .csv
- [ ] Image Alt Tag Issues .csv
- [ ] Canonical Tag Issues .csv
- [ ] Redirect Plan .csv
- [ ] Internal Linking Report .csv
- [ ] External Linking Report .csv

## Conditional Outputs (add as triggered)
- [ ] [filename] — [trigger condition]

## Session Close Outputs
- [ ] Executive Summary .md
- [ ] Session Log .md
- [ ] Workbook (Google Sheet) — URL: [fill when generated]
- [ ] Activity Log .md (generated via scripts/activity_log.py)
```

Add rows to Conditional Outputs whenever a scoring finding triggers a new file. Note the trigger condition inline. Update status markers throughout the session as files are written.

---

## FILE 18 — Session Log

Trigger: Mandatory. Created at session start (Phase 0) and updated throughout. Exported as a .md file before workbook generation.
Filename: [CLIENT] - Session Log - [Month Year].md

The Session Log is a running record of decisions, data gaps, deferred items, and key findings made during the audit. It is not a phase scoring table — it captures context that does not belong in the workbook.

Template:

```
# Session Log — [CLIENT] — [Month Year]

## Session Details
| Field | Value |
|---|---|
| Client | [name] |
| Site URL | [url] |
| Audit Date | [date] |
| Model | [model] |
| Writing Style | [A / B / C — confirmed at Phase 0] |
| Workbook Format | Google Sheet — [URL when available] |

## Data Availability
| Source | Status | Notes |
|---|---|---|
| [source name] | Available / Missing / Partial | [any notes] |

## Key Decisions
| Phase | Decision | Rationale |
|---|---|---|
| Phase 0 | [decision] | [why] |

## Data Gaps & Deferred Items
| Item | Reason | Action Required |
|---|---|---|
| [element or file] | [why it's a gap] | [what is needed and from whom] |

## HTML Report Configuration
| Field | Value |
|---|---|
| Overall score (computed) | [N]/100 |
| Overall score (override) | [N]/100 — override applied / None |
| Priority matrix dots | [N] dots selected — list labels here |
| Data sources | [list confirmed sources from Phase 0] |
| Digitad logo | [absolute file path or URL] |
| Client logo | [absolute file path or URL] |
| generate_html.py run | [ ] not yet / [x] complete |
| Drive Export URLs confirmed | [ ] all Phase 4 export Sheets uploaded and URLs recorded |

## Skill Improvement Notes
| Issue | Impact | Recommended Fix |
|---|---|---|
| [observed problem with skill or process] | [effect on output quality] | [suggested change] |
```

Add entries throughout the session. Key decisions include weight adjustments, style choices, scope changes, and any deviation from the standard phase workflow. Skill Improvement Notes capture gaps, ambiguities, or failures in the skill itself — these feed post-audit meta-analysis.

---

*FORMS-INTERNAL.md | seo-geo-technical-audit | Version 12 | April 2026*
