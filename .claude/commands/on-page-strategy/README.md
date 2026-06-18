# on-page-strategy

Builds a prioritized SEO on-page content production plan from a keyword research Google Sheet and writes it directly into the Danone production plan.

## What It Does

1. Reads a keyword research Google Sheet for the brand
2. Classifies each URL by content type (category page, product page, recipe, blog)
3. Scores and prioritizes by opportunity (skips pages already ranking top 2)
4. Writes a structured production plan into the brand's tab of the production plan Google Sheet

Priority order: **category pages → product pages → discovery content (recipes/blog)**

## Requirements

- Google Sheets access configured
- Keyword research sheet ready with URLs, keywords, and current ranking data
- Brand tab exists in the production plan

## Quick Start

```
/on-page-strategy
```

The skill will ask for:
1. Brand name
2. Keyword research Google Sheet URL
3. Target month and year
4. Any pages to exclude

## Output

Rows written to the production plan include:
- Heading (H1 recommendation)
- Target keyword
- Secondary keywords
- Content type
- Page URL
- Priority level
- Month / Year

## Notes

- Calls `/global-seo-skill` automatically if any SEO concept needs clarification during execution
- Pages already ranking position 1–2 are skipped to avoid unnecessary rewrites
- Translation/traduction rows are excluded automatically
