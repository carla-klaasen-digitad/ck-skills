---
name: seo-geo-technical-audit / OUTPUTS-HTML.md
load: On demand — read before generating the HTML client report.
---

# SEO & GEO Audit — HTML Report Generation Spec

---

## PRE-GENERATION CHECKLIST

Before running the HTML report script:
1. The workbook has been generated and confirmed complete — workbook_data.json exists in Workbook/
2. The Executive Summary .md file exists in Outputs/
3. /compact has been run after workbook generation
4. Ask user for both logo files: "Ready to generate the HTML client report. Please confirm: (1) the absolute file path for the Digitad logo, and (2) the absolute file path for the client logo."
5. Confirm the audit root directory path — all file reads and HTML/ output writes are anchored to this path

**Data source for HTML generation — use workbook_data.json exclusively.** Do not re-parse phase .md files. workbook_data.json contains all 114 scored rows in structured JSON — use it as the single source of truth for all element data. Read it with the Read tool. If the file exceeds 40KB, use the Read tool with `offset` and `limit` parameters to read in chunks (never use bash sed or cat).

**Generate each .html file as a separate, foreground task with explicit confirmation between each file.** Do not batch all pages in one generation. Rule S4 applies.

---

## DESIGN REFERENCE — READ BEFORE GENERATING ANY PAGE

The `examples/html-preview/` folder contains the canonical built examples. Read the relevant example file before generating each page — the examples are the authoritative visual and structural reference and resolve any ambiguity in this spec. When the spec and the example conflict, the example takes precedence.

| Example file | Use as template for |
|---|---|
| examples/html-preview/index.html | index.html (overview page) — includes priority matrix scatter plot component |
| examples/html-preview/technical.html | All section pages: technical.html, ux.html, tools.html, on-site.html, off-site.html, geo.html, schema.html |
| examples/html-preview/methodology.html | methodology.html (static content — clone and update client name, date, and element counts) |
| examples/html-preview/schemaexample.html | schema.html use as a template for the way I want the schema.html executed. Don't use the data in this file as it from another client|

Load DESIGN.md for the full design system specification (colour palette, typography scale, surface hierarchy, elevation rules, component rules). The examples implement this design system. Key implementation notes derived from the examples:

- **Fonts**: Plus Jakarta Sans (700, 800) + Inter (400, 500, 600) via Google Fonts. Plus Jakarta Sans is the headline font (`font-headline`); Inter is the body font.
- **Styling**: Tailwind CSS via CDN with a custom `tailwind.config` block in the page `<head>`. All design tokens are defined in the Tailwind config — do not use inline CSS for colours or spacing where a Tailwind token exists.
- **Dark backgrounds**: Use `#1a1c1c` (the `on-surface` token), never `#000000` or `#111111`.
- **Section backgrounds**: White (`#ffffff`) for hero sections; `#f3f3f3` (`surface-container-low`) for alternating content sections.
- **Hero style (section pages)**: White background with a 3px primary red bottom border (`border-b-[3px] border-primary`). Not dark. See technical.html for the exact implementation.
- **Icons**: Material Symbols Outlined icon font via Google Fonts.

---

## BRANDING TOKENS

| Token | Value | Tailwind key |
|---|---|---|
| Headline font | Plus Jakarta Sans 700/800 via Google Fonts | `font-headline` (defined in Tailwind config) |
| Body font | Inter 400/500/600 via Google Fonts | default |
| Primary | #b8001c | `primary-container` |
| Primary dark | #8c0012 | `primary` |
| Tertiary | #364457 | `tertiary` |
| On-surface (dark text) | #1a1c1c | `on-surface` |
| Surface canvas | #f3f3f3 | `surface-container-low` |
| Surface card | #ffffff | `surface-container-lowest` |
| Surface recessed | #e2e2e2 | `surface-container-highest` |
| HIGH badge | #e03131 | — |
| MEDIUM badge | #f08c00 | — |
| LOW badge | #2f9e44 | — |
| MONITOR badge | #868e96 | — |
| Manual Verification badge | #1971c2 | — |
| Score ring — red (0–49) | #e03131 | — |
| Score ring — amber (50–74) | #f08c00 | — |
| Score ring — green (75–100) | #2f9e44 | — |
| Ring track | #e2e2e2 | `surface-container-highest` |
| Logo URL | Confirm with user before generating | — |

The full Tailwind config block (including all MD3 surface tokens) is defined in technical.html — copy it verbatim into every generated page's `<head>` before the page-specific styles.

---

## FILE OUTPUT STRUCTURE

Generate 9 separate .html files in a single `HTML/` folder inside the audit root directory. Confirm folder name with user before creating.

| File | Page |
|---|---|
| index.html | Overview — executive summary, overall score ring, section bar charts, data sources carousel |
| technical.html | Technical |
| ux.html | User Experience |
| tools.html | Tools & Configuration |
| on-site.html | On-Site SEO |
| off-site.html | Off-Site |
| geo.html | GEO / AI Visibility |
| schema.html | Schema |
| methodology.html | Methodology |

All internal links between pages use relative paths (e.g. `href="technical.html"`). All external links open in a new tab with `rel="noopener noreferrer"`.

---

## SCORE CALCULATION

Calculate section scores from workbook_data.json before generating any page.

**Element score (0–100):**
Normalize the Rating Value (1=Not Present, 2=Weak, 3=Medium, 4=High, 5=Excellent) to a 0–100 scale:
`Element Score = (Rating Value − 1) / 4 × 100`
Not Applicable and Data Missing rows are excluded from calculations.

**Section score (0–100):**
`Section Score = sum(Element Score × Weight) / sum(Weight × 100) × 100`
where Weight is the numeric weight from the Weight/Importance (Numeric) column.
Round to nearest whole number.

**Overall score (0–100):**
Weighted average of all 114 scoreable elements using the same formula above. Exclude Data Missing and Not Applicable rows.

**Ring colour by score range:**
- 0–49: #b8001c (red)
- 50–74: #f0a500 (amber)
- 75–100: #2e7d32 (green)

---

## SHARED COMPONENTS

### Sticky header (all pages)

The header has three zones: left (dual logo), centre (nav), right (audit meta). The active nav link for the current page uses the tonal chip style — see technical.html for the exact class pattern.

```html
<!-- Left: Digitad wordmark + divider + client monogram badge + client name -->
<!-- Centre: nav links to all 9 pages -->
<!-- Right: "[Client] · [Month Year]" in small grey text -->
```

See technical.html for the full implementation. Copy the header block verbatim and update:
- The active nav link class for the current page (`active` class or equivalent tonal chip)
- The client name and date in the right meta span

### Breadcrumbs (section and methodology pages only — not on index)

```html
<nav class="breadcrumbs" aria-label="Breadcrumb">
  <a href="index.html">Overview</a>
  <span class="crumb-sep">›</span>
  <span class="crumb-current">[Page Title]</span>
</nav>
```

### Domain expiry banner (index page only — render only if domain expires within 90 days)

Calculate days between audit date and domain expiry date from workbook data. If ≤ 90 days, render:
```html
<div class="expiry-banner">
  Domain expires [DATE] — immediate renewal required
</div>
```
If > 90 days or date unknown, omit the banner entirely.

---

## SCORE RING COMPONENT

Used on index.html (large, overall score) and on each section page (medium, section score).

**Implementation:** SVG donut ring with CSS transition on hover and JavaScript tooltip.

Ring specifications:
- Large (index): 200px diameter, 16px stroke width
- Medium (section pages): 120px diameter, 10px stroke width
- Track (background circle): #e0e0e0
- Fill circle: colour based on score range
- Centre text: score number in Plus Jakarta Sans Bold, % sign smaller beside it
- Hover: CSS `transform: scale(1.08)` with `transition: transform 0.25s ease` on the SVG element
- Hover tooltip: positioned below the ring, shows:
  - Full score: [N]/100
  - Elements analysed: [N] elements
  - Priority breakdown: [N] HIGH · [N] MEDIUM · [N] LOW · [N] MONITOR · [N] Manual Verification Required
  - Weighted contribution (section rings only): Weight [X]% · Contribution [Y] pts

```html
<div class="ring-wrapper" data-score="[SCORE]">
  <svg class="score-ring" viewBox="0 0 [SIZE] [SIZE]" aria-label="Score: [SCORE]/100">
    <circle class="ring-track" cx="[CX]" cy="[CY]" r="[R]"
            fill="none" stroke="#e0e0e0" stroke-width="[SW]"/>
    <circle class="ring-fill" cx="[CX]" cy="[CY]" r="[R]"
            fill="none" stroke="[COLOUR]" stroke-width="[SW]"
            stroke-dasharray="[CIRCUMFERENCE]"
            stroke-dashoffset="[OFFSET]"
            stroke-linecap="round"
            transform="rotate(-90 [CX] [CY])"/>
    <text class="ring-label" x="[CX]" y="[CY]" text-anchor="middle" dominant-baseline="central">
      [SCORE]
    </text>
  </svg>
  <div class="ring-tooltip" role="tooltip">
    <strong>[SCORE]/100</strong>
    <span>[N] elements analysed</span>
    <span class="tp-high">[N] HIGH</span>
    <span class="tp-medium">[N] MEDIUM</span>
    <span class="tp-low">[N] LOW</span>
    <span class="tp-monitor">[N] MONITOR</span>
    <span class="tp-verify">[N] Manual Verification Required</span>
  </div>
</div>
```

Calculate `stroke-dashoffset`:
- `circumference = 2 × π × r`
- `offset = circumference × (1 − score / 100)`

---

## INDEX PAGE — LAYOUT SPEC (index.html)

Page title: `[CLIENT NAME] — SEO & GEO Audit — [Month Year]`

Layout order (top to bottom):
1. Sticky header
2. Domain expiry banner (conditional)
3. Executive summary section
4. Overall score ring + priority summary bar
5. Priority matrix — scatter plot
6. Section score bar charts
7. Data sources carousel

### 1. Executive summary section

Pull content from the Executive Summary .md file generated during the audit. Render as flowing paragraphs — no tables, no numbers, no element codes, no priority counts. Written for brand teams, not SEO specialists. Plain and professional tone.

```html
<section class="exec-summary">
  <div class="section-inner">
    <h1>SEO & GEO Audit — [CLIENT NAME]</h1>
    <p class="audit-date">[Month Year]</p>
    [EXECUTIVE SUMMARY PARAGRAPHS]
  </div>
</section>
```

### 2. Overall score ring + priority summary bar

```html
<section class="overview-score">
  <div class="section-inner">
    <h2>Overall Health Score</h2>
    [RING COMPONENT — large, 200px]
    <div class="priority-bar">
      <span class="badge high">[N] HIGH</span>
      <span class="badge medium">[N] MEDIUM</span>
      <span class="badge low">[N] LOW</span>
      <span class="badge monitor">[N] MONITOR</span>
    </div>
  </div>
</section>
```

### 5. Priority matrix — scatter plot

**Reference:** `examples/html-preview/index.html` — copy the full Priority Matrix `<section>` block verbatim, then substitute client-specific dot content.

The matrix is a CSS scatter plot — individual dots positioned absolutely on a coordinate plane. It is NOT a 2×2 chip grid. Each dot represents one distinct finding from the audit, positioned by its estimated impact (Y-axis) and ease of implementation (X-axis).

**Dot selection — 5 to 7 findings maximum.** Select from HIGH-priority items in `workbook_data.json`. Use this criteria to narrow the list:
- Prioritise findings with the highest Priority Score (lowest numeric value — closest to 10)
- Spread across at least 3 different phases to show breadth
- Include at least one Quick Wins quadrant item (high impact + easy to implement)
- Include at least one Major Projects item (high impact + hard — shows strategic depth)
- Avoid findings that are DATA MISSING or Manual Verification Required

**Dot positioning — use `left` and `top` as percentage values** within the 480px scatter plot container. Dots are centered using `transform: translate(-50%, -50%)`. Coordinate reference:
- X-axis: `left: 5%` = very hard, `left: 95%` = very easy. Midpoint (`left: 50%`) is the quadrant boundary.
- Y-axis: `top: 5%` = very high impact, `top: 95%` = very low impact. Midpoint (`top: 50%`) is the quadrant boundary.
- Keep dots at least 10 percentage points apart on both axes to avoid visual overlap.
- Keep dots at least 5% away from the container edges.

**Dot color — by phase:**

| Phase | Color | RGB value |
|---|---|---|
| Technical | Slate `#364457` | `rgba(54,68,87,0.88)` |
| User Experience | Slate `#364457` | `rgba(54,68,87,0.88)` |
| Tools & Configuration | Slate `#364457` | `rgba(54,68,87,0.88)` |
| On-Site SEO | Red `#b8001c` | `rgba(184,0,28,0.88)` |
| Off-Site | Red `#b8001c` | `rgba(184,0,28,0.88)` |
| GEO / AI Visibility | Blue `#1971c2` | `rgba(25,113,194,0.88)` |
| Schema | Dark red `#8c0012` | `rgba(140,0,18,0.88)` |

Use matching `box-shadow` color at 0.32 opacity for each dot.

**Dot tooltip — one sentence per dot.** Write a single plain-language sentence (max 160 characters) that explains why this finding matters. Do not repeat the dot label. Use the Score Explanation field from `workbook_data.json` as the source — condense to one sentence, remove any technical jargon, remove element codes. Never use "the user confirmed" or similar language.

**Quadrant hover labels — hidden by default, shown on hover.** The four labels are fixed and do not change per client:
- Top-left: **Major Projects** (amber `#f08c00`)
- Top-right: **Quick Wins** (green `#2f9e44`)
- Bottom-left: **Reconsider** (zinc `#868e96`)
- Bottom-right: **Easy Fixes** (blue `#1971c2`)

When a dot is hovered, the quadrant label is suppressed — the dot tooltip takes precedence. This is handled by `.scatter-plot:has(.scatter-dot:hover) .quadrant-hover-label { opacity: 0 !important; }`.

**Legend** — show only the phases that are actually represented by dots in this client's matrix (do not show all 7 phases if only 3 are used).

**Required CSS** — add to the page `<style>` block (copy from the example file or from the Dannon index.html):
```css
.quadrant-hover-label { position:absolute; top:50%; left:50%; transform:translate(-50%,calc(-50% + 4px)); opacity:0; transition:opacity 0.18s ease,transform 0.18s ease; pointer-events:none; z-index:40; white-space:nowrap; }
.quadrant-zone:hover .quadrant-hover-label { opacity:1; transform:translate(-50%,-50%); }
.scatter-plot:has(.scatter-dot:hover) .quadrant-hover-label { opacity:0 !important; }
.scatter-dot > div { transition:transform 0.15s ease; }
.scatter-dot:hover > div { transform:scale(1.12); }
.dot-tooltip { position:absolute; top:calc(100% + 10px); left:50%; transform:translateX(-50%) translateY(-4px); opacity:0; transition:opacity 0.18s ease,transform 0.18s ease; pointer-events:none; z-index:50; background:#1a1c1c; color:#fff; font-family:Inter,sans-serif; font-size:11px; line-height:1.5; padding:8px 12px; border-radius:6px; box-shadow:0 4px 16px rgba(0,0,0,0.18); width:210px; text-align:center; }
.scatter-dot:hover .dot-tooltip { opacity:1; transform:translateX(-50%) translateY(0); }
```

**:has() browser support** — `:has()` is supported in Chrome 105+, Safari 15.4+, Firefox 121+. No fallback is required for client reports.

---

### 6. Section score bar charts

One horizontal bar per section (8 sections, excluding Methodology). Bars ordered by section sequence (Technical → Schema). Each bar shows the section name, score out of 100, and a filled progress bar coloured by score range.

```html
<section class="section-scores">
  <div class="section-inner">
    <h2>Scores by Area</h2>
    <div class="score-bars">
      <!-- Repeat for each section -->
      <div class="score-bar-row">
        <a href="technical.html" class="bar-label">Technical</a>
        <div class="bar-track">
          <div class="bar-fill" style="width: [SCORE]%; background: [COLOUR];"
               aria-label="Technical: [SCORE]/100"></div>
        </div>
        <span class="bar-score">[SCORE]/100</span>
      </div>
    </div>
  </div>
</section>
```

### 7. Data sources carousel

Auto-scrolling horizontal strip of logos for all data sources used in this audit. Populate dynamically from the data sources confirmed at Phase 0 (workbook_data.json Phase 0 intake notes, or the session log). Always include the Digitad logo first.

Logo sources — use these CDN URLs:

| Source | Logo URL |
|---|---|
| Digitad | [LOGO_URL confirmed by user] |
| Google Search Console | https://logo.clearbit.com/search.google.com |
| Google Analytics | https://logo.clearbit.com/analytics.google.com |
| PageSpeed Insights | https://logo.clearbit.com/pagespeed.web.dev |
| Screaming Frog | https://logo.clearbit.com/screamingfrog.co.uk |
| Ahrefs | https://logo.clearbit.com/ahrefs.com |
| Semrush | https://logo.clearbit.com/semrush.com |
| Moz | https://logo.clearbit.com/moz.com |
| GTmetrix | https://logo.clearbit.com/gtmetrix.com |
| SE Ranking | https://logo.clearbit.com/seranking.com |
| Majestic | https://logo.clearbit.com/majestic.com |
| Lumen Database | https://logo.clearbit.com/lumendatabase.org |

Only include logos for sources that were actually used in this audit. If a Clearbit logo fails to load, fall back to the domain's favicon: `https://www.google.com/s2/favicons?domain=[domain]&sz=64`.

```html
<section class="data-sources">
  <div class="section-inner">
    <h2>Data Sources</h2>
    <div class="carousel-track-wrapper">
      <div class="carousel-track">
        <!-- Repeat for each source — duplicate set for seamless loop -->
        <div class="carousel-item">
          <img src="[LOGO_URL]" alt="[Source Name]"
               onerror="this.src='https://www.google.com/s2/favicons?domain=[domain]&sz=64'">
          <span>[Source Name]</span>
        </div>
      </div>
    </div>
  </div>
</section>
```

Carousel CSS animation — seamless loop using keyframe translation:
```css
.carousel-track {
  display: flex;
  gap: 40px;
  animation: scroll-logos 30s linear infinite;
  width: max-content;
}
.carousel-track-wrapper {
  overflow: hidden;
  mask-image: linear-gradient(to right, transparent, black 10%, black 90%, transparent);
  -webkit-mask-image: linear-gradient(to right, transparent, black 10%, black 90%, transparent);
}
@keyframes scroll-logos {
  0% { transform: translateX(0); }
  100% { transform: translateX(-50%); }
}
```
Duplicate the logo list inside `.carousel-track` (render the list twice back-to-back) so the animation loops seamlessly.

---

## SECTION PAGE — LAYOUT SPEC

Applies to: technical.html, ux.html, tools.html, on-site.html, off-site.html, geo.html, schema.html

Page title: `[PAGE TITLE] — [CLIENT NAME] — SEO & GEO Audit — [Month Year]`

Layout order (top to bottom):
1. Sticky header
2. Breadcrumbs
3. Page title + section score ring (medium, 120px) + horizontal progress bar
4. Per-element score bar chart
5. Issue dropdowns — sorted by priority: HIGH → MEDIUM → LOW → MONITOR → Manual Verification Required → Passing
6. Passing items group (grey, collapsed by default)

### 3. Section hero block

The hero is white (`bg-white`) with a 3px primary red bottom border. It is NOT a dark background. See technical.html for the full implementation. Key content elements:

- **Eyebrow**: Small coloured bar + uppercase section name label
- **h1**: Section title (large, Tailwind `text-5xl md:text-7xl font-headline`)
- **Summary**: Two paragraphs — first paragraph explains what this section covers in plain language; second paragraph calls out the two or three most critical findings specific to this client
- **Priority badge pills**: Four pill badges (HIGH [N], MEDIUM [N], LOW [N], MONITOR [N]) rendered as `<a>` anchor links pointing to their respective priority group sections on the page (e.g. `href="#high-issues"`). This lets the reader jump directly from the hero to the relevant priority group.
- **Score ring**: SVG donut ring (right column, medium size) showing the section score, coloured by score range

Priority group sections on the page must have matching `id` attributes AND `scroll-mt-20` (Tailwind) to offset the sticky header on scroll:
```html
<div id="high-issues" class="space-y-6 scroll-mt-20">
<div id="medium-issues" class="space-y-6 scroll-mt-20">
<div id="low-issues" class="space-y-6 scroll-mt-20">
<div id="monitor-issues" class="space-y-6 scroll-mt-20">
```

### 4. Per-element bar chart

One horizontal bar per element in this section, ordered by element sequence (as in workbook_data.json). Each bar shows the element name, its normalized score (0–100), and is coloured by the element's Priority level. Skip Data Missing and Not Applicable rows in this chart.

```html
<section class="element-chart">
  <div class="section-inner">
    <h2>Element Breakdown</h2>
    <div class="element-bars">
      <!-- One row per element -->
      <div class="element-bar-row">
        <span class="element-name">[Analyzed Element value]</span>
        <div class="bar-track">
          <div class="bar-fill [priority-class]"
               style="width: [ELEMENT_SCORE]%;"
               title="[Analyzed Element]: [SCORE]/100 — [Priority]"></div>
        </div>
        <span class="priority-badge [priority-class]">[Priority]</span>
      </div>
    </div>
  </div>
</section>
```

Priority CSS classes for bar colours: `priority-high` (#b8001c) · `priority-medium` (#f0a500) · `priority-low` (#2e7d32) · `priority-monitor` (#757575) · `priority-verify` (#1a6ab1) · `priority-passing` (#9e9e9e)

### 5. Issue dropdowns

Render one accordion card per element, sorted strictly by priority:
1. HIGH
2. MEDIUM
3. Opportunity
4. LOW
5. MONITOR
6. Manual Verification Required
7. Passing (collapsed group — see section 6)

Do not include Data Missing or Not Applicable rows.

**Accordion implementation**: Use JS-toggled div cards, NOT `<details>/<summary>`. See technical.html for the full implementation. Key structural rules:

- The **outer card** carries a full-height left border in the priority colour (e.g. `border-l-[6px] border-[#e03131]` for HIGH). This border runs the full height of the card — closed and open.
- The **trigger div** (header row with icon, title, chevron) has NO border of its own — the border is on the outer card only.
- The **content div** (grey box, `bg-surface-container-low`) has NO border. It uses `mx-6 rounded-lg` (or `mx-4` for LOW/MONITOR) with no `mb-` margin — bottom spacing comes from `pb-6` toggled on the outer card by JS when open.
- The JS toggle adds `pb-6` to the outer card when opening and removes it when closing, creating white space below the grey box without margin-collapse issues.
- All accordions start **closed** (content div has `hidden` class by default). Chevron rotates 180° on open.

Priority colours for left borders and icon backgrounds:
- HIGH: `#e03131`
- MEDIUM: `#f08c00`
- LOW: `#2f9e44`
- MONITOR: `#868e96`
- Manual Verification Required: `#1971c2`

The accordion JS (copy from technical.html):
```js
document.querySelectorAll('.accordion-card').forEach(card => {
  const trigger = card.querySelector('.accordion-trigger');
  const content = card.querySelector('.accordion-content');
  const icon = card.querySelector('.accordion-icon');
  if (!trigger || !content) return;
  trigger.addEventListener('click', () => {
    const isOpen = !content.classList.contains('hidden');
    content.classList.toggle('hidden', isOpen);
    card.classList.toggle('pb-6', !isOpen);
    if (icon) icon.classList.toggle('rotate-180', !isOpen);
  });
});
```

Content inside each open accordion (three columns on desktop, single column on mobile):

```html
<!-- Priority group heading — render only if group has items -->
<h2>[Group label]</h2>

<div class="accordion-card border-l-[6px] border-[PRIORITY_COLOUR] bg-white editorial-shadow">
  <div class="accordion-trigger flex items-center p-6 cursor-pointer">
    <div class="icon-circle [priority-tint]"><!-- Material Symbol icon --></div>
    <div class="flex-1"><h3>[Analyzed Element value]</h3></div>
    <span class="accordion-icon transition-transform"><!-- expand_more icon --></span>
  </div>
  <div class="accordion-content hidden p-8 bg-surface-container-low mx-6 rounded-lg
              grid grid-cols-1 md:grid-cols-3 gap-8">

    <div>
      <h4>What it is</h4>
      <p>[Description field — plain language explanation of what this element is]</p>
    </div>

    <div>
      <h4>Why it is a problem</h4>
      <p>[Score Explanation field — specific finding and impact. Full sentence. No element codes.]</p>
    </div>

    <div>
      <h4>How to fix it</h4>
      <p>[How to correct? field — each bullet as a separate sentence or rendered as a list.]</p>
    </div>

  </div><!-- end accordion-content -->
</div><!-- end accordion-card -->

<!-- Repeat for each element in priority order -->
```

Comments and Sources fields: omit entirely if empty. If present, render as a small supplementary row beneath the three-column grid inside the content div.

Group heading labels:
- HIGH → "High Priority"
- MEDIUM → "Medium Priority"
- Opportunity → "Opportunities"
- LOW → "Lower Priority"
- MONITOR → "Monitor"
- Manual Verification Required → "Requires Verification"

Omit a group heading entirely if that group has zero items.

### 6. Passing items group (collapsed by default)

```html
<details class="passing-group">
  <summary class="passing-summary">
    <span class="passing-icon">✓</span>
    No issues found ([N] elements passing)
  </summary>
  <div class="passing-list">
    <!-- One row per passing element -->
    <div class="passing-row">
      <span class="passing-check">✓</span>
      <span class="passing-name">[Analyzed Element]</span>
      <span class="passing-note">[Score Explanation — one sentence]</span>
    </div>
  </div>
</details>
```

---

## METHODOLOGY PAGE — LAYOUT SPEC (methodology.html)

Page title: `Methodology — [CLIENT NAME] — SEO & GEO Audit — [Month Year]`

Layout order:
1. Sticky header
2. Breadcrumbs
3. Page title
4. Executive summary (number-free) — same text as index.html executive summary section
5. What We Checked — section-by-section plain language description with element count
6. How We Score — scoring methodology in plain text with the rating scale table

### What We Checked

One block per section. Do not use the word "phase" anywhere.

```html
<section class="methodology-section">
  <div class="section-inner">
    <h2>What We Checked</h2>
    <div class="method-grid">

      <div class="method-card">
        <h3>Technical</h3>
        <p>26 elements — crawlability, indexation, site speed, security, structured URLs, mobile configuration, and server-level signals that affect how search engines access and interpret the site.</p>
        <a href="technical.html" class="method-link">View Technical results ›</a>
      </div>

      <div class="method-card">
        <h3>User Experience</h3>
        <p>14 elements — Core Web Vitals, mobile usability, navigation, accessibility, and on-page interaction signals that affect both users and search rankings.</p>
        <a href="ux.html" class="method-link">View User Experience results ›</a>
      </div>

      <div class="method-card">
        <h3>Tools & Configuration</h3>
        <p>11 elements — Analytics setup, tracking accuracy, Search Console configuration, and the measurement infrastructure needed to act on performance data.</p>
        <a href="tools.html" class="method-link">View Tools & Configuration results ›</a>
      </div>

      <div class="method-card">
        <h3>On-Site SEO</h3>
        <p>26 elements — Title tags, meta descriptions, heading structure, content quality, internal linking, image optimisation, and on-page signals that determine how individual pages rank.</p>
        <a href="on-site.html" class="method-link">View On-Site SEO results ›</a>
      </div>

      <div class="method-card">
        <h3>Off-Site</h3>
        <p>11 elements — Backlink profile, domain authority, referring domains, link quality, and external signals that establish the site's credibility with search engines.</p>
        <a href="off-site.html" class="method-link">View Off-Site results ›</a>
      </div>

      <div class="method-card">
        <h3>GEO / AI Visibility</h3>
        <p>26 elements — How the site appears in AI-generated responses, large language model citations, AI Overviews, and generative search experiences across major platforms.</p>
        <a href="geo.html" class="method-link">View GEO / AI Visibility results ›</a>
      </div>

      <div class="method-card">
        <h3>Schema</h3>
        <p>Schema markup implementation across all key page types — structured data that enables rich results, knowledge panel features, and machine-readable content signals.</p>
        <a href="schema.html" class="method-link">View Schema results ›</a>
      </div>

    </div>
  </div>
</section>
```

### How We Score

```html
<section class="scoring-method">
  <div class="section-inner">
    <h2>How We Score</h2>

    <p>Each element is rated on a five-point scale from Not Present to Excellent, then multiplied by a weight that reflects its real-world impact on search and AI visibility. The resulting Priority Score determines where action is most urgent.</p>

    <h3>Rating Scale</h3>
    <table class="method-table">
      <thead><tr><th>Rating</th><th>Meaning</th></tr></thead>
      <tbody>
        <tr><td>Not Present (1)</td><td>The element does not exist on the site.</td></tr>
        <tr><td>Weak (2)</td><td>Exists but implemented very poorly.</td></tr>
        <tr><td>Medium (3)</td><td>Functional but with significant room to improve.</td></tr>
        <tr><td>High (4)</td><td>Mostly good, with minor improvements possible.</td></tr>
        <tr><td>Excellent (5)</td><td>Best practice met — virtually no issues.</td></tr>
      </tbody>
    </table>

    <h3>Importance Weights</h3>
    <table class="method-table">
      <thead><tr><th>Weight</th><th>Tier</th><th>Meaning</th></tr></thead>
      <tbody>
        <tr><td>10</td><td>Critical</td><td>Core ranking or visibility factor — high urgency.</td></tr>
        <tr><td>7.5</td><td>High</td><td>Strong impact on search performance.</td></tr>
        <tr><td>5</td><td>Medium</td><td>Moderate impact — worth addressing.</td></tr>
        <tr><td>2.5</td><td>Low</td><td>Minor or indirect signal.</td></tr>
      </tbody>
    </table>

    <h3>Priority Levels</h3>
    <table class="method-table">
      <thead><tr><th>Priority Score</th><th>Priority</th><th>What it means</th></tr></thead>
      <tbody>
        <tr><td>10 or under</td><td><span class="badge high">HIGH</span></td><td>Act immediately — significant impact on visibility.</td></tr>
        <tr><td>11–20</td><td><span class="badge medium">MEDIUM</span></td><td>Address this quarter — meaningful improvement available.</td></tr>
        <tr><td>21–35</td><td><span class="badge low">LOW</span></td><td>Monitor and improve — lower urgency.</td></tr>
        <tr><td>36–50</td><td><span class="badge monitor">MONITOR</span></td><td>No action needed — performing well.</td></tr>
      </tbody>
    </table>

  </div>
</section>
```

---

## GENERATION WORKFLOW

HTML files are generated by running `scripts/generate_html.py` from the skill scripts directory. Do not generate HTML files individually or manually — Rule S8 in CLAUDE.md applies.

### Step 1 — Confirm prerequisites (L3 gate must have passed)

Before running the script, confirm all five items from the PRE-GENERATION CHECKLIST above are complete.

### Step 2 — Configure the script

Set the CONFIGURATION block at the top of `scripts/generate_html.py`:

```python
AUDIT_DIR               = ""     # Absolute path to audit root, e.g. "/Users/you/client_audit"
CLIENT_NAME             = ""     # Display name, e.g. "Danimals"
AUDIT_DATE              = ""     # e.g. "March 2026"
CLIENT_SLUG             = ""     # URL-safe slug, e.g. "danimals"
DIGITAD_LOGO_PATH       = ""     # Absolute path to Digitad logo file
CLIENT_LOGO_PATH        = ""     # Absolute path to client logo file
OVERALL_SCORE_OVERRIDE  = None   # Set to int to override computed score (e.g. 40)
EXEC_SUMMARY_PARAS      = [      # Pull from Executive Summary .md — plain text, no element codes
    "First paragraph...",
    "Second paragraph...",
]
PRIORITY_MATRIX_DOTS    = [      # 5–7 items. Keys: label, href, x (0–100), y (0–100), color, shadow, tooltip
    # {"label": "Social Meta Tags", "href": "on-site.html", "x": 60, "y": 20,
    #  "color": "rgba(184,0,28,0.88)", "shadow": "rgba(184,0,28,0.32)",
    #  "tooltip": "One sentence explaining why this finding matters."},
]
DATA_SOURCES            = [      # Confirmed sources from Phase 0 session log
    # {"name": "Screaming Frog", "icon": "bug_report"},
    # {"name": "PageSpeed",      "icon": "monitoring"},
]
```

Log the configuration values in the Session Log under the HTML Report Configuration section (see FORMS-INTERNAL.md).

### Step 3 — Run the script

```bash
python3 /absolute/path/to/seo-geo-technical-audit/scripts/generate_html.py
```

The script writes all 9 .html files to `{AUDIT_DIR}/HTML/`. Confirm the file list output printed by the script.

### Step 4 — Run L4 validation gate

Load CHECKS.md and run all L4 checks after the script completes. After all 9 files pass L4: confirm the full file list with the user.

---

## CSS DESIGN SYSTEM

The CSS design system is implemented directly inside `scripts/generate_html.py` as part of the Tailwind config block. Do not add a separate CSS block to HTML files — the script handles all styling. For design system reference (colour tokens, typography, components), read DESIGN.md and the example files in `examples/html-preview/`.

---

## CONTENT RULES — APPLY TO EVERY HTML PAGE

- No element codes (T01, G12, etc.) anywhere — not in headings, not in text, not in comments
- No section names used as internal references ("as noted in the Technical section..." is banned; describe the finding directly)
- No cross-references between pages or elements ("see also...", "addressed elsewhere")
- No specific product, plugin, or service names in any recommendation — describe what to implement, not which product to use
- No generic tool URLs — the Sources field may contain specific report filenames only (e.g. "Title Tag Issues report")
- No raw markdown, no code blocks, no terminal-style formatting visible to the reader
- No automated-audit language — "user confirmed," "user-provided," "user said" must not appear on any page
- "Phase 1," "Phase 2," etc. must not appear anywhere in the HTML output
- Write in full sentences for all descriptive fields — fragments are not acceptable in client-facing documents
- The executive summary (index.html and methodology.html) must be entirely number-free — no scores, counts, or percentages

---


*OUTPUTS-HTML.md | seo-geo-technical-audit | Version 11 | March 2026*
