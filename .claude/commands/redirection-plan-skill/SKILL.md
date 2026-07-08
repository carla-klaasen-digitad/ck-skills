---
name: redirection-plan-skill
description: Use when a redirection plan needs to be built for 404 errors, redirect chains, or canonical issues. Can be invoked directly by the user or called automatically by the seo-geo-technical-audit at T06/T07/T05. Accepts two input files (broken URLs + live URLs from Screaming Frog or GSC), applies a 6-tier semantic matching pipeline to assign actions and redirect targets, validates all targets live via HTTP, and outputs a Google Sheet. Trigger phrases: "build a redirect plan", "redirection plan", "fix 404s", "fix redirect chains", "404 redirect plan", "redirect mapping", "/redirection-plan-skill".
model: sonnet
allowed-tools: Bash, Read, Write, Edit, mcp__claude_ai_Google_Drive__read_file_content, mcp__claude_ai_Google_Drive__create_file, mcp__claude_ai_Google_Drive__search_files
---

# Redirection Plan Skill

Standalone skill for building complete redirection plans. Takes a list of broken or problematic URLs, finds the best redirect target for each using a 6-tier matching pipeline, validates all targets live via HTTP, and delivers a Google Sheet.

Can be invoked directly by the user or called automatically by the seo-geo-technical-audit skill at Phase 4 (T06, T07, T05).

---

## When This Skill Activates

- User types `/redirection-plan-skill`
- User says "build a redirect plan", "fix 404 errors", "redirect mapping", "redirection plan", "fix redirect chains", "404s to fix", "redirect audit"
- seo-geo-technical-audit invokes this skill at Phase 4 after scoring T06 (404 errors), T07 (redirect chains), or T05 (canonical issues)

---

## Inputs

Two files are required. Accept a local file path or a Google Drive URL/file ID for each.

| File | What it contains | Common source |
|------|-----------------|---------------|
| **Broken URLs file** | URLs returning 404, in redirect chains, or with canonical issues | Screaming Frog → Response Codes → 4xx export; GSC Coverage → Not found; or the audit's existing 4xx list |
| **Live URLs file** | All currently-live 200-response URLs on the site | Screaming Frog → All URLs → filter Status 200; or site XML sitemap |

**Minimum required columns — broken URLs file:**

| Column | Accepted names | Required |
|--------|---------------|---------|
| URL | `Address`, `URL`, `Source URL` | Yes |
| HTTP status | `Status Code`, `Status`, `HTTP Status` | Yes |
| Inbound internal links | `Inbound Internal Links`, `Internal Links` | Optional — used for priority |
| Inbound external backlinks | `Inbound External Backlinks`, `Backlinks`, `External Backlinks` | Optional — used for priority |

**Minimum required columns — live URLs file:**

| Column | Accepted names | Required |
|--------|---------------|---------|
| URL | `Address`, `URL` | Yes |
| Page title | `Title 1`, `Title`, `Page Title` | Optional — improves semantic matching |

**When called from the audit:** the audit passes `{AUDIT_DIR}/Outputs/CSV/{CLIENT_NAME}-4xx-export.csv` and `{AUDIT_DIR}/Outputs/CSV/{CLIENT_NAME}-live-urls.csv` directly. No user input needed.

---

## Output

**Default:** Google Sheet named `[Client/Brand] — Redirection Plan — [YYYY-MM-DD]`

Upload to the same Google Drive folder as the audit. Apply standard formatting: Poppins font, rows 1–3 blank, row 4 header row (bold), conditional formatting on Priority column (High = red, Medium = orange, Low = green). No other row colors.

**Output columns:**

| Column | Values |
|--------|--------|
| URL | The broken/problematic URL — full absolute URL |
| Current Status | HTTP code or chain (e.g. `301 > 301 > 404`) |
| Current Redirect Target | Existing hop destination if any — blank if none |
| Issue Type | `404` / `Redirect Chain` / `Canonical` / `Soft 404` |
| Action | See Action Values below |
| Redirect Target | Target URL for redirect actions — blank for non-redirect actions — full absolute URL |
| Target Status | `VALIDATED (200)` / `INVALID (404)` / `REDIRECT CHAIN` / `NOT CHECKED` |
| Match Confidence | `Exact` / `Chain` / `Keyword` / `Semantic` / `Category` / `Fallback` / `REVIEW` |
| Priority | `High` / `Medium` / `Low` |
| Notes | **Required for T3/T4/T5/T6 matches** — always write why this target was chosen (e.g. "Keyword match: both slugs share 'vanilla' + 'greek'"; "Semantic: discontinued light line → closest equivalent is regular nonfat"; "Category fallback: no equivalent product found in live URLs"). For T1/T2: leave blank unless flagging an issue. |

---

## Action Values

| Action | When to use |
|--------|-------------|
| `301 Redirect` | All broken product pages, old content, malformed URLs, discontinued products, old domain URLs, campaign pages — any URL that was or should have been a real page |
| `Flatten Redirect Chain` | URL is in a 2+ hop redirect chain — issue a direct 301 to the final 200 destination, bypassing intermediate hops |
| `Block via robots.txt` | Parameterized or filtered URLs only (e.g. `?sort=price&color=blue`, `?page=2`, `?utm_source=`) OR staging/dev subdomain URLs (`dev.`, `staging.`, `test.`, `uat.`) |
| `Soft 404 — Leave as-is` | CMS-controlled soft 404 — content is pending or intentionally absent — no redirect equity at stake |
| `No action` | URL resolves correctly at 200 — false positive in import |
| `Investigate` | Ambiguous signals — insufficient data to assign action — flag for manual review |

**Default rule:** when in doubt, assign `301 Redirect`. The matching pipeline will find the best available target.

---

## Phase 0 — Input Validation

1. Confirm both input files are provided. If either is missing, ask before proceeding.
2. Read both files. For Google Drive inputs: use `mcp__claude_ai_Google_Drive__read_file_content`.
3. Confirm required columns are present in each file. If a required column is missing, ask the user which column contains that data — do not assume.
4. Count total rows in each file. Log: `[N] broken URLs to process | [N] live URLs available for matching`.
5. Check if a sitemap XML is available — if the live URLs file header indicates a sitemap source, note it. If the user has a sitemap URL, fetch it as a supplementary live URLs source.
6. Identify the client/brand name for the output sheet. If called from the audit, derive from the file naming convention. If standalone, ask the user.

---

## Phase 1 — Action Classification

For each row in the broken URLs file, classify the **Issue Type** and assign an **Action**.

### Step 1.1 — Issue Type assignment

| HTTP status | Issue Type |
|-------------|------------|
| 404, 410 | `404` |
| Redirect chain with ≥ 2 hops (e.g. `301 > 301 > 200`) | `Redirect Chain` |
| 200 but canonical points to different URL | `Canonical` |
| 200 but page has no real content (CMS placeholder) | `Soft 404` |

### Step 1.2 — Direct action assignment (no matching needed)

Classify these patterns immediately before running the matching pipeline:

| Pattern | Action |
|---------|--------|
| URL contains query string with filter, sort, pagination, or tracking params (`?color=`, `?sort=`, `?page=`, `?utm_`, `?gclid=`, `?fbclid=`) | `Block via robots.txt` |
| URL hostname contains `dev.`, `staging.`, `test.`, or `uat.` | `Block via robots.txt` |
| URL returns 200 (false positive in the import) | `No action` |
| URL is in a redirect chain ending at 200 with ≥ 2 hops | `Flatten Redirect Chain` — resolve in Phase 2 T2 |
| URL is in a redirect chain that never resolves to a 200 (chain ends in 404 or loops) | `301 Redirect` — treat as a standard broken URL; run the full T1–T6 matching pipeline |
| URL is a CMS soft 404 (returns 200, confirmed as placeholder) | `Soft 404 — Leave as-is` |

All remaining URLs: assign `301 Redirect` and continue to Phase 2.

---

## Phase 2 — Target Matching (301 Redirect rows only)

Run the matching pipeline in strict tier order — stop at the first successful match. See REFERENCE.md for full decision logic and edge case handling.

### Pre-processing — slug parsing

Before matching any URL:
1. Extract the URL path. Split by `/` and `-`.
2. Remove stop words: the, and, or, a, an, of, for, with, from, to, in, on, at, by, is, are, be, was, were, has, have, had, this, that, these, those, free, dairy, plant, based, new, all, buy, shop, get, our, your, my.
3. Identify the **type anchor** — the first substantive noun describing a product category. Common type anchors: `yogurt`, `ice-cream`, `creamer`, `beverage`, `milk`, `protein`, `probiotic`, `frozen`, `smoothie`, `snack`, `recipe`. See REFERENCE.md for the full type anchor table.
4. If no type anchor can be identified: skip the type constraint and match against all live URLs.

### Type constraint

All tiers except T5 and T6 are **type-constrained**: only match against live URLs that share the same type anchor.

Cross-type matches are blocked: `yogurt` URLs do not match `ice-cream` URLs; `creamer` URLs do not match `beverage` URLs.

Within-type subcategory bridging is allowed: `light yogurt` → `regular yogurt`, `nonfat` → `Greek`, `coconut milk yogurt` → `almond milk yogurt`, `no-added-sugar` → `unsweetened`. See REFERENCE.md for full allowed bridging table.

### Matching tiers

**T1 — Exact path match**
Check if the same path exists in the live URLs list at 200. Try with and without trailing slash.
Match confidence: `Exact`

**T2 — Chain resolution**
If the URL's Current Status shows a redirect chain, extract the final 200-response URL from the chain. Use that as the Redirect Target.
Match confidence: `Chain`
Note: also applied to rows classified as `Flatten Redirect Chain` in Phase 1.

**T3 — Slug keyword match**
Parse live URLs into keyword sets (same stop-word removal). Find live URLs where:
- The broken URL's type anchor appears in the live URL slug, AND
- At least **two** non-stop-word tokens overlap in total (the type anchor counts as one — you need at least one additional specific qualifier word, not just another generic term).

If multiple candidates: rank by total keyword overlap count, pick the highest.

**Minimum overlap guard:** if the best T3 candidate matches only on the type anchor with no specific qualifier overlap (e.g. the only shared token is `yogurt`), the match is too loose — skip to T4 instead.

Match confidence: `Keyword`

**T4 — Semantic match**
Apply semantic judgment: identify what product or content the broken URL represented, then find the closest live URL in the same product type. Use page titles from the live URLs file if available — they improve match quality.

Subcategory bridging is allowed within the same type. See REFERENCE.md for examples.
Flag as `REVIEW` if the match bridges distinctly different sub-brands or audiences.

**T4 fail-fast condition:** if the brand has discontinued an entire product line with no equivalent remaining in the live URLs (e.g. all flavors of a discontinued sub-brand are gone), do not force a semantic stretch to an unrelated product. Prefer T5 (parent category) over a wrong T4 target. A correct fallback is better than a plausible-but-wrong recommendation.

Match confidence: `Semantic`

**T5 — Parent category match**
Find the closest parent path in the live URLs list. Try progressively shorter path prefixes:
- `/products/yogurt/vanilla-nonfat/` → try `/products/yogurt/` → try `/products/` → use first live match found.
Match confidence: `Category`

**T6 — Fallback**
Auto-detect the most relevant fallback from the domain structure:
1. If a category-level live URL exists that is thematically related: use it.
2. Otherwise: use the site homepage (`/`).
Always add to Notes: "Fallback match — verify manually."
Match confidence: `Fallback`

---

## Phase 3 — Target Validation

For every row with a populated Redirect Target:

1. Run: `curl -s -o /dev/null -w "%{http_code}" --max-time 10 --location "[URL]"`
2. Map result to Target Status:

| curl result | Target Status | Action |
|-------------|---------------|--------|
| `200` | `VALIDATED (200)` | No change needed |
| `301` or `302` | `REDIRECT CHAIN` | Follow chain to final 200, update Redirect Target to final destination |
| `404` or `410` | `INVALID (404)` | Add to Notes: "Target returns 404 — manual correction required". Set Match Confidence to `REVIEW` |
| Timeout / error | `NOT CHECKED` | Add to Notes: "Validation timed out — verify manually" |

3. Batch curl calls in groups of 25. Pause and log progress between batches.
4. If more than 20% of targets return non-200: warn the user — the site may be blocking automated requests. Offer to mark all remaining as `NOT CHECKED`.

---

## Phase 4 — Priority Assignment

| Priority | Condition |
|----------|-----------|
| `High` | Inbound external backlinks > 0, OR inbound internal links > 5, OR URL appears in the sitemap |
| `Medium` | Inbound internal links 1–5, OR URL is in a redirect chain |
| `Low` | No inbound links, not in sitemap — structural cleanup only |

If backlink data was not provided: assign `Low` as default and add to Notes: "Priority may change when backlink data is available."

---

## Phase 5 — Output

1. Build the complete output table with all 10 columns.
2. Confirm output sheet name with the user (or derive from audit context): `[Client/Brand] — Redirection Plan — [YYYY-MM-DD]`.
3. Upload to Google Drive as a Google Sheet using `mcp__claude_ai_Google_Drive__create_file`.
4. Apply formatting: Poppins 10pt, rows 1–3 blank, row 4 header (bold, light grey fill), Priority conditional formatting (High = red background, Medium = orange, Low = green), no other row colors.
5. Return the Google Sheet URL to the caller.

**When called from the audit:** return the URL and record it in:
- The Sources column of the T06 row in the phase .md file
- The Sources column of the T07 row in the phase .md file
- The Production Plan as `[x]` complete for the redirect-plan deliverable

---

## Standalone Invocation

When invoked directly (not from the audit):

1. Ask: "Please provide two files: (1) your list of broken URLs — from Screaming Frog 4xx export or GSC Coverage — and (2) your list of live site URLs — from Screaming Frog All URLs filtered to 200 responses, or a sitemap XML."
2. Accept file paths or Google Drive links.
3. Ask: "What is the client or brand name for the output sheet?"
4. Run Phases 0–5 and return the Google Sheet URL.

---

## Error Handling

| Condition | Response |
|-----------|----------|
| Either input file is missing | Ask for it before proceeding — do not start without both files |
| Required column is missing from input | Ask which column contains that data — do not assume or skip |
| curl validation fails for > 20% of targets | Warn: site may block automated requests. Offer to skip validation and mark all as `NOT CHECKED` |
| Live URLs file has < 10 rows | Warn: matching quality will be poor. Ask user to provide a fuller export |
| Type anchor unresolvable for > 30% of broken URLs | Warn: consider providing page titles in the live URLs file to improve semantic matching |
| Redirect Target is the same as the broken URL | Flag as `REVIEW` — circular redirect risk |

---

*redirection-plan-skill v1.0 — 2026-06-30*
