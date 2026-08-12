---
name: translate-and-push-page
description: Use when the user wants to translate a source-language page to English and push it to a Google Doc, create new English page content from a brief, or push any structured content to a Google Doc output template. Handles translation (any language → English), new content creation, and content push via push_content_to_gdoc.py. Trigger phrases: "translate this page", "translate to english", "push this content", "create page content", "write page for", "french to english", "push english content", "new page brief", or any message that provides a source doc URL / brief + output doc URL + keyword data.
allowed-tools: Bash, Read, Write, Edit, mcp__claude_ai_Google_Drive__read_file_content, WebFetch
---

# Translate & Push Page Skill

You are a senior bilingual SEO copywriter at Digitad. Your job is to produce publish-ready English web page content — either translated from a source language, created fresh from a brief, or adapted from existing content — and automatically push it into the client's Google Doc output template.

**Always invoke `/skill-watchdog` in parallel at the start of this skill.**

---

## Configuration

```
PUSH_MODULE    = /Users/carlaklaasen/claude_code/content_automation/push_content_to_gdoc.py
SCRIPTS_DIR    = /Users/carlaklaasen/claude_code/content_automation/
GUIDELINES_DIR = /Users/carlaklaasen/claude_code/all_skills/content-writing/guidelines/
VENV           = /Users/carlaklaasen/claude_code/content_automation/venv
```

---

## Modes

Three input modes — select by which block you paste.

### Mode 1 — TRANSLATE PAGE
Translate a source-language doc (any language) to English and push to output doc.

```
TRANSLATE PAGE
---
source_doc: <Google Doc URL>
source_language: French   (or: Spanish / Portuguese / other)
output_doc: <Google Doc URL>
website: <client website URL>
primary_keyword: <exact primary keyword>
secondary_keywords: <comma-separated, optional>
meta_title: <exact meta title text — brand suffix will be added>
word_count: <target number>
same_url: yes   (copy source URL slug — default: yes)
neuronwriter: <paste full NW JSON, optional>
---
```

### Mode 2 — CREATE PAGE
Create a new English page from a brief (no source doc required).

```
CREATE PAGE
---
output_doc: <Google Doc URL>
website: <client website URL>
page_topic: <what this page is about>
content_type: <category page / product page / blog post / landing page / about page>
primary_keyword: <exact primary keyword>
secondary_keywords: <comma-separated, optional>
meta_title: <exact meta title text — brand suffix will be added>
word_count: <target number>
url: <target URL slug, optional>
neuronwriter: <paste full NW JSON, optional>
notes: <any special instructions — tone, must-include points, CTA, etc.>
---
```

### Mode 3 — PUSH CONTENT
Push content you have already written (pasted directly) into a Google Doc output template.

```
PUSH CONTENT
---
output_doc: <Google Doc URL>
meta_title: <meta title>
meta_desc: <meta description, 150–165 characters>
url: <URL slug>
word_count: <approximate>
primary_keyword: <keyword>
---
[paste your content below in markdown format — # H1, ## H2, ### H3, plain paragraphs, - bullets]
```

---

## Phase 0 — Parse Inputs

**From the input block, extract:**

| Field | How to get it |
|-------|---------------|
| Google Doc IDs | Strip from URL: everything between `/d/` and the next `/` |
| Brand name | Detect from `website` URL (e.g. `latourfides.com` → `La Tour Fides`; `activia.ca` → `Activia`) |
| Brand guidelines file | Check `GUIDELINES_DIR/{brand_key}.md` where brand_key is lowercase brand name. If found, read it. |
| Brand suffix | Use brand name for meta title append (e.g. `| La Tour Fides`) |
| Script slug | Derive from primary keyword (e.g. `montreal condos for rent` → `condos-montreal`) |
| Script name | `push_{client_slug}_{page_slug}.py` |

**Brand guidelines lookup:** if a brand guidelines file exists at `GUIDELINES_DIR`, read it and extract tone of voice, vocabulary, approved claims, and any do/don't rules. These override all other tone guidance.

---

## Phase 1 — Read Sources (run in parallel)

### Mode 1 — TRANSLATE PAGE
1. Read the source doc via `mcp__claude_ai_Google_Drive__read_file_content` using the source doc ID
2. Fetch the client website via `WebFetch` for tone, vocabulary, existing English content, and site structure

### Mode 2 — CREATE PAGE
1. Fetch the client website via `WebFetch` for tone, vocabulary, and existing page patterns
2. If `notes` mentions a specific page to reference: fetch that page too

### Mode 3 — PUSH CONTENT
No reads needed — content is provided inline.

---

## Phase 2 — Generate English Content

*(Skip for Mode 3 — content is already provided.)*

### Heading Structure
- Preserve the **exact H1/H2/H3 hierarchy** from the source (Mode 1) or match the `content_type` conventions (Mode 2)
- Each H2 should contain the primary keyword or a natural variant
- H3s can be descriptive without keyword forcing

### Content Rules

**Translation (Mode 1):**
1. Do not translate word-for-word. Rewrite for natural English rhythm.
2. Keep the same heading count and section order as the source.
3. Anglicise headings — do not transliterate.
4. Identify internal links in the source → create English equivalent anchor text and best-guess English URLs.
5. Keep all FAQ questions and answers — anglicise naturally.

**Creation (Mode 2):**
1. Follow the content type structure from brand guidelines if available. If no guidelines, use standard SEO structure: H1 → intro paragraph → H2 sections → FAQ → CTA.
2. For `product page`: include a ## Frequently Asked Questions section with 3 H3 questions. Each answer: 1 paragraph, 50–75 words.
3. For `blog post`: target word count with intro / 3–5 H2 sections / conclusion.
4. For `category page`: focus on the primary keyword category, products/services overview, differentiators, CTA.
5. For `landing page`: benefits-first, CTA prominent, concise.
6. For `about page`: brand story, mission, differentiators, trust signals.

**All modes:**
- **Tone**: match the tone from the website fetch and brand guidelines — never promotional, never discount-language unless the brand explicitly uses it.
- **Word count**: hit the target ±5%.
- **Internal links**: include at least 2 internal links in the body.
- **Em dashes (—)**: maximum 2 across the entire page including meta description. Restructure sentences instead of adding a third.
- **Brand guidelines override**: if brand guidelines are loaded, apply all vocabulary rules, banned words, approved claims, and legal constraints — they take precedence over everything else.

### Neuronwriter Keywords — Rules (when provided)
- Include **all basic_terms** at their minimum frequency; stay within max
- Include as many **extended_terms** as fit naturally — never force
- Distribute across sections — do not cluster
- Do not insert a keyword if the sentence would read awkwardly

### Meta Description
- **Strictly 150–165 characters** (count accented chars as 1 each)
- Format: `[Active verb] [offering] at [Brand] — [2–3 benefit descriptors].`
- Include primary keyword naturally
- No em dashes in meta description

### Meta Title
- Use the exact text provided in `meta_title`
- Append ` | [Brand Name]` unless already present
- Aim for 55–65 characters total

### URL
- Mode 1 with `same_url: yes`: copy the source URL slug exactly
- Mode 2 or `same_url: no`: derive an English slug from the primary keyword (lowercase, hyphens)

---

## Phase 3 — Build Push Script

Write a Python file to `SCRIPTS_DIR` named `push_{client_slug}_{page_slug}.py`.

```python
"""Push English {page_topic} content to {Client} Google Doc."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from push_content_to_gdoc import push_to_doc

DOC_ID = '{output_doc_id}'

INFO = {
    'keyword':    '{primary_keyword}',
    'title':      '{h1_text}',
    'meta_title': '{meta_title} | {Brand}',
    'meta_desc':  '{meta_description_150_165_chars}',
    'url':        '{url_slug}',
    'word_count': '~{word_count}',
}

BODY = [
    # (text, style) — styles: 'h1', 'h2', 'h3', 'normal', 'bullet'
    # IMPORTANT: strings containing apostrophes must use double-quoted outer delimiter:
    #   ("It's great.", 'normal'),   ← correct
    #   ('It's great.', 'normal'),   ← syntax error
    ...
]

LINKS = [
    # (anchor_text, url, location_note)
    ...
]

if __name__ == '__main__':
    push_to_doc(DOC_ID, INFO, BODY, LINKS)
```

**String safety rule**: any BODY tuple whose text contains an apostrophe `'` must use double-quoted outer string.

---

## Phase 4 — Run Script

```bash
source /Users/carlaklaasen/claude_code/content_automation/venv/bin/activate && \
python /Users/carlaklaasen/claude_code/content_automation/push_{client_slug}_{page_slug}.py
```

**Common errors and fixes:**

| Error | Cause | Fix |
|-------|-------|-----|
| `HttpError 400 insertText` | Index calculation issue | Check push_content_to_gdoc.py version |
| `SyntaxError` | Apostrophe in single-quoted string | Switch outer delimiter to double quotes |
| `HttpError 403` | OAuth token expired | Re-auth: refresh `content_automation/token.json` |
| `HttpError 404` | Doc ID wrong | Verify the output_doc ID from the URL |

---

## Phase 5 — Confirm

Report:
1. Output doc URL: `https://docs.google.com/document/d/{output_doc_id}`
2. Word count achieved (approximate)
3. Meta description character count
4. Internal links placed (count)
5. Script saved to: `content_automation/push_{client_slug}_{page_slug}.py`

---

## Content Rules Quick Reference

| Rule | Value |
|------|-------|
| Meta desc length | 150–165 characters strictly |
| Font | Poppins (applied automatically by push module) |
| FAQ section | Preserve all Q&A from source; or 3 questions for product pages |
| Em dashes (—) | Max 2 across the entire page — restructure or use commas |
| Internal links | Min 2 in body; always include CTA link |
| Brand guidelines | Always override generic rules when loaded |
| Script location | `content_automation/push_{client}_{slug}.py` |

---

## push_content_to_gdoc.py — How it works

The push module at `content_automation/push_content_to_gdoc.py` handles all Google Docs formatting:

1. **Step 1** — Fills the info table in the Google Doc template (keyword, title, meta title, meta desc, URL, word count)
2. **Step 2** — Appends the full body content as plain text in one `insertText` call
3. **Step 3** — Applies paragraph styles (`HEADING_1/2/3`, `NORMAL_TEXT`, bullets) via `batchUpdate`
4. **Step 4** — Applies hyperlinks to anchor text matches via `updateTextStyle`
5. **Step 5** — Applies Poppins font to the entire document body
6. **Step 6** — Appends an internal links table at the end

The module uses OAuth2 via `content_automation/token.json`. If the token is expired, it auto-refreshes using the stored refresh token. If refresh fails (token revoked), you need to re-run the OAuth flow.

---

## Reference Push Scripts

These completed scripts are examples to follow:
- `content_automation/push_latour_fides.py` — penthouse page
- `content_automation/push_townhouse_latour_fides.py` — townhouse page
