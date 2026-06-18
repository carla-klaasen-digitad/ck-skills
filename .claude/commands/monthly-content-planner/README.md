# monthly-content-planner

Runs the monthly on-site content brief creation workflow for all approved brands. Reads the production plan, creates a Google Doc brief per row, generates optimised content via Claude, and emails a summary to the analyst.

## What It Does

For each approved brand with rows due in the current month:

1. Reads eligible rows from the production plan Google Sheet
2. Routes each row to the correct workflow (optimization, creation with context, or fresh creation)
3. Creates a Google Doc brief from the brand template
4. Scrapes the existing page (if a URL exists)
5. Fact-validates claims against the live brand website
6. Generates optimised content using Claude (Opus)
7. Appends ORIGINAL + OPTIMISED sections to the brief doc
8. Writes the doc link back to the production plan
9. Sends a summary email to the analyst

## Requirements

- Google Sheets and Google Drive access configured (OAuth credentials)
- `ANTHROPIC_API_KEY` set in `.env`
- Brand guidelines files present and status set to `Approved` in `all_skills/content-writing/guidelines/`
- Production plan ID set in skill configuration (`PRODUCTION_PLAN_ID`)

## Quick Start

Run for the current month, all approved brands:

```
/monthly-content-planner
```

## Options

```
# Specific month (back-fill)
/monthly-content-planner month=April year=2026

# Specific brands only
/monthly-content-planner brands=Oikos,Silk,ID

# Combined
/monthly-content-planner month=May year=2026 brands=Oikos,Silk
```

## Output

- One Google Doc brief per eligible row, created in the brand's monthly Drive folder
- Doc link written to column N of the production plan
- Row status updated to "Writing (Digitad)"
- Summary email sent to `carla.klaasen@digitad.ca`

## Content Workflows

| Type | Behavior |
|------|----------|
| Optimization | Scrapes existing page → generates optimised version with `[U]...[/U]` markers for every change |
| Creation with context | Scrapes existing page for tone reference → writes fresh content |
| Creation only | No scrape → writes from scratch using keyword + heading |

## Brand Configuration

Each brand needs these fields in its guidelines file to be picked up by the skill:

| Field | Required |
|-------|----------|
| Status: Approved | Yes |
| Tab Name | Yes |
| On-Site Content Folder (Drive URL) | Yes |
| Content Brief Template (Doc URL) | Yes |
| Neuronwriter Project URL | Optional |

## Schedule

Runs automatically on the first Monday of each month at 9:00 AM.
