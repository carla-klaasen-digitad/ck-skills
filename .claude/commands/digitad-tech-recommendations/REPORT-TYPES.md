# Report Types

Eight report types have been identified from the 2026 production plan. Types marked ✅ have at least one worked example. Types marked 🔲 are documented from the production plan only — worked examples needed before finalizing the spec.

---

## 1. Indexation ✅
**Production plan label:** Indexation - Optimization
**Coverage:** Robots.txt + Sitemap.xml
**Written by:** Digitad

### Audit rows to read
- Sitemap.xml row (look for "Sitemap.xml" in column F, ~row 7)
- Robots.txt row (look for "Robots.txt" in column F, ~row 23)
- Also check indexation error rows (~rows 4–6) for noindex candidates

### Supplementary sheets to request
- Sitemap Indexation Issues sheet (linked in audit column Q)
- Indexed URLs not in Sitemap sheet (linked in audit column Q)
- Robots.txt Recommendation doc (linked in audit column Q)

### Clarifying questions (specific to this type)
1. Is the homepage present in the sitemap? (Verify from data — do not assume.)
2. Should noindex recommendations apply to all pages or only specific categories?
3. Are there tracking parameter URLs that need a Disallow rule?

### Document structure (H2 sections)
1. **Robots.txt** — current state → recommended version (bold NEW disallow rules only) → recommended actions
2. **Sitemap.xml** — current indexed count vs. sitemap count, breakdown by issue type (301 redirects, canonical issues, 404s, not indexed) → recommended actions

### Worked examples
- DNA Robots.txt & Sitemap (doc `124S6pkcA09262CyK-wgv0fYKWxIhleiK7IOCybkCNr8`)
- L+F Robots.txt & Sitemap (doc `1Jwlx8ITlqSpE5EzUZXEVD3WU-hVyozb0xF2xheLiwAo`)

### Key numbers to extract
- Pages in sitemap / pages indexed
- % of sitemap entries with 301 / 404 / canonical issues / not indexed
- Existing robots.txt disallow rules
- Tracking parameter types causing 404s (for new disallow rules)

---

## 2. Canonical / 404 / 301 ✅
**Production plan labels:** Canonical - Optimization · Links - Redirections Errors 404
**Coverage:** Canonical URLs, 404 Errors, 301 Redirection Chains
**Written by:** Digitad (canonical + 301 analysis) / Client implements

### Audit rows to read
- Canonical URLs row (look for "Canonical URLs" in column F, ~row 25)
- 404 Errors / 30X Redirections row (look for "404" in column F, ~row 26)

### Supplementary sheets to request
- Canonical Tags Correction Plan
- Full Redirection Plan (covers canonical redirects + 404 pages + image 404s)
- Redirection Chains sheet

### Clarifying questions (specific to this type)
1. Any unexpected brand URLs in the redirection chains sheet? (e.g. a cross-domain link — include with a note, or exclude?)
2. Should image-level 404s (e.g. /wp-content/uploads/) be included or treated separately?
3. Three H2 sections (Canonical | 404 | 301) or combined differently?
4. Is the canonical flip direction standard or reversed? (Reversed = cleaner URL needs to become canonical, doubled version redirects to it — explain in detail for dev team.)

### Document structure (H2 sections)
1. **Canonical URLs** — count of affected pages, categories of issue (flip, trailing slash/case, tracking params) → recommended actions
2. **404 Errors** — count (%), page-level 404s with redirect targets, image-level 404s (lower priority) → recommended actions
3. **301 Redirection Issues** — chain count, table of all chains (Initial URL | Current Final | Recommended Redirect) → recommended actions

### Worked examples
- DNA Canonical URLs & 404 Errors (doc `1bJT9Pdttqwbgp5vfbbyMQdWAze-yQ8WHTGEpfwcP-oM`)
- L+F Canonical URLs, 404 Errors & 301 Redirection Issues (doc `1tqqLydtM38R3yklVQ1R96B0OZK_PFuWkSSxRoBRUOjM`)

### Key numbers to extract
- Count of pages with non-self-referential canonical tags
- % of pages returning 301 / 404
- Number of redirection chains and hop count
- Whether discontinued products were deleted without redirects

---

## 3. Meta-tags 🔲
**Production plan label:** Meta-tags - Optimization
**Coverage:** Heading structure (H1/H2/H3), meta titles, meta descriptions, breadcrumbs
**Written by:** Digitad

### Audit rows to read
- Meta title rows
- Meta description rows
- Heading structure rows
- Breadcrumb rows
*(Exact row numbers TBD from first worked example — likely rows 30–45 range)*

### Supplementary sheets to request
- Meta title audit sheet (if separate from main audit)
- Heading structure export
- Breadcrumb implementation doc

### Clarifying questions (specific to this type)
1. Is the scope all pages, or priority pages only (homepage, category pages, product pages)?
2. Should the report include specific examples of optimized meta titles/descriptions, or just the structural rules?
3. Are breadcrumbs currently implemented? (Not present → new implementation vs. present → fix existing)

### Document structure (proposed — confirm from first worked example)
1. **Heading Structure** — current state (H1 count per page, hierarchy issues), recommended fixes
2. **Meta Titles** — current issues (too long, duplicate, missing), recommended approach
3. **Meta Descriptions** — current issues, recommended approach
4. **Breadcrumbs** — current state, recommended implementation

### Worked examples
- None yet. First upcoming: International Delight (May 2026), Oikos (May 2026)

---

## 4. Structured Data ✅
**Production plan labels:** Structured Data - New · Structured Data - Modified
**Coverage:** Schema markup (JSON-LD), rich results eligibility, Organization/sameAs entity establishment
**Written by:** Digitad

### Audit rows to read
- SameAs / Organization Schema row (look for "SameAs" in column F)
- Schema Markup Overview row (look for "Schema Markup Overview" in column F)
- Schema Markup Recommendations tab (general) — read in full to validate existing data before building the quarterly tab

### Full process for schema reports

#### Step 1 — Read and validate the general Schema Markup Recommendations tab
Read the existing "Schema Markup Recommendations" tab in the audit spreadsheet. For each Q2-scoped page type, validate the Recommended Schema Markup JSON-LD:
- Check all URLs (sameAs social profiles, logo paths, page URLs) — flag anything uncertain as `[NEEDS VERIFICATION]`
- Check SKU numbers, phone numbers, or specific identifiers — flag if they appear invented or unconfirmed
- Do NOT flag: standard schema.org properties, known founding dates, the brand domain, or standard recipe/product fields

#### Step 2 — Create a quarterly schema tab in the audit spreadsheet
Create a new tab named `Schema Markup Recommendations - Q2` (or Q3/Q4 as appropriate) in the same audit spreadsheet.

**Column structure** (same formatting as the general schema tab + one new column):
`Page Type | Template | Schema Markup Type | Implementation Status | Current Schema Markup | Recommended Schema Markup | Recommendations | Sources`

**Scope:** only include page types addressed in the current quarter's recommendations.

**Row strategy per page type:**
- **Unique pages** (Homepage, About Page): one row, Template column blank, Sources = page URL
- **Template pages** (Recipe, Product, Category, Article): TWO rows:
  - Row 1 — `Template`: Page Type = template name (e.g. "Recipe Page Template"), Template = "Template", Status = "To Implement", Current = blank, Recommended = JSON-LD with `[PLACEHOLDER]` for page-specific values (URL, name, image), Sources = blank
  - Row 2 — `Example`: Page Type = descriptive label (e.g. "Example: Plain Whole Milk Yogurt 32oz"), Template = "Example", Status = "To Implement", Current = original current schema for that page, Recommended = fully specified JSON-LD for that real example page, Sources = page URL
- If structural differences between pages of the same type suggest multiple templates are needed, discuss with the user before writing

**Flagging:** for any cell where data cannot be verified, write `[NEEDS VERIFICATION]` in that cell and append the flag reason to the Recommendations column.

**Formatting:** match the existing general schema tab exactly — same font, header background color, column widths, frozen header row.

#### Step 3 — Write the Google Doc recommendation
One H2 section. **Do NOT include JSON-LD in the doc.** Structure:
- **Problem:** what schema is missing/incorrect by page type — one sentence per type
- **Impact:** why it matters (entity recognition, rich results, LLM visibility)
- **Fix:** numbered list — what to add per page type (e.g. "Add Organization schema with sameAs to the homepage") + final item: validate through Google Rich Results Test
- Italic note: `Full JSON-LD per page type is in the Schema Markup Recommendations tab of the linked audit.`
- Italic link to the **quarterly** tab (not the general one) — use the gid of the Q2 tab created in Step 2

#### Step 4 — After writing the doc
Report any `[NEEDS VERIFICATION]` flags to the user for confirmation before the doc is sent to the client.

**Do not recommend FAQPage schema** — deprecated by Google.

### Clarifying questions (specific to this type)
1. "New" vs "Modified" — is this a first implementation or updating existing schema?
2. Which page types are in scope? — derive from the quarter's recommendation topics

### Worked examples
- Dannon Q2 2026 (doc `1IsGLWLmJJQMrCq8Da0tH7MivCeIV9vbfn_fA83Jkwgc`, Q2 schema tab gid `568915506`)

---

## 5. Performance 🔲
**Production plan label:** Performance - In Depth Analysis
**Coverage:** PageSpeed Insights (desktop/mobile), GTmetrix grade, JS/CSS optimization
**Written by:** Digitad (analysis); Client implements

### Audit rows to read
- PageSpeed Desktop row
- PageSpeed Mobile row
- GTmetrix row
- JavaScript/CSS row

### Supplementary sheets to request
- GTmetrix Performance Report PDF
- PageSpeed Insights exports

### Clarifying questions (specific to this type)
1. Is this a standalone performance report or part of a broader indexation report?
2. Should Core Web Vitals be broken out separately?

### Document structure (from Evian example)
1. **Current Performance** — Desktop score, Mobile score, GTmetrix grade
2. **Key Bottlenecks** — bullet list of primary issues (JS execution, image delivery, render blocking, etc.)
3. **Detailed PageSpeed Insights** — per-metric breakdown with recommended fixes

### Worked examples
- Evian performance report (prior session — doc ID not in current registry)

---

## 6. Images 🔲
**Production plan label:** Images - Optimization
**Coverage:** Image alt tags, image format (WebP/JPEG), image size/compression
**Written by:** Digitad (spec); Client implements

### Audit rows to read
- Image alt tag rows
- Image format/size rows
*(Exact rows TBD)*

### Clarifying questions (specific to this type)
1. Is the scope all images or priority pages only?
2. Are there specific images already flagged in the audit as highest-priority?

### Document structure (proposed)
1. **Alt Tags** — pages missing alt text, recommended approach
2. **Image Format** — non-WebP images, conversion recommendation
3. **Image Size** — oversized images affecting load time, compression targets

### Worked examples
- None yet. First upcoming: SToK (Aug. 2026), Silk (Aug. 2026)

---

## 7. Links 🔲
**Production plan label:** Links - Optimization
**Coverage:** Internal linking strategy, external links, anchor text, breadcrumb links, noopener security
**Written by:** Digitad (analysis); Client implements

### Audit rows to read
- External linking / noopener row
- Internal linking rows
*(Exact rows TBD)*

### Clarifying questions (specific to this type)
1. Is the focus on internal linking strategy, external link security, or both?
2. Are breadcrumbs already covered in a Meta-tags report for this brand?

### Document structure (proposed)
1. **Internal Linking** — orphan pages, anchor text issues, crawlability
2. **External Links** — noopener attribute, link equity leakage
3. **Breadcrumbs** — if not covered in Meta-tags report

### Worked examples
- None yet. First upcoming: Light+Fit (Sept. 2026), Too Good (Sept. 2026)

---

## 8. About Page 🔲
**Production plan labels:** About Page - Creation · About Page - Optimization
**Coverage:** Create a new About page or optimize an existing one
**Written by:** Digitad (spec); Client implements

### Clarifying questions (specific to this type)
1. Does an About page currently exist? (Creation vs. optimization)
2. What entity types should be covered? (Brand history, mission, team, products)
3. Should schema markup (Organization, AboutPage) be included in this report or in a separate Structured Data report?

### Document structure (proposed)
1. **Current State** — existing About page assessment (or confirmation it doesn't exist)
2. **Recommended Page Structure** — section outline with content recommendations
3. **Schema Markup** — Organization / AboutPage schema spec (if in scope)

### Worked examples
- None yet. First upcoming: International Delight (Oct. 2026), Oikos (Nov. 2026)
