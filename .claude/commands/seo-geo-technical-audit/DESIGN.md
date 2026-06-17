{\rtf1\ansi\ansicpg1252\cocoartf2822
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\fs24 \cf0 # Design System Strategy: The Executive Lens\
\
## 1. Overview & Creative North Star\
**Creative North Star: "The Precision Curator"**\
\
The objective of this design system is to transform dense SEO and GEO audit data into an authoritative, executive-friendly narrative. Most SaaS dashboards fail by cluttering the interface with "container-itis"\'97boxes within boxes separated by harsh lines.\
\
"The Precision Curator" breaks the template look by utilizing **Editorial Asymmetry** and **Tonal Depth**. We treat the dashboard not as a software interface, but as a premium digital report. By leveraging high-contrast typography and expansive whitespace, we guide the eye toward "Insight" rather than just "Data." We favor breathing room over density, and tonal shifts over structural borders.\
\
---\
\
## 2. Color & Surface Philosophy\
This system is built on a sophisticated interplay between the authoritative Digitad Red and a tiered grayscale palette that mimics physical layers of fine paper and frosted glass.\
\
### Color Palette Reference\
- **Primary High-Impact:** `primary` (#8c0012) and `primary_container` (#b8001c). These are reserved for critical "Action" or "Success/Alert" states.\
- **The Foundation:** `background` (#f9f9f9) and `surface` (#f9f9f9).\
- **Surface Hierarchy (The Stacking Rule):**\
- `surface_container_lowest` (#ffffff): Use for the main content cards or active data modules.\
- `surface_container_low` (#f3f3f3): Use for the primary canvas background.\
- `surface_container_highest` (#e2e2e2): Use for recessed areas like search bars or inactive navigation states.\
\
### Core Visual Rules\
* **The "No-Line" Rule:** 1px solid borders are strictly prohibited for sectioning. Boundaries must be defined solely through background color shifts. For example, a white card (`surface_container_lowest`) sits on a light grey canvas (`surface_container_low`).\
* **The "Glass & Gradient" Rule:** To provide "soul" to the data, use a subtle linear gradient on primary elements (e.g., `primary` to `primary_container`). For floating modals or navigation overlays, apply a `backdrop-blur` of 12px with a semi-transparent `surface` color to achieve a "frosted glass" effect.\
* **Signature Textures:** Large data visualizations should use the `tertiary` (#364457) and `primary` scales to provide a professional, executive-level color contrast that avoids the "rainbow" look of amateur dashboards.\
\
---\
\
## 3. Typography\
We use a high-contrast scale to create an editorial feel. The pairing of **Plus Jakarta Sans** and **Inter** creates a balance between modern geometry and functional legibility.\
\
* **Display & Headlines (Plus Jakarta Sans):** Used for high-level metrics and section titles.\
- *Intent:* High tracking and bold weights convey authority.\
- *Usage:* `display-lg` for primary SEO scores; `headline-sm` for audit categories.\
* **Body & Labels (Inter):** Used for data points, issue lists, and descriptions.\
- *Intent:* Maximum readability.\
- *Usage:* `body-md` for issue descriptions; `label-sm` (all caps, increased letter-spacing) for meta-information like "Status" or "Date."\
\
---\
\
## 4. Elevation & Depth\
Depth in this system is achieved through **Tonal Layering** rather than traditional structural lines.\
\
* **The Layering Principle:** Treat the UI as a series of stacked sheets.\
- Layer 0: `surface_container_low` (The Desk)\
- Layer 1: `surface_container_lowest` (The Paper/Card)\
- Layer 2: Ambient Shadow (The Lift)\
* **Ambient Shadows:** When an element must float (e.g., a dropdown or a "Critical Issue" alert), use a shadow with a 20px\'9640px blur and only 4% opacity using a tint of the `on_surface` color. It should feel like a soft glow, not a dark drop shadow.\
* **The "Ghost Border" Fallback:** For accessibility in input fields, use the `outline_variant` token at 15% opacity. It should be barely perceptible, serving as a suggestion of a boundary rather than a hard wall.\
\
---\
\
## 5. Components\
\
### Buttons\
* **Primary:** A subtle gradient from `primary` to `primary_container`. Border radius `lg` (0.5rem). Use `title-sm` for button text.\
* **Secondary:** Ghost style. No background, no border. Use `on_surface_variant` for text, shifting to `primary` on hover.\
* **Tertiary:** `surface_container_highest` background with `on_surface` text for low-priority actions.\
\
### Cards & Data Modules\
* **Style:** No borders. Background: `surface_container_lowest`.\
* **Spacing:** Minimum padding of `spacing-6` (2rem) to allow data to breathe.\
* **Data Viz:** Audit rings should use a thick stroke (8px+) with rounded caps. The "Empty" track should be `surface_container_highest`.\
\
### Structured Issue Lists\
* **The "No-Divider" Rule:** Forbid the use of horizontal lines between list items. Instead, use a vertical spacing of `spacing-4` and a subtle `surface_container_low` background on hover to isolate the row.\
* **Hierarchy:** Use `title-md` for the issue title and `body-sm` with `on_surface_variant` for the technical description.\
\
### Input Fields\
* **Style:** Minimalist. `surface_container_highest` background, no border, 0.5rem radius.\
* **Focus State:** A 2px "Ghost Border" using the `primary` color at 30% opacity.\
\
---\
\
## 6. Do\'92s and Don\'92ts\
\
### Do:\
- **Use "Aggressive" Whitespace:** If you think there is enough space, add 20% more. This is an executive tool; space equals clarity.\
- **Asymmetric Layouts:** Place a large metric (`display-lg`) on the left and a small, structured list on the right to create visual interest.\
- **Tonal Transitions:** Use background shifts to define "Active" states in navigation rather than underlines or boxes.\
\
### Don\'92t:\
- **Avoid 100% Black:** Use `on_surface` (#1a1c1c) for text to maintain a premium, softer contrast.\
- **No Heavy Borders:** Never use a 1px border to separate the sidebar from the main content; use a background shift from `surface` to `surface_container_low`.\
- **No Crowding:** Do not let two cards touch. Use the `spacing-4` or `spacing-6` scale to ensure a "gutter" of the background color is always visible.}