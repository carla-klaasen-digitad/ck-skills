# Style Rules

Confirmed stylistic preferences observed from user edits across Evian, Danone North America, and Light + Fit reports (April 2026). These are mandatory — the user has edited finished docs to enforce them.

---

## Content Rules

### SR-01: No Expected Outcome sections
Every time an Expected Outcome section was included, it was deleted. Do not write Expected Outcome paragraphs or sections under any heading name.

### SR-02: Audit cross-reference at top
The first line after the title must be: `*Complete SEO and GEO Audit:*` (italic, user fills in the link).
The user adds this every time — preempt it.

### SR-03: Inline cross-references between reports
When a recommendation references another report, write a short italic placeholder:
`*See [Report Name] for details.*`
Do not re-explain the content of the other report. Do not duplicate findings across docs.

### SR-04: No verbose writing
Every sentence must earn its place. Lead with the key metric or finding — no preamble, no contextual explanation of what a technology is, no padding. If a sentence can be removed without losing information, remove it. The user consistently trims long introductory paragraphs and explanatory filler.
Example: "26 pages have non-self-referential canonical tags." — not "Canonical tags are important for SEO because they tell search engines which version of a page to index. On this site, 26 pages have non-self-referential canonical tags."

### SR-05: Short recommended actions
2–4 items maximum. Only the highest-impact actions. The user removes lower-priority or redundant actions.

### SR-06: "the website" in prose
Never refer to the site by domain name in prose. Use "the website" or "pages on the website."
- Correct: "pages on the website"
- Wrong: "pages on lightandfit.com"

### SR-07: Examples in italics
URL examples and path examples should be set in italics to visually differentiate them from main text.
Example: *https://www.lightandfit.com/light-yogurt/nonfat-yogurt/*

### SR-08: Absolute URLs in examples
Always cite full absolute URLs in examples, not relative paths.
- Correct: *https://www.lightandfit.com/nonfat-yogurt/*
- Wrong: */nonfat-yogurt/*

### SR-09: Tight scope — cross-reference instead of re-including
If a finding could belong in another report (e.g. robots.txt details in a canonical report), remove it and write a cross-reference placeholder. Don't pad reports with out-of-scope content.

### SR-10: Fewer reference document links per section
Pick the most directly actionable source. The user trimmed from two reference docs to one per section. Don't over-reference.

### SR-11: Bold only NEW robots.txt disallow rules
In the recommended robots.txt version, bold only the newly added Disallow rules — not the existing ones — to visually distinguish additions from what is already in place.

---

## Format Rules

### SR-12: Link policy varies by brand (see CLIENT-REGISTRY.md)
- Light + Fit: no links anywhere — user adds manually
- Happy Family: no links anywhere — user adds manually
- Danone North America: links kept
- Others: confirm at start of first report

### SR-18: Three-part bolded structure per section/sub-section
Every section (H2) and sub-section (H3) uses exactly three bolded inline labels followed by brief, dev-team-focused content:
- **Problem:** what the issue is — only the word "Problem" is bolded, not the description after the colon
- **Impact:** why it matters for SEO/performance — only the word "Impact" is bolded
- **Fix:** numbered action list, or italic placeholder if the fix is a linked document (user adds link) — only the word "Fix" is bolded

The old 3-sentence prose paragraph format is replaced by this structure. The "Recommended Actions:" numbered list is removed — actions go directly inside **Fix:**. Confirmed April 2026.

### SR-16: Em-dash limit — maximum 2 per document
Use no more than 2 em-dashes per technical recommendation document in total. Replace excess em-dashes with semicolons, colons, parentheses, or sentence restructuring.

### SR-17: Sitemap maintenance guidelines always included
Every technical recommendation document that covers sitemap or indexation must include a "Sitemap Maintenance Guidelines" bullet list after the recommended actions. Minimum coverage: URL eligibility criteria (200 + self-referencing canonical + no noindex), keeping sitemap current with page changes, removing 404/redirected URLs promptly, https + trailing slash consistency, re-submitting to GSC after structural changes. Confirmed April 2026.

### SR-13: Tables for redirection chains
Use a markdown table for listing redirection chains: Initial URL | Current Final URL | Recommended Redirect.
Tables were kept without user edits — preferred format for structured data.

### SR-19: No full URL lists in the document
Never list individual affected URLs in the Fix section. Instead: describe the issue pattern, state the count, and reference the spreadsheet with an italic placeholder. The user adds the spreadsheet link manually.
- Wrong: bullet list of 15 canonical URLs
- Right: "15 pages have missing trailing slashes. *See SToK - Full Redirection Plan for the complete list.*"
Applies to: canonical redirects, 404 errors, redirection chains, sitemap add/remove lists, and any other per-URL fix list.

---

## What NOT to Include

- Expected Outcome sections
- Long contextual preambles explaining SEO concepts
- More than 4 recommended actions per section
- Domain names in prose
- Findings that belong in a different report (cross-reference instead)
- More than one reference document link per section (unless the second is truly distinct)
