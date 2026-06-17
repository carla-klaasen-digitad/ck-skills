#!/usr/bin/env python3
"""
generate_html.py — SEO & GEO Audit HTML Report Generator
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Version 1.1 — Tailwind design system (matches yocrunch reference output)

DESIGN SYSTEM: Tailwind CDN + Material Symbols Outlined + Plus Jakarta Sans + Inter
Do NOT use CSS variables or Gilroy — those are not used in production HTML output.
The correct system is confirmed by reading yocrunch_technical_audit/HTML/ reference files.

HOW TO USE FOR A NEW AUDIT
---------------------------
1. Set the CONFIGURATION block below — AUDIT_DIR, CLIENT_NAME, AUDIT_DATE, CLIENT_SLUG,
   DIGITAD_LOGO_PATH, CLIENT_LOGO_PATH.
2. Set OVERALL_SCORE_OVERRIDE if the exec summary states a specific score.
3. Populate EXEC_SUMMARY_PARAS from the Executive Summary .md (plain text, no element codes).
4. Populate PRIORITY_MATRIX_DOTS (5–7 items from HIGH-priority findings).
5. Populate DATA_SOURCES (confirmed tools from the Phase 0 session log).
6. Run: python3 scripts/generate_html.py

INPUT:
  {AUDIT_DIR}/Workbook/workbook_data.json
  DIGITAD_LOGO_PATH (set in config)
  CLIENT_LOGO_PATH (set in config)
  {AUDIT_DIR}/Outputs/CSV/*Schema Markup Corrections*.csv
  {AUDIT_DIR}/Outputs/*Executive Summary*.md

OUTPUT: 9 HTML files in {AUDIT_DIR}/HTML/
  index.html, technical.html, ux.html, tools.html, on-site.html,
  off-site.html, geo.html, schema.html, methodology.html

LOCATION: all_skills/seo-geo-technical-audit-v11/scripts/generate_html.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import json
import math
import os
import csv
import re
import glob
import shutil
from pathlib import Path

# ============================================================
# CONFIGURATION — set per audit before running
# ============================================================
AUDIT_DIR   = ""     # e.g. "/Users/you/claude_code/client_technical_audit"
CLIENT_NAME = ""     # e.g. "Danimals"
AUDIT_DATE  = ""     # e.g. "March 2026"
AUDIT_URL   = ""     # e.g. "https://danimals.com/"
CLIENT_SLUG = ""     # URL-safe slug for logo filename: {CLIENT_SLUG}-logo.png, e.g. "danimals"

# Logo paths — absolute file paths confirmed with user before running
DIGITAD_LOGO_PATH = ""   # e.g. "/Users/you/claude_code/digitad-logo.png"
CLIENT_LOGO_PATH  = ""   # e.g. "/Users/you/claude_code/danimals-logo.png"

# Optional overall score override — set to an int to use instead of the computed average.
# Use when the exec summary states a specific score that differs from the weighted average.
# Set to None to use the computed average from workbook_data.json.
# Example (Danimals): OVERALL_SCORE_OVERRIDE = 40
OVERALL_SCORE_OVERRIDE = None

# Executive summary paragraphs for the index.html hero (HTML-safe strings).
# Pull from the Executive Summary .md — plain text, no element codes, no scores.
# Example (Danimals):
# EXEC_SUMMARY_PARAS = [
#     "Danimals has a solid technical infrastructure and clean security profile — the site is "
#     "fully secured with valid SSL, HTTP correctly redirects to HTTPS sitewide, AI crawlers "
#     "are permitted access through robots.txt, and domain integrity is not a concern.",
#     "The most urgent priorities centre on content structure and social discoverability. "
#     "Social meta tags are entirely absent sitewide — every share on Facebook, Instagram, "
#     "or LinkedIn generates an uncontrolled preview.",
#     "The site publishes no blog, recipes, or editorial content, which means it cannot appear "
#     "in informational search results or AI-generated responses for any query beyond brand-specific searches.",
# ]
EXEC_SUMMARY_PARAS = []

# Priority matrix scatter dots — 5 to 7 items, defined manually per audit.
# Each dict keys: label, href (target page), x (0–100, 0=hard 100=easy),
#                 y (0–100, 0=high impact 100=low impact), color, shadow, tooltip
# Dot color by phase — Technical/UX/Tools: rgba(54,68,87,0.88) slate
#                      On-Site/Off-Site:   rgba(184,0,28,0.88) red
#                      GEO:                rgba(25,113,194,0.88) blue
#                      Schema:             rgba(140,0,18,0.88) dark red
# Example (Danimals):
# PRIORITY_MATRIX_DOTS = [
#     {"label": "Content Hub",    "href": "geo.html",      "x": 18, "y": 10,
#      "color": "rgba(25,113,194,0.88)", "shadow": "rgba(25,113,194,0.32)",
#      "tooltip": "No blog or articles published. A content hub opening two articles per month opens an entirely new acquisition channel within 6–12 months."},
#     {"label": "TL;DR Summaries","href": "geo.html",      "x": 68, "y": 12,
#      "color": "rgba(25,113,194,0.88)", "shadow": "rgba(25,113,194,0.32)",
#      "tooltip": "No introductory paragraphs on any page. Adding a 2–4 sentence summary is the fastest lever for AI Overview citation eligibility."},
#     {"label": "Social Meta Tags","href": "on-site.html", "x": 60, "y": 20,
#      "color": "rgba(184,0,28,0.88)",  "shadow": "rgba(184,0,28,0.32)",
#      "tooltip": "No Open Graph or Twitter Card tags exist sitewide. Every social share generates an uncontrolled preview."},
#     {"label": "llms.txt",       "href": "geo.html",      "x": 84, "y": 7,
#      "color": "rgba(25,113,194,0.88)", "shadow": "rgba(25,113,194,0.32)",
#      "tooltip": "No llms.txt file present. Note: Google does not currently endorse llms.txt — this dot is left as a placeholder example only."},
#     {"label": "FAQ Heading Fix", "href": "geo.html",     "x": 52, "y": 26,
#      "color": "rgba(25,113,194,0.88)", "shadow": "rgba(25,113,194,0.32)",
#      "tooltip": "25 FAQ pairs use H4 headings. Changing to H3 improves LLM extraction — FAQPage schema is no longer a Google-supported rich result type."},
#     {"label": "HTTP Backlinks",  "href": "off-site.html","x": 24, "y": 38,
#      "color": "rgba(86,95,106,0.88)",  "shadow": "rgba(86,95,106,0.32)",
#      "tooltip": "73% of inbound backlinks still target the HTTP URL. Updating the 13 highest-quality referring domains to HTTPS is a targeted, high-return outreach effort."},
# ]
PRIORITY_MATRIX_DOTS = []

# Data sources carousel — confirmed tools from Phase 0 session log.
# Use Material Symbols icon names (see https://fonts.google.com/icons).
# Example (Danimals):
# DATA_SOURCES = [
#     {"name": "PageSpeed",      "icon": "monitoring"},
#     {"name": "GTmetrix",       "icon": "speed"},
#     {"name": "Screaming Frog", "icon": "bug_report"},
#     {"name": "Majestic",       "icon": "link"},
#     {"name": "Moz",            "icon": "search_check"},
#     {"name": "SE Ranking",     "icon": "query_stats"},
#     {"name": "WHOIS",          "icon": "domain"},
#     {"name": "Lumen Database", "icon": "gavel"},
# ]
DATA_SOURCES = []

# Phase metadata — file, labels, description for hero sections
# Map from workbook family values to PHASE_META keys
FAMILY_KEY_MAP = {
    "Technical":            "Technical",
    "UX":                   "User Experience",
    "User Experience":      "User Experience",
    "Tools & Configuration":"Tools & Configuration",
    "On-Site SEO":          "On-Site SEO",
    "Off-Site":             "Off-Site",
    "GEO / AI Visibility":  "GEO / AI Visibility",
}

PHASE_META = {
    "Technical": {
        "file": "technical.html",
        "nav_label": "Technical",
        "eyebrow": "Technical",
        "h1": "Technical",
        "desc": "The technical audit examines crawlability, indexation, site speed, security, platform configuration, and code quality — the infrastructure search engines depend on to access, interpret, and rank content.",
        "sub": "Sitemap structure, canonical tags, redirect chains, Core Web Vitals, HTTP security headers, and CMS configuration are all examined against current best practice.",
    },
    "User Experience": {
        "file": "ux.html",
        "nav_label": "User Experience",
        "eyebrow": "User Experience",
        "h1": "User Experience",
        "desc": "The user experience audit assesses mobile usability, page speed delivery, navigation structure, accessibility compliance, and the design elements that influence how visitors engage with and navigate the site.",
        "sub": "Mobile rendering, above-the-fold loading, font sizing, tap target compliance, and navigation clarity are assessed against Google's usability guidelines.",
    },
    "Tools & Configuration": {
        "file": "tools.html",
        "nav_label": "Tools &amp; Config",
        "eyebrow": "Tools &amp; Config",
        "h1": "Tools &amp; Config",
        "desc": "The tools and configuration audit examines analytics setup, tracking integrity, Search Console configuration, and the measurement infrastructure required to act on performance data.",
        "sub": "GA4 event tracking, Google Tag Manager configuration, Search Console verification, and third-party pixel integrity are all reviewed.",
    },
    "On-Site SEO": {
        "file": "on-site.html",
        "nav_label": "On-Site SEO",
        "eyebrow": "On-Site SEO",
        "h1": "On-Site SEO",
        "desc": "The on-site audit covers title tags, meta descriptions, heading structure, content quality, internal linking, image optimisation, schema markup, and the page-level signals that determine how individual pages rank and appear in search.",
        "sub": "Title tag lengths, duplicate headings, missing alt attributes, thin content pages, internal linking gaps, and Open Graph coverage are assessed against current SEO best practice.",
    },
    "Off-Site": {
        "file": "off-site.html",
        "nav_label": "Off-Site",
        "eyebrow": "Off-Site",
        "h1": "Off-Site",
        "desc": "The off-site audit examines the backlink profile, domain authority, referring domain quality, anchor text distribution, spam score, and the external signals that contribute to domain trust and authority.",
        "sub": "Majestic backlink export, Moz Domain Authority and Spam Score, WHOIS registration history, Lumen Database copyright check, and competitor backlink gap analysis are all reviewed.",
    },
    "GEO / AI Visibility": {
        "file": "geo.html",
        "nav_label": "GEO",
        "eyebrow": "GEO / AI Visibility",
        "h1": "GEO / AI Visibility",
        "desc": "The GEO audit assesses how and how often the brand appears in AI Overviews, large language model citations, and generative search across Google, ChatGPT, Perplexity, and Bing Copilot.",
        "sub": "AI Overview presence, entity clarity, structured data signals, Bing indexation, and content structure for AI extraction are all assessed.",
    },
}

# ============================================================
# SCORE HELPERS
# ============================================================

SCORE_VALUES = {
    "Not Present": 1, "Weak": 2, "Medium": 3, "High": 4, "Excellent": 5
}

def element_score(score_label):
    """Normalise a rating label to 0–100. Returns None for non-scoreable rows."""
    v = SCORE_VALUES.get(score_label)
    return round((v - 1) / 4 * 100) if v is not None else None

def bar_width_pct(score_label):
    """Returns bar width % (minimum 2% so bar is always visible)."""
    s = element_score(score_label)
    if s is None:
        return None
    return max(2, s)

def ring_color_hex(score):
    """Returns hex color for score ring fill."""
    if score is None: return "#868e96"
    if score < 50:    return "#e03131"
    if score < 75:    return "#f08c00"
    return "#2f9e44"

def section_bar_color_cls(score):
    """Returns Tailwind bg class for section score bar."""
    if score is None: return "bg-zinc-400"
    if score < 50:    return "bg-primary"
    if score < 75:    return "bg-[#f08c00]"
    return "bg-[#2f9e44]"

def section_bar_color_text(score):
    """Returns Tailwind text class for section score label."""
    if score is None: return "text-zinc-400"
    if score < 50:    return "text-primary"
    if score < 75:    return "text-[#f08c00]"
    return "text-[#2f9e44]"

def priority_bar_color(priority):
    """Returns hex color for element bar chart fill."""
    return {
        "HIGH":    "#b8001c",
        "MEDIUM":  "#f08c00",
        "LOW":     "#2f9e44",
        "MONITOR": "#868e96",
        "Manual Verification Required": "#1971c2",
    }.get(priority, "#cccccc")

def accordion_color(priority):
    """Returns hex color for accordion border/icon/header."""
    return {
        "HIGH":    "#e03131",
        "MEDIUM":  "#f08c00",
        "LOW":     "#2f9e44",
        "MONITOR": "#868e96",
        "Manual Verification Required": "#1971c2",
    }.get(priority, "#868e96")

PRIORITY_ORDER = ["HIGH", "MEDIUM", "LOW", "MONITOR", "Manual Verification Required"]

def sort_priority(p):
    try:
        return PRIORITY_ORDER.index(p)
    except ValueError:
        return len(PRIORITY_ORDER)

def compute_scores(rows):
    """
    Returns:
      overall_score: int
      phase_scores: {family_name: int}
      priority_counts: {priority: int}  (overall)
      phase_priority_counts: {family_name: {priority: int}}
    """
    # Overall
    scoreable = [r for r in rows if element_score(r.get("score")) is not None]
    overall = round(sum(element_score(r["score"]) for r in scoreable) / len(scoreable)) if scoreable else 0

    # Per phase (map raw family values to PHASE_META keys first)
    phase_scores = {}
    for phase_key in PHASE_META:
        phase_rows = [r for r in scoreable if FAMILY_KEY_MAP.get(r.get("family", ""), r.get("family", "")) == phase_key]
        if phase_rows:
            phase_scores[phase_key] = round(sum(element_score(r["score"]) for r in phase_rows) / len(phase_rows))
        else:
            phase_scores[phase_key] = 0

    # Priority counts (overall)
    priority_counts = {}
    for r in rows:
        p = r.get("priority", "")
        if p in PRIORITY_ORDER:
            priority_counts[p] = priority_counts.get(p, 0) + 1

    # Per-phase priority counts
    phase_priority_counts = {}
    for phase_key in PHASE_META:
        phase_rows = [r for r in rows if FAMILY_KEY_MAP.get(r.get("family", ""), r.get("family", "")) == phase_key]
        counts = {}
        for r in phase_rows:
            p = r.get("priority", "")
            if p in PRIORITY_ORDER:
                counts[p] = counts.get(p, 0) + 1
        phase_priority_counts[phase_key] = counts

    return overall, phase_scores, priority_counts, phase_priority_counts

# ============================================================
# HTML ESCAPING
# ============================================================

def h(text):
    """HTML-escape a string."""
    if not text:
        return ""
    return (str(text)
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;"))

def format_body_text(text):
    """Convert plain text (with \n paragraphs) to HTML paragraphs."""
    if not text:
        return ""
    paras = [p.strip() for p in str(text).split("\n\n") if p.strip()]
    if not paras:
        paras = [text.strip()]
    return "\n".join(f'<p class="text-sm text-zinc-600 leading-relaxed">{h(p)}</p>' for p in paras)

def format_how_to(text):
    """Convert bullet-pointed text (• item) to HTML."""
    if not text:
        return ""
    lines = [ln.strip() for ln in str(text).split("\n") if ln.strip()]
    items = []
    in_list = False
    html_parts = []
    for ln in lines:
        if ln.startswith("•"):
            items.append(f"<li>{h(ln[1:].strip())}</li>")
        else:
            if items:
                html_parts.append(f'<ul class="list-disc list-inside space-y-1">' + "".join(items) + "</ul>")
                items = []
            html_parts.append(f'<p>{h(ln)}</p>')
    if items:
        html_parts.append(f'<ul class="list-disc list-inside space-y-1">' + "".join(items) + "</ul>")
    return "\n".join(html_parts)

# ============================================================
# ELEMENT ICON LOOKUP
# ============================================================

ICON_KEYWORDS = [
    ("sitemap", "map"),
    ("robots.txt", "smart_toy"),
    ("robots", "policy"),
    ("canonical", "merge"),
    ("404", "error"),
    ("redirect", "alt_route"),
    ("https", "lock"),
    ("ssl", "security"),
    ("wp-admin", "admin_panel_settings"),
    ("admin panel", "admin_panel_settings"),
    ("wordpress", "web"),
    ("pagespeed", "speed"),
    ("core web vital", "monitor_heart"),
    ("gtmetrix", "speed"),
    ("javascript", "code"),
    ("css", "css"),
    ("lazy load", "image_search"),
    ("image", "image"),
    ("cdn", "cloud"),
    ("html-to-text", "article"),
    ("html ratio", "article"),
    ("w3c", "verified"),
    ("encoding", "translate"),
    ("charset", "translate"),
    ("server", "dns"),
    ("schema", "data_object"),
    ("structured data", "data_object"),
    ("mobile", "phone_iphone"),
    ("navigation", "menu"),
    ("breadcrumb", "alt_route"),
    ("font", "font_download"),
    ("color contrast", "palette"),
    ("accessibility", "accessibility"),
    ("cookie", "cookie"),
    ("referrer", "policy"),
    ("security header", "security"),
    ("hsts", "security"),
    ("content", "article"),
    ("word count", "article"),
    ("thin content", "article"),
    ("title tag", "title"),
    ("meta description", "description"),
    ("h1", "format_h1"),
    ("h2", "format_h2"),
    ("heading", "title"),
    ("alt text", "image"),
    ("alt tag", "image"),
    ("alt attribute", "image"),
    ("internal link", "hub"),
    ("anchor text", "link"),
    ("external link", "open_in_new"),
    ("open graph", "share"),
    ("og:", "share"),
    ("twitter card", "share"),
    ("social meta", "share"),
    ("backlink", "link"),
    ("domain authority", "verified"),
    ("spam score", "report"),
    ("disavow", "block"),
    ("lumen", "gavel"),
    ("whois", "domain"),
    ("google analytics", "monitoring"),
    ("ga4", "monitoring"),
    ("google tag", "tag"),
    ("gtm", "tag"),
    ("search console", "search"),
    ("gsc", "search"),
    ("bing", "search"),
    ("indexnow", "flash_on"),
    ("ai overview", "auto_awesome"),
    ("llm", "psychology"),
    ("chatgpt", "psychology"),
    ("gemini", "psychology"),
    ("perplexity", "psychology"),
    ("tl;dr", "short_text"),
    ("intro paragraph", "short_text"),
    ("entity", "business"),
    ("wikipedia", "auto_stories"),
    ("wikidata", "auto_stories"),
    ("social profile", "share"),
    ("facebook", "share"),
    ("instagram", "photo_camera"),
    ("youtube", "smart_display"),
    ("twitter", "share"),
    ("faq", "quiz"),
    ("review", "star"),
    ("rating", "star"),
    ("author", "person"),
    ("recaptcha", "smart_toy"),
    ("hreflang", "language"),
    ("competitor", "compare"),
]

def element_icon(element_name):
    """Returns a Material Symbol icon name for an element."""
    name_lower = (element_name or "").lower()
    for keyword, icon in ICON_KEYWORDS:
        if keyword in name_lower:
            return icon
    return "info"

# ============================================================
# TAILWIND CONFIG (shared across all pages)
# ============================================================

TAILWIND_COLORS = '''{
          "surface-tint": "#be091f", "on-surface": "#1a1c1c", "primary-fixed-dim": "#ffb3ae",
          "on-primary-fixed-variant": "#930014", "on-tertiary-fixed": "#0d1c2e",
          "secondary-container": "#dae3f0", "on-primary": "#ffffff", "on-surface-variant": "#5c403d",
          "error": "#ba1a1a", "tertiary": "#364457", "on-error": "#ffffff", "primary": "#8c0012",
          "background": "#f9f9f9", "on-tertiary-container": "#c4d3ea", "surface-dim": "#dadad9",
          "primary-container": "#b8001c", "on-primary-container": "#ffc4bf", "on-secondary": "#ffffff",
          "surface-container-low": "#f4f3f3", "on-primary-fixed": "#410004",
          "surface-container-lowest": "#ffffff", "inverse-on-surface": "#f1f1f0",
          "secondary": "#565f6a", "inverse-surface": "#2f3131", "surface-container-high": "#e8e8e8",
          "outline-variant": "#e5bdba", "on-tertiary": "#ffffff", "surface": "#f9f9f9",
          "tertiary-container": "#4d5b6f", "inverse-primary": "#ffb3ae", "error-container": "#ffdad6",
          "outline": "#906f6c", "surface-container": "#eeeeed", "surface-variant": "#e2e2e2",
          "surface-bright": "#f9f9f9", "primary-fixed": "#ffdad7",
          "surface-container-highest": "#e2e2e2", "on-background": "#1a1c1c"
        }'''

# ============================================================
# HTML HEAD
# ============================================================

def html_head(title, extra_styles=""):
    """Returns the <head> block. extra_styles is injected into <style>."""
    base_styles = """
  .material-symbols-outlined { font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24; }
  .editorial-shadow { box-shadow: 0 20px 40px rgba(26,28,28,0.04); }"""
    return f"""<!DOCTYPE html>
<html lang="en" class="light">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>{h(title)}</title>
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap" rel="stylesheet"/>
<link rel="preconnect" href="https://fonts.googleapis.com"/>
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin=""/>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Plus+Jakarta+Sans:wght@700;800&display=swap" rel="stylesheet"/>
<script src="https://cdn.tailwindcss.com?plugins=forms,container-queries"></script>
<script id="tailwind-config">
  tailwind.config = {{
    darkMode: "class",
    theme: {{
      extend: {{
        colors: {TAILWIND_COLORS},
        fontFamily: {{ "headline": ["Plus Jakarta Sans"], "body": ["Inter"], "label": ["Inter"] }},
        borderRadius: {{"DEFAULT": "0.125rem", "lg": "0.25rem", "xl": "0.5rem", "full": "9999px"}},
      }},
    }},
  }}
</script>
<style>{base_styles}{extra_styles}
</style>
</head>"""

# ============================================================
# NAV
# ============================================================

NAV_PAGES = [
    ("index.html",       "Overview"),
    ("technical.html",   "Technical"),
    ("ux.html",          "User Experience"),
    ("tools.html",       "Tools &amp; Config"),
    ("on-site.html",     "On-Site SEO"),
    ("off-site.html",    "Off-Site"),
    ("geo.html",         "GEO"),
    ("schema.html",      "Schema"),
    ("methodology.html", "Methodology"),
]

def nav_html(active_file, nav_height="h-20", pt="pt-20"):
    """Returns the sticky header nav HTML."""
    client_logo_file = f"{CLIENT_SLUG}-logo.png"
    links = []
    for file, label in NAV_PAGES:
        if file == active_file:
            links.append(
                f'<a href="{file}" class="text-on-surface font-medium bg-surface-container-low px-3 py-1 rounded-md font-headline text-sm tracking-tight">{label}</a>'
            )
        else:
            links.append(
                f'<a href="{file}" class="text-zinc-500 font-medium hover:text-zinc-800 transition-colors font-headline text-sm tracking-tight">{label}</a>'
            )
    links_html = "\n      ".join(links)
    return f"""
<header class="fixed top-0 w-full z-50 bg-white/85 backdrop-blur-[20px] shadow-[0_8px_30px_rgb(0,0,0,0.04)]">
  <nav class="flex justify-between items-center {nav_height} px-8 w-full mx-auto max-w-[1920px]">
    <div class="flex items-center gap-4 flex-shrink-0">
      <img src="digitad-logo.png" alt="Digitad" class="h-7 w-auto"/>
      <span class="w-px h-5 bg-zinc-200"></span>
      <img src="{client_logo_file}" alt="{h(CLIENT_NAME)}" class="h-7 w-auto rounded"/>
    </div>
    <div class="hidden md:flex items-center gap-5 text-sm font-medium font-headline">
      {links_html}
    </div>
    <div class="text-xs font-label text-zinc-400 tracking-widest uppercase flex-shrink-0">{h(CLIENT_NAME)} &middot; {h(AUDIT_DATE)}</div>
  </nav>
</header>"""

# ============================================================
# FOOTER + JS
# ============================================================

def footer_html():
    return f"""
<footer class="bg-zinc-900 w-full py-12 flex flex-col items-center justify-center text-center px-6">
  <p class="font-label text-[10px] uppercase tracking-[0.1em] font-medium text-zinc-400 opacity-80 hover:opacity-100 transition-colors">
    Prepared by Digitad &middot; {h(CLIENT_NAME)} &middot; SEO &amp; GEO Audit &middot; {h(AUDIT_DATE)}
  </p>
</footer>"""

def accordion_script():
    return """
<script>
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
</script>"""

# ============================================================
# SCORE RING
# ============================================================

def score_ring_html(score, r=90, viewbox=220):
    """Returns SVG score ring HTML snippet."""
    circ = round(2 * math.pi * r, 2)
    if score is None or score == 0:
        offset = circ
    else:
        offset = round(circ * (1 - score / 100), 2)
    color = ring_color_hex(score)
    size = viewbox
    return f"""<svg class="w-[{size}px] h-[{size}px] transform -rotate-90" viewBox="0 0 {viewbox} {viewbox}">
    <circle cx="{viewbox//2}" cy="{viewbox//2}" r="{r}" fill="transparent" stroke="#e2e2e2" stroke-width="14"/>
    <circle cx="{viewbox//2}" cy="{viewbox//2}" r="{r}" fill="transparent" stroke="{color}" stroke-width="14"
            stroke-dasharray="{circ}" stroke-dashoffset="{offset}" stroke-linecap="round"/>
  </svg>"""

# ============================================================
# BREADCRUMBS
# ============================================================

def breadcrumb_html(page_label):
    return f"""
  <div class="px-8 py-5 max-w-7xl mx-auto">
    <nav class="flex items-center gap-2 text-xs font-label uppercase tracking-widest text-zinc-400" aria-label="Breadcrumb">
      <a href="index.html" class="hover:text-primary transition-colors">Overview</a>
      <span class="material-symbols-outlined text-[12px]">chevron_right</span>
      <span class="text-primary font-bold">{page_label}</span>
    </nav>
  </div>"""

# ============================================================
# PRIORITY BADGES
# ============================================================

def priority_badges_linked(counts, prefix=""):
    """Priority badge row with anchor links for section pages."""
    badges = []
    anchors = {
        "HIGH":    "#high-issues",
        "MEDIUM":  "#medium-issues",
        "LOW":     "#low-issues",
        "MONITOR": "#monitor-items",
    }
    styles = {
        "HIGH":    ("bg-primary", "text-white"),
        "MEDIUM":  ("border border-[#f08c00]", "text-[#f08c00]"),
        "LOW":     ("border border-[#2f9e44]", "text-[#2f9e44]"),
        "MONITOR": ("border border-zinc-400", "text-zinc-500"),
    }
    for p in ["HIGH", "MEDIUM", "LOW", "MONITOR"]:
        n = counts.get(p, 0)
        if n == 0:
            continue
        cls, txt_cls = styles[p]
        label = p.capitalize() if p != "MONITOR" else "Monitor"
        badges.append(
            f'<a href="{anchors[p]}" class="{cls} px-4 py-2 rounded-full flex items-center gap-2 no-underline hover:opacity-80 transition-opacity">'
            f'<span class="{txt_cls} text-[10px] font-bold font-label uppercase tracking-widest">{label} {n}</span>'
            f'</a>'
        )
    # Passing items link
    passing_count = counts.get("Passing", 0)
    if passing_count:
        badges.append(
            f'<a href="#passing-items" class="border border-zinc-400 px-4 py-2 rounded-full flex items-center gap-2 no-underline hover:opacity-80 transition-opacity">'
            f'<span class="text-zinc-500 text-[10px] font-bold font-label uppercase tracking-widest">Passing {passing_count}</span>'
            f'</a>'
        )
    return "\n".join(badges)

def priority_badges_static(counts):
    """Priority badge row (non-linked) for index.html."""
    badges = []
    styles = {
        "HIGH":    ("bg-primary", "text-white"),
        "MEDIUM":  ("border border-[#f08c00]", "text-[#f08c00]"),
        "LOW":     ("border border-[#2f9e44]", "text-[#2f9e44]"),
        "MONITOR": ("border border-zinc-400", "text-zinc-500"),
    }
    for p in ["HIGH", "MEDIUM", "LOW", "MONITOR"]:
        n = counts.get(p, 0)
        if n == 0:
            continue
        cls, txt_cls = styles[p]
        label = p.capitalize() if p != "MONITOR" else "Monitor"
        badges.append(
            f'<div class="{cls} px-4 py-2 rounded-full flex items-center gap-2">'
            f'<span class="{txt_cls} text-[10px] font-bold tracking-widest font-label uppercase">{label} {n}</span>'
            f'</div>'
        )
    return "\n".join(badges)

# ============================================================
# ELEMENT BAR CHART
# ============================================================

def element_bar_chart_html(rows):
    """Generates the element breakdown bar chart for a section page."""
    scoreable = [r for r in rows if element_score(r.get("score")) is not None]
    if not scoreable:
        return '<p class="text-sm text-zinc-400 italic">No scored elements.</p>'

    sorted_rows = sorted(scoreable, key=lambda r: sort_priority(r.get("priority", "")))
    bars = []
    for r in sorted_rows:
        elem = h(r.get("element", ""))
        desc = h(r.get("sub_category", ""))
        label = f"{elem}" + (f" &mdash; {desc}" if desc else "")
        pct = bar_width_pct(r["score"])
        p = r.get("priority", "MONITOR")
        color = priority_bar_color(p)
        p_label = p if p in ["HIGH", "MEDIUM", "LOW", "MONITOR"] else p[:3].upper() if p else "—"
        bars.append(
            f'<div class="grid grid-cols-[1fr_200px_60px] items-center gap-4">'
            f'<span class="text-xs font-body text-zinc-600 truncate">{label}</span>'
            f'<div class="h-2 bg-surface-container-highest rounded-full overflow-hidden">'
            f'<div class="h-full rounded-full" style="width:{pct}%;background:{color};"></div>'
            f'</div>'
            f'<span class="text-xs font-label font-bold text-right" style="color:{color};">{p_label}</span>'
            f'</div>'
        )
    return "\n".join(bars)

# ============================================================
# ACCORDION CARD (ISSUE/OPPORTUNITY)
# ============================================================

def accordion_card_html(row, priority):
    """Generates a single accordion card for an issue or opportunity row."""
    color = accordion_color(priority)
    icon = element_icon(row.get("element", ""))
    elem_name = h(row.get("element", "Unknown element"))
    what_it_is = format_body_text(row.get("description", ""))
    why_problem = format_body_text(row.get("explanation", ""))
    how_to_fix = format_how_to(row.get("how_to", ""))

    if row.get("status") == "Opportunity":
        col2_label = "Why it is an opportunity"
        col3_label = "How to take advantage"
    else:
        col2_label = "Why it is a problem"
        col3_label = "How to fix it"

    return f"""
      <div class="bg-white editorial-shadow accordion-card border-l-[6px] rounded-r-xl" style="border-color:{color};">
        <div class="flex items-center p-6 accordion-trigger cursor-pointer gap-4">
          <div class="w-10 h-10 flex items-center justify-center rounded-full shrink-0" style="background:{color}20;color:{color};">
            <span class="material-symbols-outlined text-xl">{icon}</span>
          </div>
          <div class="flex-1 min-w-0">
            <h3 class="font-headline font-bold text-base text-on-surface">{elem_name}</h3>
          </div>
          <span class="material-symbols-outlined text-zinc-400 accordion-icon transition-transform shrink-0">expand_more</span>
        </div>
        <div class="accordion-content hidden mx-6 mb-0 p-8 bg-surface-container-low rounded-lg grid grid-cols-1 md:grid-cols-3 gap-8">
          <div>
            <h4 class="text-[10px] font-label font-extrabold uppercase tracking-widest mb-3" style="color:{color};">What it is</h4>
            <div class="text-sm text-zinc-600 leading-relaxed space-y-2">{what_it_is}</div>
          </div>
          <div>
            <h4 class="text-[10px] font-label font-extrabold uppercase tracking-widest mb-3" style="color:{color};">{col2_label}</h4>
            <div class="text-sm text-zinc-600 leading-relaxed space-y-2">{why_problem}</div>
          </div>
          <div>
            <h4 class="text-[10px] font-label font-extrabold uppercase tracking-widest mb-3" style="color:{color};">{col3_label}</h4>
            <div class="text-sm text-zinc-600 leading-relaxed space-y-2">{how_to_fix}</div>
          </div>
        </div>
      </div>"""

# ============================================================
# PASSING ITEMS SECTION
# ============================================================

def is_passing_item(row):
    """Infer whether a row is a passing/correct item (score High/Excellent + MONITOR priority)."""
    return row.get("priority") == "MONITOR" and row.get("score") in ("High", "Excellent")

def passing_section_html(rows):
    """Generates the collapsible passing items section."""
    passing = [r for r in rows if is_passing_item(r)]
    if not passing:
        return ""
    count = len(passing)
    items = []
    for r in passing:
        items.append(
            f'<div class="flex items-start gap-3 py-3 px-4 bg-surface-container-lowest rounded-lg">'
            f'<span class="material-symbols-outlined text-[#2f9e44] text-base mt-0.5 shrink-0">check</span>'
            f'<div><p class="text-sm font-body font-semibold text-zinc-700">{h(r.get("element", ""))}</p>'
            f'<p class="text-xs text-zinc-500 mt-0.5 leading-relaxed">{h(r.get("explanation", ""))}</p></div>'
            f'</div>'
        )
    items_html = "\n          ".join(items)
    return f"""
    <div id="passing-items">
      <details class="group bg-white editorial-shadow p-6 rounded-xl cursor-pointer">
        <summary class="flex items-center gap-4 list-none">
          <span class="material-symbols-outlined text-[#2f9e44] text-lg">check_circle</span>
          <span class="font-headline font-bold text-base text-zinc-600">No issues found &mdash; {count} element{"s" if count != 1 else ""} passing</span>
          <span class="material-symbols-outlined text-zinc-400 ml-auto group-open:rotate-180 transition-transform">expand_more</span>
        </summary>
        <div class="mt-3 space-y-2 px-2">
          {items_html}
        </div>
      </details>
    </div>"""

# ============================================================
# PRIORITY GROUP (accordion section)
# ============================================================

def priority_group_html(priority, rows_for_priority):
    """Generates a full priority group section (heading + accordion cards)."""
    if not rows_for_priority:
        return ""
    anchor = {
        "HIGH":    "high-issues",
        "MEDIUM":  "medium-issues",
        "LOW":     "low-issues",
        "MONITOR": "monitor-items",
    }.get(priority, "other-issues")
    color = accordion_color(priority)
    label = {
        "HIGH":    "High Priority",
        "MEDIUM":  "Medium Priority",
        "LOW":     "Low Priority",
        "MONITOR": "Monitor",
    }.get(priority, priority)
    n = len(rows_for_priority)
    cards = "\n".join(accordion_card_html(r, priority) for r in rows_for_priority)
    return f"""
    <div id="{anchor}" class="space-y-5 scroll-mt-20">
      <div class="flex items-center justify-between mb-2">
        <h2 class="text-xl font-headline font-bold text-on-surface">{label}</h2>
        <span class="px-3 py-1 text-white text-[10px] font-bold uppercase rounded-full tracking-wider" style="background:{color};">{n} item{"s" if n != 1 else ""}</span>
      </div>
      {cards}
    </div>"""

# ============================================================
# GENERATE: INDEX.HTML
# ============================================================

def generate_index(rows, overall_score, phase_scores, priority_counts):
    """Generates index.html — the audit overview page."""
    extra_styles = """
  .mask-edges {
    mask-image: linear-gradient(to right, transparent, black 8%, black 92%, transparent);
    -webkit-mask-image: linear-gradient(to right, transparent, black 8%, black 92%, transparent);
  }
  @keyframes carousel-move {
    0% { transform: translateX(0); }
    100% { transform: translateX(-50%); }
  }
  .animate-carousel-move { animation: carousel-move 30s linear infinite; }
  .animate-carousel-move:hover { animation-play-state: paused; }
  .quadrant-hover-label {
    position: absolute; top: 50%; left: 50%;
    transform: translate(-50%, calc(-50% + 4px));
    opacity: 0; transition: opacity 0.18s ease, transform 0.18s ease;
    pointer-events: none; z-index: 40; white-space: nowrap;
  }
  .quadrant-zone:hover .quadrant-hover-label { opacity: 1; transform: translate(-50%, -50%); }
  .scatter-plot:has(.scatter-dot:hover) .quadrant-hover-label { opacity: 0 !important; }
  .scatter-dot > div { transition: transform 0.15s ease; }
  .scatter-dot:hover > div { transform: scale(1.12); }
  .dot-tooltip {
    position: absolute; top: calc(100% + 10px); left: 50%;
    transform: translateX(-50%) translateY(-4px); opacity: 0;
    transition: opacity 0.18s ease, transform 0.18s ease; pointer-events: none;
    z-index: 50; background: #1a1c1c; color: #fff;
    font-family: Inter, sans-serif; font-size: 11px; line-height: 1.5;
    padding: 8px 12px; border-radius: 6px;
    box-shadow: 0 4px 16px rgba(0,0,0,0.18); width: 210px; text-align: center;
  }
  .scatter-dot:hover .dot-tooltip { opacity: 1; transform: translateX(-50%) translateY(0); }"""

    head = html_head(f"{CLIENT_NAME} — SEO & GEO Audit — {AUDIT_DATE}", extra_styles)
    nav = nav_html("index.html", "h-20", "pt-20")

    # Exec summary paragraphs
    exec_paras_html = "\n".join(
        f'<p class="text-zinc-700 text-base leading-relaxed font-body">{p}</p>'
        for p in EXEC_SUMMARY_PARAS
    )

    # Section descriptions bullet list
    section_bullets = """<div class="pt-2 space-y-2 text-sm text-zinc-500 font-body leading-relaxed">
            <p><span class="text-zinc-800 font-semibold">Technical &amp; UX</span> — Crawlability, indexation, site speed, Core Web Vitals, and mobile usability. The health of the infrastructure search engines depend on.</p>
            <p><span class="text-zinc-800 font-semibold">On-Site SEO &amp; Off-Site</span> — Title tags, content quality, internal linking, backlink profile, and the on- and off-page signals that determine how individual pages rank.</p>
            <p><span class="text-zinc-800 font-semibold">Tools &amp; Configuration</span> — Analytics setup, Search Console accuracy, and the measurement infrastructure needed to act on performance data.</p>
            <p><span class="text-zinc-800 font-semibold">GEO / AI Visibility</span> — How and how often the brand appears in AI Overviews, large language model citations, and generative search across major platforms.</p>
            <p><span class="text-zinc-800 font-semibold">Schema</span> — Structured data markup that enables rich results, knowledge panel features, and machine-readable content signals.</p>
          </div>"""

    # Priority badges (static, no links)
    badges_html = priority_badges_static(priority_counts)

    # Score ring (220px, r=90)
    ring = score_ring_html(overall_score, r=90, viewbox=220)

    # Priority matrix dots
    dots_html = ""
    for dot in PRIORITY_MATRIX_DOTS:
        # x=0 is hard (left), x=100 is easy (right)
        # y=0 is high impact (top), y=100 is low impact (bottom)
        left_pct = dot["x"]
        top_pct = dot["y"]
        dots_html += f"""
              <a href="{dot['href']}" class="scatter-dot absolute flex flex-col items-center" style="left:{left_pct}%;top:{top_pct}%;transform:translate(-50%,-50%);z-index:30;text-decoration:none;">
                <div class="w-10 h-10 rounded-full" style="background:{dot['color']};box-shadow:0 4px 14px {dot['shadow']};"></div>
                <span class="text-[11px] font-semibold font-label whitespace-nowrap mt-1.5" style="color:#364457;">{h(dot['label'])}</span>
                <div class="dot-tooltip">{h(dot['tooltip'])}</div>
              </a>"""

    # Section score bars
    score_bars = []
    bar_items = [
        ("Technical",          "technical.html", "Technical"),
        ("User Experience",    "ux.html",        "User Experience"),
        ("Tools & Configuration", "tools.html",  "Tools &amp; Configuration"),
        ("On-Site SEO",        "on-site.html",   "On-Site SEO"),
        ("Off-Site",           "off-site.html",  "Off-Site"),
        ("GEO / AI Visibility","geo.html",        "GEO / AI Visibility"),
    ]
    for family, href, label in bar_items:
        score = phase_scores.get(family, 0)
        bar_cls = section_bar_color_cls(score)
        txt_cls = section_bar_color_text(score)
        score_bars.append(f"""
          <div class="grid grid-cols-1 md:grid-cols-[240px_1fr_80px] items-center gap-8 group">
            <a href="{href}" class="text-tertiary font-headline font-bold tracking-tight group-hover:text-primary transition-colors flex items-center gap-2">
              {label}
              <span class="material-symbols-outlined text-sm opacity-0 group-hover:opacity-100 transition-opacity">arrow_forward</span>
            </a>
            <div class="h-3 bg-surface-container-low rounded-full overflow-hidden">
              <div class="h-full {bar_cls} rounded-full" style="width:{score}%"></div>
            </div>
            <span class="text-right font-headline font-bold {txt_cls}">{score}/100</span>
          </div>""")
    score_bars_html = "\n".join(score_bars)

    # Data sources carousel (duplicated for seamless loop)
    def carousel_item(src):
        return (f'<div class="flex flex-col items-center opacity-60 grayscale hover:grayscale-0 transition-all cursor-pointer">'
                f'<div class="w-12 h-12 bg-zinc-900/10 rounded-lg flex items-center justify-center mb-3">'
                f'<span class="material-symbols-outlined text-zinc-900">{src["icon"]}</span>'
                f'</div>'
                f'<span class="font-label text-[10px] font-bold tracking-widest text-zinc-800 uppercase">{h(src["name"])}</span>'
                f'</div>')
    set1 = "\n".join(carousel_item(s) for s in DATA_SOURCES)
    set2 = set1  # duplicate for seamless loop

    return f"""{head}
<body class="bg-surface text-on-surface font-body antialiased">
{nav}
<main class="pt-20">

  <!-- Hero / Executive Summary -->
  <section class="relative bg-white border-b-[3px] border-primary py-24 overflow-hidden">
    <div class="absolute right-0 top-0 w-[500px] h-[500px] bg-primary/5 blur-[100px] rounded-full pointer-events-none"></div>
    <div class="max-w-[1440px] mx-auto px-12 grid grid-cols-1 lg:grid-cols-2 gap-20 items-center relative z-10">

      <!-- Left: Summary -->
      <div>
        <div class="flex items-center gap-4 mb-6">
          <div class="w-12 h-[2px] bg-primary"></div>
          <span class="text-primary font-headline text-xs tracking-[0.2em] font-bold uppercase">Digitad &mdash; SEO &amp; GEO Technical Audit</span>
        </div>
        <h1 class="text-on-surface text-6xl md:text-7xl font-headline font-bold mb-4 tracking-tight">{h(CLIENT_NAME)}</h1>
        <p class="text-zinc-500 font-headline text-lg mb-8 tracking-wide">{h(AUDIT_DATE)}</p>
        <div class="max-w-xl space-y-5">
          {exec_paras_html}
          {section_bullets}
        </div>
      </div>

      <!-- Right: Score Ring + Priority Badges -->
      <div class="flex flex-col items-center">
        <div class="relative mb-10">
          {ring}
          <div class="absolute inset-0 flex flex-col items-center justify-center">
            <span class="text-on-surface text-6xl font-headline font-bold leading-none">{overall_score}</span>
            <span class="text-zinc-500 font-label text-xs uppercase tracking-widest mt-2">out of 100</span>
          </div>
        </div>
        <div class="flex flex-wrap gap-3 justify-center">
          {badges_html}
        </div>
      </div>

    </div>
  </section>

  <!-- Priority Matrix -->
  <section class="bg-surface-container-lowest py-24">
    <div class="max-w-[1440px] mx-auto px-12">
      <div class="bg-white rounded-xl p-12 shadow-[0_8px_40px_rgba(26,28,28,0.04)]">
        <div class="flex items-center mb-4">
          <div class="w-[3px] h-[22px] bg-primary mr-5 rounded-full"></div>
          <h2 class="text-tertiary font-headline text-2xl font-bold tracking-tight pr-8">Prioritization Matrix</h2>
          <div class="flex-grow h-[1px] bg-surface-container-highest"></div>
        </div>
        <p class="text-sm text-zinc-500 font-body mb-12 max-w-xl">Top findings ranked by impact versus implementation effort. Hover a quadrant to see what it means.</p>
        <div class="flex gap-4">
          <!-- Y-axis label -->
          <div class="flex flex-col items-center justify-center gap-3 flex-shrink-0 w-8">
            <span class="material-symbols-outlined text-zinc-400 text-base" style="transform:rotate(-90deg)">arrow_upward</span>
            <span class="text-[10px] font-label font-extrabold uppercase tracking-widest text-zinc-400" style="writing-mode:vertical-rl;transform:rotate(180deg);letter-spacing:0.15em;">Impact</span>
            <span class="material-symbols-outlined text-zinc-400 text-base" style="transform:rotate(-90deg)">arrow_downward</span>
          </div>
          <div class="flex-1 flex flex-col gap-2">
            <div class="flex justify-start pl-1">
              <span class="text-[10px] font-label font-semibold uppercase tracking-widest text-zinc-400">High</span>
            </div>
            <!-- Scatter Plot -->
            <div class="scatter-plot relative rounded-lg overflow-hidden border border-[#e2e2e2]" style="height:480px;">
              <!-- Quadrant dividers -->
              <div class="absolute inset-0 pointer-events-none" style="z-index:5;background:linear-gradient(to right,transparent calc(50% - 0.5px),#e2e2e2 calc(50% - 0.5px),#e2e2e2 calc(50% + 0.5px),transparent calc(50% + 0.5px)),linear-gradient(to bottom,transparent calc(50% - 0.5px),#e2e2e2 calc(50% - 0.5px),#e2e2e2 calc(50% + 0.5px),transparent calc(50% + 0.5px));"></div>
              <!-- Quadrant zones -->
              <div class="quadrant-zone absolute top-0 left-0 w-1/2 h-1/2 cursor-default">
                <div class="quadrant-hover-label"><span class="px-3 py-1 bg-[#f08c00] text-white text-[10px] font-label font-bold uppercase tracking-widest rounded-full shadow-sm">Major Projects</span></div>
              </div>
              <div class="quadrant-zone absolute top-0 right-0 w-1/2 h-1/2 cursor-default">
                <div class="quadrant-hover-label"><span class="px-3 py-1 bg-[#2f9e44] text-white text-[10px] font-label font-bold uppercase tracking-widest rounded-full shadow-sm">Quick Wins</span></div>
              </div>
              <div class="quadrant-zone absolute bottom-0 left-0 w-1/2 h-1/2 cursor-default">
                <div class="quadrant-hover-label"><span class="px-3 py-1 bg-[#868e96] text-white text-[10px] font-label font-bold uppercase tracking-widest rounded-full shadow-sm">Reconsider</span></div>
              </div>
              <div class="quadrant-zone absolute bottom-0 right-0 w-1/2 h-1/2 cursor-default">
                <div class="quadrant-hover-label"><span class="px-3 py-1 bg-[#1971c2] text-white text-[10px] font-label font-bold uppercase tracking-widest rounded-full shadow-sm">Easy Fixes</span></div>
              </div>
              <!-- Scatter Dots -->
              {dots_html}
            </div>
            <div class="flex justify-start pl-1">
              <span class="text-[10px] font-label font-semibold uppercase tracking-widest text-zinc-400">Low</span>
            </div>
            <!-- X-axis -->
            <div class="flex items-center justify-between px-2 pt-1">
              <div class="flex items-center gap-1">
                <span class="material-symbols-outlined text-zinc-400 text-base">arrow_back</span>
                <span class="text-[10px] font-label font-semibold uppercase tracking-widest text-zinc-400">Hard</span>
              </div>
              <span class="text-[10px] font-label font-extrabold uppercase tracking-widest text-zinc-400">Ease of Implementation</span>
              <div class="flex items-center gap-1">
                <span class="text-[10px] font-label font-semibold uppercase tracking-widest text-zinc-400">Easy</span>
                <span class="material-symbols-outlined text-zinc-400 text-base">arrow_forward</span>
              </div>
            </div>
          </div>
        </div>
        <!-- Legend -->
        <div class="border-t border-[#e2e2e2] mt-10 pt-6">
          <span class="text-[10px] font-label font-extrabold uppercase tracking-widest text-zinc-400 block mb-3">Phase</span>
          <div class="flex flex-wrap gap-2">
            <span class="inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-[11px] font-semibold font-label text-white" style="background:#364457;"><span class="w-2 h-2 rounded-full inline-block" style="background:rgba(255,255,255,0.4);"></span>Technical</span>
            <span class="inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-[11px] font-semibold font-label text-white" style="background:#364457;"><span class="w-2 h-2 rounded-full inline-block" style="background:rgba(255,255,255,0.4);"></span>User Experience</span>
            <span class="inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-[11px] font-semibold font-label text-white" style="background:#364457;"><span class="w-2 h-2 rounded-full inline-block" style="background:rgba(255,255,255,0.4);"></span>Tools &amp; Config</span>
            <span class="inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-[11px] font-semibold font-label text-white" style="background:#b8001c;"><span class="w-2 h-2 rounded-full inline-block" style="background:rgba(255,255,255,0.4);"></span>On-Site SEO</span>
            <span class="inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-[11px] font-semibold font-label text-white" style="background:#1971c2;"><span class="w-2 h-2 rounded-full inline-block" style="background:rgba(255,255,255,0.4);"></span>GEO / AI Visibility</span>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- Section Score Bars -->
  <section class="bg-surface-container-low py-24">
    <div class="max-w-[1440px] mx-auto px-12">
      <div class="bg-surface-container-lowest rounded-xl p-12 shadow-[0_8px_40px_rgba(26,28,28,0.04)]">
        <div class="flex items-center mb-16">
          <div class="w-[3px] h-[22px] bg-primary mr-5 rounded-full"></div>
          <h2 class="text-tertiary font-headline text-2xl font-bold tracking-tight pr-8">Performance by Area</h2>
          <div class="flex-grow h-[1px] bg-surface-container-highest"></div>
        </div>
        <div class="space-y-10">
          {score_bars_html}
        </div>
      </div>
    </div>
  </section>

  <!-- Data Sources Carousel -->
  <section class="bg-[#f3f3f3] py-20">
    <div class="max-w-[1440px] mx-auto px-12">
      <div class="mb-10 text-center">
        <p class="font-headline text-[10px] font-bold tracking-[0.3em] uppercase text-primary mb-2">Integrated Audit Sources</p>
        <div class="w-12 h-[1px] bg-primary/30 mx-auto"></div>
      </div>
      <div class="relative overflow-hidden mask-edges py-8">
        <div class="flex items-center gap-24 whitespace-nowrap animate-carousel-move">
          {set1}
          {set2}
        </div>
      </div>
    </div>
  </section>

</main>
{footer_html()}
</body>
</html>"""

# ============================================================
# GENERATE: SECTION PAGE (technical, ux, tools, on-site, off-site, geo)
# ============================================================

def generate_section_page(family, rows):
    """Generates a phase section page (technical.html, ux.html, etc.)."""
    meta = PHASE_META[family]
    file = meta["file"]
    phase_rows = [r for r in rows if FAMILY_KEY_MAP.get(r.get("family", ""), r.get("family", "")) == family]

    # Compute scores
    scoreable = [r for r in phase_rows if element_score(r.get("score")) is not None]
    phase_score = round(sum(element_score(r["score"]) for r in scoreable) / len(scoreable)) if scoreable else 0

    # Count priorities for this phase (exclude passing items from MONITOR count)
    p_counts = {}
    for r in phase_rows:
        p = r.get("priority", "")
        if p in PRIORITY_ORDER and not is_passing_item(r) and element_score(r.get("score")) is not None:
            p_counts[p] = p_counts.get(p, 0) + 1
    # Count passing items separately
    passing_count = sum(1 for r in phase_rows if is_passing_item(r))
    p_counts["Passing"] = passing_count

    head = html_head(f"{meta['h1']} — {CLIENT_NAME} — SEO &amp; GEO Audit — {AUDIT_DATE}")
    nav = nav_html(file, "h-16", "pt-16")
    crumb = breadcrumb_html(meta["eyebrow"])

    # Score ring (200px, r=80)
    ring = score_ring_html(phase_score, r=80, viewbox=200)
    color = ring_color_hex(phase_score)

    # Priority badge row (linked)
    badges_html = priority_badges_linked(p_counts)

    # Element bar chart
    bar_chart = element_bar_chart_html(phase_rows)

    # Build accordion groups (exclude passing items and unscored rows from accordions)
    accordion_groups = []
    for priority in ["HIGH", "MEDIUM", "LOW", "MONITOR"]:
        group_rows = [r for r in phase_rows
                      if r.get("priority") == priority and not is_passing_item(r)
                      and element_score(r.get("score")) is not None]
        accordion_groups.append(priority_group_html(priority, group_rows))
    accordion_html = "\n".join(g for g in accordion_groups if g)

    # Passing items
    passing_html = passing_section_html(phase_rows)

    return f"""{head}
<body class="bg-surface-container-low font-body text-on-surface antialiased">
{nav}
<main class="pt-16">
  {crumb}

  <!-- Hero Section -->
  <section class="bg-white border-b-[3px] border-primary py-20 relative overflow-hidden">
    <div class="absolute right-0 top-0 w-[400px] h-[400px] bg-primary/5 blur-[100px] rounded-full pointer-events-none"></div>
    <div class="max-w-7xl mx-auto px-8 grid grid-cols-1 md:grid-cols-2 items-center gap-16 relative z-10">
      <div>
        <div class="flex items-center gap-4 mb-5">
          <div class="w-10 h-[2px] bg-primary"></div>
          <span class="text-primary font-headline font-bold uppercase tracking-[0.2em] text-xs">{meta['eyebrow']}</span>
        </div>
        <h1 class="text-5xl md:text-7xl font-headline font-extrabold tracking-tighter mb-6 leading-none text-on-surface">{meta['h1']}</h1>
        <div class="max-w-xl mb-10 space-y-3">
          <p class="text-zinc-700 text-base leading-relaxed">{meta['desc']}</p>
          <p class="text-zinc-500 text-sm leading-relaxed">{meta['sub']}</p>
        </div>
        <div class="flex flex-wrap gap-3">
          {badges_html}
        </div>
      </div>
      <!-- Score Ring -->
      <div class="flex justify-center md:justify-end">
        <div class="relative w-[200px] h-[200px]">
          {ring}
          <div class="absolute inset-0 flex flex-col items-center justify-center">
            <span class="text-5xl font-headline font-bold text-on-surface leading-none">{phase_score}</span>
            <span class="text-zinc-500 font-label text-xs uppercase tracking-widest mt-2">out of 100</span>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- Element Bar Chart -->
  <section class="py-16 px-8 max-w-7xl mx-auto">
    <div class="bg-surface-container-lowest rounded-xl p-10 editorial-shadow">
      <div class="flex items-center mb-10">
        <div class="w-[3px] h-5 bg-primary mr-4 rounded-full"></div>
        <h2 class="text-tertiary font-headline text-lg font-bold tracking-tight">Element Breakdown</h2>
      </div>
      <div class="space-y-4">
        {bar_chart}
      </div>
    </div>
  </section>

  <!-- Issue Accordions -->
  <section class="py-4 px-8 max-w-7xl mx-auto space-y-16 pb-24">
    {accordion_html}
    {passing_html}
  </section>

</main>
{footer_html()}
{accordion_script()}
</body>
</html>"""

# ============================================================
# GENERATE: SCHEMA.HTML
# ============================================================

def generate_schema_page(schema_rows):
    """Generates schema.html from parsed schema CSV rows."""
    head = html_head(f"Schema Markup — {CLIENT_NAME} — SEO &amp; GEO Audit — {AUDIT_DATE}")
    nav = nav_html("schema.html", "h-16", "pt-16")
    crumb = breadcrumb_html("Schema Markup")

    # Count statuses
    missing = sum(1 for r in schema_rows if "Not Implemented" in r.get("Implementation Status", "") or "absent" in r.get("Implementation Status", "").lower())
    partial = sum(1 for r in schema_rows if "Partial" in r.get("Implementation Status", ""))
    page_count = len(schema_rows)

    # Hero badges
    hero_badges = f"""
          <span class="px-4 py-2 rounded-full bg-[#e03131] flex items-center gap-2">
            <span class="text-white text-[10px] font-bold font-label uppercase tracking-widest">{missing} Not Implemented</span>
          </span>
          <span class="px-4 py-2 rounded-full border border-[#f08c00] flex items-center gap-2">
            <span class="text-[#f08c00] text-[10px] font-bold font-label uppercase tracking-widest">{partial} Partial</span>
          </span>
          <span class="px-4 py-2 rounded-full border border-zinc-400 flex items-center gap-2">
            <span class="text-zinc-500 text-[10px] font-bold font-label uppercase tracking-widest">{page_count} Page Templates</span>
          </span>"""

    # Schema cards
    def status_color(status):
        s = status.lower()
        if "not implemented" in s or "absent" in s:
            return "#e03131"
        if "partial" in s:
            return "#f08c00"
        if "correct" in s or "present" in s:
            return "#2f9e44"
        return "#868e96"

    def status_icon_label(status):
        s = status.lower()
        if "not implemented" in s or "absent" in s:
            return "close", "Not Implemented"
        if "partial" in s:
            return "warning", "Partial"
        return "check", "Correct"

    cards = []
    for r in schema_rows:
        page_type = h(r.get("Page Type", ""))
        schema_type = h(r.get("Schema Markup Type", ""))
        status = r.get("Implementation Status", "")
        current = h(r.get("Current Schema Markup", ""))
        recommended = h(r.get("Recommended Schema Markup", ""))
        notes = h(r.get("Recommendations", ""))
        color = status_color(status)
        icon_name, icon_label = status_icon_label(status)

        cards.append(f"""
      <div class="bg-white editorial-shadow rounded-r-xl border-l-[6px] p-8" style="border-color:{color};">
        <div class="flex items-center gap-3 mb-4">
          <div class="w-9 h-9 flex items-center justify-center rounded-full shrink-0" style="background:{color}20;color:{color};">
            <span class="material-symbols-outlined text-lg">data_object</span>
          </div>
          <div>
            <span class="text-[10px] font-label font-extrabold uppercase tracking-widest" style="color:{color};">{icon_label}</span>
            <h3 class="font-headline font-bold text-base text-on-surface">{page_type} &mdash; {schema_type}</h3>
          </div>
        </div>
        <p class="text-sm text-zinc-500 leading-relaxed mb-4"><strong class="text-zinc-700">Current state:</strong> {current}</p>
        <p class="text-sm text-zinc-700 leading-relaxed mb-4"><strong>Recommended action:</strong> {notes}</p>
      </div>""")

    cards_html = "\n".join(cards)

    return f"""{head}
<body class="bg-surface-container-low font-body text-on-surface antialiased">
{nav}
<main class="pt-16">
  {crumb}

  <!-- Hero Section -->
  <section class="bg-white border-b-[3px] border-primary py-20 relative overflow-hidden">
    <div class="absolute right-0 top-0 w-[400px] h-[400px] bg-primary/5 blur-[100px] rounded-full pointer-events-none"></div>
    <div class="max-w-7xl mx-auto px-8 relative z-10">
      <div class="flex items-center gap-4 mb-5">
        <div class="w-10 h-[2px] bg-primary"></div>
        <span class="text-primary font-headline font-bold uppercase tracking-[0.2em] text-xs">Schema Markup</span>
      </div>
      <h1 class="text-5xl md:text-7xl font-headline font-extrabold tracking-tighter mb-6 leading-none text-on-surface">Schema Markup</h1>
      <div class="max-w-2xl mb-10 space-y-3">
        <p class="text-zinc-700 text-base leading-relaxed">
          Structured data is present across multiple page templates but contains significant gaps — the Organization entity is absent sitewide, structured Q&amp;A markup is incomplete, and Product schema is missing from all product pages.
        </p>
        <p class="text-zinc-500 text-sm leading-relaxed">
          This page documents the current schema state, required corrections, and implementation sequence for all {page_count} reviewed page templates. Priority: Organization sameAs first, then Product schema per product template.
        </p>
      </div>
      <div class="flex flex-wrap gap-3">
        {hero_badges}
      </div>
    </div>
  </section>

  <!-- Schema Cards -->
  <section class="py-16 px-8 max-w-7xl mx-auto">
    <div class="flex items-center mb-8">
      <div class="w-[3px] h-5 bg-primary mr-4 rounded-full"></div>
      <h2 class="text-tertiary font-headline text-lg font-bold tracking-tight">Schema by Page Template</h2>
    </div>
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {cards_html}
    </div>
  </section>

</main>
{footer_html()}
</body>
</html>"""

# ============================================================
# GENERATE: METHODOLOGY.HTML
# ============================================================

def generate_methodology():
    """Generates the static methodology page."""
    head = html_head(f"Methodology — {CLIENT_NAME} — SEO &amp; GEO Audit — {AUDIT_DATE}")
    nav = nav_html("methodology.html", "h-16", "pt-16")
    crumb = breadcrumb_html("Methodology")

    phases = [
        ("technical.html",  "Phase 1 — Technical",          "26 elements",  "Crawlability, indexation, site speed, Core Web Vitals, HTTPS, security headers, CMS configuration, and code quality. Covers all infrastructure factors that search engines depend on to access and rank content."),
        ("ux.html",         "Phase 2 — User Experience",    "14 elements",  "Mobile usability, page speed delivery, navigation structure, font sizing, accessibility compliance, cookie compliance, and above-the-fold content quality."),
        ("tools.html",      "Phase 3 — Tools & Configuration", "11 elements", "GA4 analytics setup, Google Tag Manager configuration, pixel integrity, Search Console verification and coverage, Bing Webmaster Tools setup, and third-party tracking accuracy."),
        ("on-site.html",    "Phase 4 — On-Site SEO",        "26 elements",  "Title tags, meta descriptions, heading structure (H1–H2), content quality and depth, image alt attributes, Open Graph and social meta tags, internal linking, external linking, canonical implementation, and schema markup coverage."),
        ("off-site.html",   "Phase 5 — Off-Site",           "11 elements",  "Backlink profile (Majestic), Domain Authority and Spam Score (Moz), WHOIS registration history, Lumen Database copyright check, anchor text diversity, referring domain quality, and competitor backlink gap analysis."),
        ("geo.html",        "Phase 6 — GEO / AI Visibility", "26 elements", "AI Overview presence, LLM citation eligibility, entity clarity, TL;DR summaries, FAQ content structure, Bing indexation and IndexNow, structured data signals for AI extraction, and social profile entity linking."),
    ]

    phase_cards = []
    for href, name, count, desc in phases:
        phase_cards.append(f"""
      <a href="{href}" class="block bg-white editorial-shadow rounded-xl p-8 border-l-[6px] border-primary hover:shadow-lg transition-shadow no-underline">
        <div class="flex items-center justify-between mb-3">
          <h3 class="font-headline font-bold text-base text-on-surface">{h(name)}</h3>
          <span class="text-[10px] font-label font-extrabold uppercase tracking-widest text-primary">{count}</span>
        </div>
        <p class="text-sm text-zinc-500 leading-relaxed">{h(desc)}</p>
      </a>""")
    phases_html = "\n".join(phase_cards)

    scoring_rows = [
        ("Not Present", "1", "#e03131", "Element does not exist on the site."),
        ("Weak",        "2", "#e03131", "Exists but implemented very poorly — significant issues."),
        ("Medium",      "3", "#f08c00", "Functional but with significant room to improve."),
        ("High",        "4", "#2f9e44", "Mostly good — minor improvements possible."),
        ("Excellent",   "5", "#2f9e44", "Virtually no issues — best practice met."),
    ]
    scoring_html = "\n".join(
        f'<tr class="border-t border-surface-container-high">'
        f'<td class="py-3 pr-6 font-body font-semibold text-sm" style="color:{c};">{r}</td>'
        f'<td class="py-3 px-4 text-sm text-zinc-600">{v}</td>'
        f'<td class="py-3 px-4 text-sm text-zinc-600">{d}</td>'
        f'</tr>'
        for r, v, c, d in scoring_rows
    )

    priority_rows = [
        ("10 or under",  "HIGH",    "#e03131", "Act immediately — significant impact on search or AI visibility."),
        ("11–20",        "MEDIUM",  "#f08c00", "Address this quarter."),
        ("21–35",        "LOW",     "#2f9e44", "Monitor and improve when resources allow."),
        ("36–50",        "MONITOR", "#868e96", "No action needed — performing well."),
    ]
    priority_html = "\n".join(
        f'<tr class="border-t border-surface-container-high">'
        f'<td class="py-3 pr-6 text-sm font-mono text-zinc-600">{ps}</td>'
        f'<td class="py-3 px-4"><span class="px-2 py-1 rounded-full text-[10px] font-label font-bold uppercase text-white" style="background:{c};">{p}</span></td>'
        f'<td class="py-3 px-4 text-sm text-zinc-600">{d}</td>'
        f'</tr>'
        for ps, p, c, d in priority_rows
    )

    return f"""{head}
<body class="bg-surface-container-low font-body text-on-surface antialiased">
{nav}
<main class="pt-16">
  {crumb}

  <!-- Hero -->
  <section class="bg-white border-b-[3px] border-primary py-20 relative overflow-hidden">
    <div class="absolute right-0 top-0 w-[400px] h-[400px] bg-primary/5 blur-[100px] rounded-full pointer-events-none"></div>
    <div class="max-w-7xl mx-auto px-8 relative z-10">
      <div class="flex items-center gap-4 mb-5">
        <div class="w-10 h-[2px] bg-primary"></div>
        <span class="text-primary font-headline font-bold uppercase tracking-[0.2em] text-xs">Methodology</span>
      </div>
      <h1 class="text-5xl md:text-7xl font-headline font-extrabold tracking-tighter mb-6 leading-none text-on-surface">Methodology</h1>
      <p class="text-zinc-700 text-base leading-relaxed max-w-2xl">
        This audit covers 114 elements across 6 phases — Technical, User Experience, Tools &amp; Configuration, On-Site SEO, Off-Site, and GEO / AI Visibility. Each element is scored on a 5-point rating scale, weighted by business impact, and prioritised by a composite score formula.
      </p>
    </div>
  </section>

  <!-- Phase Overview -->
  <section class="py-16 px-8 max-w-7xl mx-auto">
    <div class="flex items-center mb-8">
      <div class="w-[3px] h-5 bg-primary mr-4 rounded-full"></div>
      <h2 class="text-tertiary font-headline text-lg font-bold tracking-tight">Audit Phases</h2>
    </div>
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {phases_html}
    </div>
  </section>

  <!-- Scoring Scale -->
  <section class="py-12 px-8 max-w-7xl mx-auto">
    <div class="bg-surface-container-lowest rounded-xl p-10 editorial-shadow">
      <div class="flex items-center mb-8">
        <div class="w-[3px] h-5 bg-primary mr-4 rounded-full"></div>
        <h2 class="text-tertiary font-headline text-lg font-bold tracking-tight">Rating Scale</h2>
      </div>
      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead>
            <tr>
              <th class="text-left py-3 pr-6 text-xs font-label font-extrabold uppercase tracking-widest text-zinc-400">Rating</th>
              <th class="text-left py-3 px-4 text-xs font-label font-extrabold uppercase tracking-widest text-zinc-400">Value</th>
              <th class="text-left py-3 px-4 text-xs font-label font-extrabold uppercase tracking-widest text-zinc-400">Definition</th>
            </tr>
          </thead>
          <tbody>{scoring_html}</tbody>
        </table>
      </div>
    </div>
  </section>

  <!-- Priority Formula -->
  <section class="py-12 px-8 max-w-7xl mx-auto pb-24">
    <div class="bg-surface-container-lowest rounded-xl p-10 editorial-shadow">
      <div class="flex items-center mb-4">
        <div class="w-[3px] h-5 bg-primary mr-4 rounded-full"></div>
        <h2 class="text-tertiary font-headline text-lg font-bold tracking-tight">Priority Formula</h2>
      </div>
      <p class="text-sm text-zinc-500 mb-8 leading-relaxed">
        Priority Score = Rating Value &times; Weight. Lower scores are more urgent. Weights range from 2.5 (Low) to 10 (Critical), reflecting the business impact of each element type.
      </p>
      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead>
            <tr>
              <th class="text-left py-3 pr-6 text-xs font-label font-extrabold uppercase tracking-widest text-zinc-400">Priority Score</th>
              <th class="text-left py-3 px-4 text-xs font-label font-extrabold uppercase tracking-widest text-zinc-400">Priority</th>
              <th class="text-left py-3 px-4 text-xs font-label font-extrabold uppercase tracking-widest text-zinc-400">Action</th>
            </tr>
          </thead>
          <tbody>{priority_html}</tbody>
        </table>
      </div>
    </div>
  </section>

</main>
{footer_html()}
</body>
</html>"""

# ============================================================
# DATA LOADING
# ============================================================

def load_workbook_data():
    """Loads and returns all rows from workbook_data.json."""
    json_path = Path(AUDIT_DIR) / "Workbook" / "workbook_data.json"
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("rows", [])

def load_schema_csv():
    """Loads schema CSV rows. Returns list of dicts."""
    csv_dir = Path(AUDIT_DIR) / "Outputs" / "CSV"
    pattern = str(csv_dir / "*Schema Markup Corrections*.csv")
    matches = glob.glob(pattern)
    if not matches:
        print("  [WARN] Schema CSV not found — schema.html will be minimal.")
        return []
    with open(matches[0], "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        return list(reader)

# ============================================================
# WRITE FILE
# ============================================================

def write_html(filename, content):
    """Writes HTML content to the HTML output directory."""
    html_dir = Path(AUDIT_DIR) / "HTML"
    html_dir.mkdir(exist_ok=True)
    out_path = html_dir / filename
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(content)
    size_kb = round(len(content) / 1024, 1)
    print(f"  ✓ {filename}  ({size_kb} KB)")

# ============================================================
# MAIN
# ============================================================

def main():
    print(f"\nGenerating HTML report for {CLIENT_NAME} — {AUDIT_DATE}")
    print(f"AUDIT_DIR: {AUDIT_DIR}\n")

    # Load data
    print("Loading workbook data...")
    rows = load_workbook_data()
    print(f"  {len(rows)} rows loaded.")

    print("Loading schema CSV...")
    schema_rows = load_schema_csv()
    print(f"  {len(schema_rows)} schema page templates loaded.")

    # Compute scores
    overall_score, phase_scores, priority_counts, phase_priority_counts = compute_scores(rows)
    if OVERALL_SCORE_OVERRIDE is not None:
        overall_score = OVERALL_SCORE_OVERRIDE
        print(f"\nOverall score: {overall_score}/100 (overridden from config)")
    else:
        print(f"\nOverall score: {overall_score}/100 (computed)")
    print("Phase scores:")
    for family, score in phase_scores.items():
        print(f"  {family}: {score}/100")
    print("Priority counts (overall):")
    for p, n in priority_counts.items():
        print(f"  {p}: {n}")

    # Copy logo files to HTML/ output directory
    html_dir = Path(AUDIT_DIR) / "HTML"
    html_dir.mkdir(exist_ok=True)
    if DIGITAD_LOGO_PATH and os.path.isfile(DIGITAD_LOGO_PATH):
        shutil.copy2(DIGITAD_LOGO_PATH, html_dir / "digitad-logo.png")
        print(f"  Logo: digitad-logo.png copied from {DIGITAD_LOGO_PATH}")
    elif DIGITAD_LOGO_PATH:
        print(f"  WARNING: Digitad logo not found at {DIGITAD_LOGO_PATH}")
    if CLIENT_LOGO_PATH and os.path.isfile(CLIENT_LOGO_PATH):
        shutil.copy2(CLIENT_LOGO_PATH, html_dir / f"{CLIENT_SLUG}-logo.png")
        print(f"  Logo: {CLIENT_SLUG}-logo.png copied from {CLIENT_LOGO_PATH}")
    elif CLIENT_LOGO_PATH:
        print(f"  WARNING: Client logo not found at {CLIENT_LOGO_PATH}")

    print("\nGenerating HTML files:")

    # 1. index.html
    write_html("index.html", generate_index(rows, overall_score, phase_scores, priority_counts))

    # 2–7. Section pages
    for family in PHASE_META:
        meta = PHASE_META[family]
        write_html(meta["file"], generate_section_page(family, rows))

    # 8. schema.html
    write_html("schema.html", generate_schema_page(schema_rows))

    # 9. methodology.html
    write_html("methodology.html", generate_methodology())

    print(f"\nDone. All 9 files written to {AUDIT_DIR}/HTML/")
    print("Open index.html in a browser to verify output matches yocrunch reference design.")

if __name__ == "__main__":
    main()
