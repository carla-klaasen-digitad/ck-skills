---
name: seo-geo-technical-audit / REFERENCE-SCHEMA.md
load: On demand — read before running the Schema Sub-Phase or Mode C (Schema Deep-Dive Only).
---

# SEO & GEO Audit — Schema Markup Reference

Load this file before running the Schema Sub-Phase. This is a separate standalone deliverable — not part of the main audit scoring table. Run after Phase 4 if schema issues are found in O09, or independently in Mode C (Schema Deep-Dive Only).

---

## STEP 1 — Identify page types

Ask: "Please confirm which page types exist on this site. I will request the current schema markup for each one individually."

Standard page types (adapt to site type):
- Homepage
- Product / service page
- Category / collection page
- Blog article
- Recipe page (if applicable)
- FAQ content (note: FAQPage @type is no longer a Google-supported rich result type — do not implement or recommend FAQPage schema. Assess heading structure for FAQ content instead.)
- About page
- Contact page
- Landing page
- Any other custom page type with unique schema needs

---

## STEP 2 — Collect markup per page type

**Two sources must both be checked — they capture different implementation layers:**

**Source A — JSON-LD (AEM / CMS generated):** Claude fetches this automatically via WebFetch. For each confirmed page type, fetch the live URL and extract all `<script type="application/ld+json">` blocks. Do not ask the user to do this manually — use WebFetch.

**Source B — Microdata (Pillar or other CMS):** Check the audit project folder for a `schema/` directory. Files in this folder (named `[page-type]-[url]-SCHEMA.json`) contain Microdata exports from tools such as Pillar. These must be read and documented alongside the JSON-LD. If the `schema/` folder does not exist, ask: "Do you have Pillar or CMS schema exports? If so, please share the folder path or paste the files."

Document BOTH layers for each page type in column D (Current Schema Markup). Mixed JSON-LD + Microdata implementation is a finding in its own right and must be noted in the Recommendations column.

Do not infer, assume, or generate schema based on partial information. If a page type cannot be fetched (gated, requires login), mark as "Unable to fetch — manual review required."

---

## STEP 3 — Analysis output per page type

For each page type, produce a schema analysis with the following sections in this exact order:

```
PAGE TYPE: [name]
URL: [url if provided]

CURRENT IMPLEMENTATION
[paste current markup exactly as provided by user — do not reformat or truncate]

ASSESSMENT
| Property | Status | Issue |
|---|---|---|
| @type | Correct / Wrong / Missing | [specific detail] |
| @id | Correct / Wrong / Missing | [specific detail] |
| [every relevant property for this schema type] | | |

CRITICAL ERRORS
[numbered list — no prose — one error per line]

MISSING PROPERTIES
[numbered list — no prose — one property per line with brief reason]

RECOMMENDED SCHEMA MARKUP
[full corrected JSON-LD — complete, valid, copy-paste ready]

IMPLEMENTATION NOTES
- Changed @type from [X] to [Y] because: [specific SEO/GEO reason]
- Added [property] because: [specific reason — LLM entity recognition / rich result eligibility / E-A-T signal / etc.]
- Removed [property] because: [reason]
```

Rules for the Recommended Schema Markup section:
- Must be complete and valid JSON-LD — not a partial example
- Must use https:// for all URLs — no relative paths, no protocol-relative URLs
- Must include @context, @type, and @id on every entity
- All @id values must be persistent, unique URLs (typically the page URL with a #fragment for secondary entities)
- Do not include placeholder values — if a value is unknown, note it in Implementation Notes and use a clearly marked placeholder: "[INSERT: product SKU]"

---

## STEP 4 — Write output as a tab in the audit Google Sheet

Add a tab named **"Schema Markup Implementation"** to the existing audit Google Sheet (the same sheet used for the Detailed Technical Audit tab). Do not create a separate spreadsheet.

**Reference example (do not copy content — format only):**
`https://docs.google.com/spreadsheets/d/1u10YOkqM3E7tcKKF_uE196pxrwGjukLpL_y1Yv7AsPY/edit?gid=772030336`

### Column layout (7 columns, A–G)

| Column | Header | Content |
|---|---|---|
| A | Page Type | Page type name — e.g. Homepage, Product Page, Category Page |
| B | Schema markup type | Correct schema type hierarchy using arrow notation — e.g. `collectionpage -> product`, `article; webpage` |
| C | Schema markup implementation | Status: one of `Correct`, `To improve`, `Missing`, `Error`, `Not applicable` |
| D | Current Schema markup | Raw markup from the live page — JSON-LD blocks verbatim + Microdata summary note. Cell is CLIPPED (content is stored in full; user clicks to expand). |
| E | Correct Schema markup | Complete, copy-paste ready corrected JSON-LD. Use `[INSERT: ...]` placeholders for values only the client can supply (logo URL, SKU, BazaarVoice rating, etc.). Cell is CLIPPED. |
| F | Recommendations | Issues bullet list followed by implementation guidance. Plain language, no element codes, no phase references, client-facing. |
| G | Sources | "Schema Validator." followed by newline and "URL: [full page URL]" |

### Row structure — two rows per page type

Each page type produces **two rows**:
1. **Page type row** — all 7 columns populated
2. **Organization reminder row** — A=blank, B=`organization`, C=`To improve`, D=`See Homepage for Organization schema recommendations — applies to all page templates.`, E–G=blank

### Exact formatting spec

Apply via Sheets API — do not use manual formatting. All values are exact:

**Header row:**
- Background: `rgb(0.722, 0.0, 0.110)` — hex #B8001C
- Text: Poppins, size 12, bold, white, CENTER, MIDDLE
- Wrap: WRAP on A/B/C/F/G — CLIP on D/E

**Data rows (all):**
- Font: Poppins, size 10, no bold (except column B which is bold), no background colour
- Row height: 21px
- Column A: CENTER MIDDLE WRAP
- Column B: bold CENTER MIDDLE WRAP
- Column C: CENTER MIDDLE WRAP (status as plain text — no background colour)
- Column D: LEFT MIDDLE CLIP
- Column E: LEFT MIDDLE CLIP
- Column F: LEFT MIDDLE WRAP
- Column G: CENTER MIDDLE WRAP

**Column widths (exact):**
A=267px | B=226px | C=218px | D=426px | E=499px | F=409px | G=273px
---

## SCHEMA TYPE REFERENCE

Apply based on confirmed page type. Use the most specific applicable type — never fall back to generic WebPage when a more specific type exists.

| Page Type | Primary Schema Type | Key Required Properties |
|---|---|---|
| Homepage | WebPage + Organization | Organization: name, url, logo, sameAs (all active social profiles), contactPoint. WebPage: @id, url, name |
| Product page | Product | name, image, description, brand, offers (with priceCurrency and availability), aggregateRating (if reviews exist), sku |
| Category / collection page | CollectionPage | @id, url, name, description, mainEntity (ItemList with child product URLs) |
| Blog article | Article or BlogPosting | headline, author (Person with name and url), datePublished, dateModified, image, publisher (Organization) |
| Recipe page | Recipe | name, image, description, author, datePublished, prepTime, cookTime, totalTime, recipeYield, recipeIngredient, recipeInstructions, nutrition, aggregateRating |
| FAQ page | ~~FAQPage~~ — DEPRECATED: FAQPage @type is no longer supported by Google as a rich result type. Do not implement or recommend. Assess whether FAQ questions use proper heading tags (H2/H3) for LLM extraction instead. |
| About page | AboutPage | @id, url, name, mainEntity pointing to Organization entity |
| Contact page | ContactPage | @id, url, name, mainEntity pointing to Organization with contactPoint (telephone, email, contactType) |
| All pages | BreadcrumbList | itemListElement: array of ListItems, each with position (integer), name, and item (URL) |
| Sitewide (homepage only) | WebSite | url, name, potentialAction: SearchAction (if site search exists, with target and query-input) |

### sameAs — required social profile list

The sameAs array in Organization schema must include all active brand profiles. Standard list to check against:

- Facebook: https://www.facebook.com/[brand]
- Instagram: https://www.instagram.com/[brand]
- X / Twitter: https://twitter.com/[brand] or https://x.com/[brand]
- LinkedIn: https://www.linkedin.com/company/[brand]
- YouTube: https://www.youtube.com/@[brand]
- TikTok: https://www.tiktok.com/@[brand]
- Pinterest: https://www.pinterest.com/[brand] (if active)
- Wikipedia: https://en.wikipedia.org/wiki/[Brand] (if exists)

Ask the user to confirm which platforms are active before populating sameAs. Do not list platforms the brand is not present on.

### JSON-LD quality rules

Every corrected schema block must follow these rules:

1. Use JSON-LD format only — not microdata or RDFa
2. Place in a `<script type="application/ld+json">` tag in the `<head>`
3. Use @graph array on pages with multiple entities (preferred over separate script blocks)
4. All URLs must be absolute with https://
5. datePublished and dateModified must be ISO 8601 format: YYYY-MM-DD
6. aggregateRating must only be included if real reviews exist — never fabricate a rating
7. For Product schema: availability must use a schema.org URL value — e.g. https://schema.org/InStock
8. Never nest entities more than two levels deep without using @id cross-references
9. Schema markup values must never be invented or assumed. If a required property value (e.g. logo URL, SKU, prep time, calorie count) is not directly confirmed by the user or verifiable from the provided exports, omit the property entirely. Do not use placeholder values in deliverable files. If a value is needed but unavailable, note it as a gap in the session log and Production Plan, and ask the user to confirm before the schema file is delivered. The only exception is in draft schema blocks — a clearly marked placeholder (e.g. "[INSERT: product SKU]") is acceptable in a draft but must be resolved before client delivery.

---

## SCHEMA VALIDATION CHECKLIST

After writing all corrected markup, ask: "Would you like me to provide the validation steps for each corrected schema block?"

If yes, provide for each page type:
1. Rich Results Test URL: https://search.google.com/test/rich-results — paste corrected markup, confirm no critical errors
2. Schema.org validator URL: https://validator.schema.org/ — paste corrected markup, confirm no warnings
3. Specific rich result type the corrected schema makes the page eligible for (e.g. Product rich results, FAQ rich results, Recipe rich results)

---

*REFERENCE-SCHEMA.md | seo-geo-technical-audit | Last updated: May 2026*
