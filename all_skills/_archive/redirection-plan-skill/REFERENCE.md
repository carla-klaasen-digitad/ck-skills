# REFERENCE — Redirection Plan Skill

Full decision logic, type anchor tables, allowed bridging rules, and edge case guidance.

---

## Action Decision Tree

```
Is the URL a parameterized/filtered URL or on a staging/dev subdomain?
  YES → Block via robots.txt
  NO ↓

Is the URL in a redirect chain with ≥ 2 hops ending at 200?
  YES → Flatten Redirect Chain
  NO ↓

Does the URL return 200 (false positive)?
  YES → No action
  NO ↓

Is this a CMS soft 404 (returns 200, no real content)?
  YES → Soft 404 — Leave as-is
  NO ↓

Default → 301 Redirect → proceed to target matching
```

---

## Type Anchor Table

The type anchor is the first substantive product category noun extracted from the URL slug.

| Type anchor keywords | Canonical type | Blocked cross-matches |
|---------------------|---------------|----------------------|
| `yogurt`, `yoghurt` | yogurt | ice-cream, frozen, creamer, beverage, protein-shake |
| `ice-cream`, `icecream`, `frozen`, `dessert`, `gelato`, `sorbet` | frozen dessert | yogurt, creamer, beverage |
| `creamer`, `creamers`, `coffee-creamer` | creamer | yogurt, frozen, beverage |
| `milk`, `beverage`, `drink`, `oatmilk`, `almondmilk`, `coconutmilk`, `soymilk` | beverage | yogurt, ice-cream, creamer (unless dual-category) |
| `protein`, `protein-shake`, `protein-drink` | protein | yogurt (unless product is explicitly protein yogurt) |
| `probiotic` | infer from path context — yogurt or beverage | cross-match only within the inferred category |
| `recipe`, `recipes` | content | match to /recipes/ or /vegan-recipes/ category |
| `blog`, `article`, `news` | content | match to /blog/ or /news/ category |
| `where-to-buy`, `store-locator`, `find` | utility | match to /where-to-buy/ or site homepage |
| `contact`, `about`, `faq`, `careers` | utility | match to equivalent utility page |
| `coupon`, `promotion`, `offer` | promotional | match to /coupons/ or site homepage — no cross-match |

**When no type anchor is found:** skip the type constraint entirely and match against all live URLs.

---

## Allowed Within-Type Subcategory Bridging

Within the same type anchor, these subcategory bridges are permitted at T3 and T4:

### Yogurt
| From | To | Allowed |
|------|----|---------|
| `nonfat` | `greek` | Yes |
| `light` | `regular` | Yes |
| `light` | `nonfat` | Yes |
| `no-sugar-added` | `unsweetened` | Yes |
| `coconut-milk yogurt` | `almond-milk yogurt` | Yes — same category, different base |
| `kids yogurt` | `adult yogurt` | Flag REVIEW — different audience |
| `pro yogurt` | `standard yogurt` | Flag REVIEW — different product line |

### Frozen Desserts
| From | To | Allowed |
|------|----|---------|
| `no-sugar-added ice cream` | `regular ice cream` | Yes |
| `mini bars` | `full bars` | Yes |
| `cocowhip` | `whipped cream alternative` | Yes |
| `ice cream bars` | `pints` | Flag REVIEW — different format |

### Beverages
| From | To | Allowed |
|------|----|---------|
| `coconut milk` | `almond milk` | Yes |
| `oat milk` | `almond milk` | Yes |
| `unsweetened` | `original` | Yes |
| `barista edition` | `regular` | Yes |
| `beverage` | `creamer` | No — blocked cross-type |

---

## Match Confidence — When to Flag REVIEW

Add `REVIEW` to the Match Confidence column (overrides the tier label) when:

- T3/T4: keyword overlap is only 1 word and that word is generic (e.g. only `yogurt` matches, not a specific product qualifier)
- T4: the match bridges different sub-brands with different audiences (e.g. kids product → adult product)
- T4: the match bridges significantly different product formats (bars → pints)
- T5: the category page itself is a redirect or returns non-200
- T6: any fallback match — always flag
- T1/T2/T3: the Redirect Target returns non-200 at validation time

When REVIEW is set: add a specific explanation to Notes so the analyst knows exactly what to verify.

---

## Priority Rules — Full Logic

| Condition | Priority |
|-----------|----------|
| Inbound external backlinks confirmed (any count > 0) | High |
| URL present in XML sitemap | High |
| Inbound internal links > 5 | High |
| Inbound internal links 1–5 | Medium |
| URL is in a redirect chain (any depth) | Medium |
| No inbound links, not in sitemap, no chain | Low |
| Backlink data column not provided | Low + Notes: "Priority may change when backlink data is available" |

---

## robots.txt vs 301 — Decision Guide

**Only use `Block via robots.txt` for:**
1. Parameterized/filtered URLs — anything with a query string containing filter, sort, pagination, or tracking parameters
2. Staging or dev subdomain URLs that were accidentally indexed

**Use `301 Redirect` for everything else**, including:
- Old campaign and promotional pages (even with zero SEO equity)
- Discontinued product pages
- Old domain URLs (oikosyogurt.com → oikos.com)
- Malformed slugs or URL typos
- Legacy URL structures after a site migration
- Language subfolder URLs (`/jp/`, `/zh/`, `/fr/`) — redirect to homepage

**Never use `Block via robots.txt` for:**
- URLs that once had real content (even if deleted)
- URLs that appear in external backlinks
- URLs that appear in the sitemap (remove from sitemap separately; still redirect)

---

## Redirect Chain Flattening — Logic

A redirect chain is defined as: A → B → C (≥ 2 hops before reaching a 200).

For chain flattening:
1. Extract the final 200-response URL from the chain (the last URL in the chain).
2. Set the broken URL's Redirect Target to that final 200 URL directly.
3. Set Action to `Flatten Redirect Chain`.
4. Validate the final 200 URL in Phase 3.
5. Add to Notes: "Flattened from [original chain depth]-hop chain via [intermediate URL]."

If the chain ends in 404 (chain never resolves): treat as a standard 404 and run the full T1–T6 matching pipeline instead.

---

## Fallback Hierarchy — Auto-Detection

When no match is found through T1–T4:

**T5 — Parent path auto-detection:**
- Strip the last path segment repeatedly until a live URL is found.
- `/products/yogurt/vanilla-nonfat/` → try `/products/yogurt/` → try `/products/` → try `/`
- Use the first match that exists in the live URLs list.

**T6 — Homepage fallback:**
- Use `https://[domain]/` as the final fallback.
- If a category-level live URL is thematically related and was not found in T5 (e.g. the path structure is non-hierarchical), use it instead of the homepage.
- Always flag T6 matches as `REVIEW` in Match Confidence.

---

## Sitemap Cross-Reference

The live URLs file is the primary source for target matching. The sitemap XML is used as a supplementary check:

1. If a candidate target URL is in the live URLs list but NOT in the sitemap: note in the output. The redirect will work but the target may have lower crawl priority.
2. If a candidate target URL appears in the sitemap but does NOT appear in the live URLs list (Screaming Frog): the sitemap entry may be stale. Flag as `REVIEW` — verify the page is actually live before using it as a target.
3. If both sources confirm the URL at 200: no flag needed.

---

## Output Sheet Naming Convention

Default: `[Client/Brand] — Redirection Plan — [YYYY-MM-DD]`

| Client | Example name |
|--------|-------------|
| Oikos | `Oikos — Redirection Plan — 2026-06-30` |
| So Delicious | `So Delicious — Redirection Plan — 2026-06-30` |
| Dannon | `Dannon — Redirection Plan — 2026-06-30` |
| Silk | `Silk — Redirection Plan — 2026-06-30` |
| International Delight | `International Delight — Redirection Plan — 2026-06-30` |

---

## Audit Integration Reference

When called from the seo-geo-technical-audit:

| Field | Value |
|-------|-------|
| Trigger point | Phase 4, after T06 (404 errors) and T07 (redirect chains) are scored |
| Broken URLs input | `{AUDIT_DIR}/Outputs/CSV/{CLIENT_NAME}-4xx-export.csv` |
| Live URLs input | `{AUDIT_DIR}/Outputs/CSV/{CLIENT_NAME}-live-urls.csv` |
| Output destination | Same Google Drive folder as the audit |
| Audit records | Sheet URL → Sources column of T06 row, T07 row, and Production Plan item 7 |
| Replaces | Manual `[CLIENT_NAME]-redirect-plan.csv` generation in FORMS-EXPORTS-MANDATORY.md FILE 7 |

The skill's Google Sheet output IS the Phase 4 mandatory redirect-plan deliverable. The audit does not separately generate a basic redirect-plan.csv.

---

*redirection-plan-skill REFERENCE v1.0 — 2026-06-30*
