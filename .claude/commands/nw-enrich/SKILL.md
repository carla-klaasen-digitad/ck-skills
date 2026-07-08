---
name: nw-enrich
description: Use when the user wants to enrich a Google Doc with Neuronwriter keywords or entities — triggered by phrases like "enrich with NW", "NW enrichment", "add neuronwriter keywords", "I've pasted the NW keywords", "rewrite with neuronwriter", or any mention of enriching a doc using a Neuronwriter keyword/entity list. Loads brand guidelines, rewrites content to cover NW-recommended topics naturally, applies brand compliance and SEO rules, then strips the NW keyword section from the doc.
allowed-tools: Bash, Read, Write, Edit
---

# NW Enrich Skill

You are a senior SEO content strategist at Digitad. Your job is to enrich a Google Doc with Neuronwriter keyword/entity recommendations — rewriting the content to naturally cover recommended topics while maintaining brand voice, content structure, SEO best practices, and all legal/compliance constraints from the brand guidelines.

**Always invoke `/skill-watchdog nw-enrich` in parallel at the start of this skill.**

---

## Configuration

```
ENV_FILE       = /Users/carlaklaasen/claude_code/.env
GUIDELINES_DIR = /Users/carlaklaasen/claude_code/all_skills/content-writing/guidelines
SCRIPTS_DIR    = /Users/carlaklaasen/claude_code/.claude/commands/monthly-content-planner/scripts
TEMP_DIR       = /tmp/nw-enrich
MARKER         = --- NW ENRICH BELOW ---
```

Create TEMP_DIR if it doesn't exist:
```bash
mkdir -p /tmp/nw-enrich
```

---

## Invocation

```
/nw-enrich [doc_url_or_id]
```

Example:
```
/nw-enrich https://docs.google.com/document/d/1abc123.../edit
```

Extract doc ID from URL:
```python
import re
match = re.search(r'/document/d/([^/]+)', doc_url)
doc_id = match.group(1) if match else doc_url.strip()
```

---

## Phase 0 — Pre-flight

1. Confirm `doc_url_or_id` was provided. If not: output usage instructions and exit.
2. Extract `doc_id` from URL if a full URL was given.
3. Verify `.env` is readable and `ANTHROPIC_API_KEY` is set.
4. Confirm `GUIDELINES_DIR` exists.

---

## Phase 1 — Read Google Doc

Use the gdocs_helper script to read the full doc content as plain text:

```bash
python3 SCRIPTS_DIR/gdocs_helper.py read_doc \
  --doc-id "{doc_id}" \
  > /tmp/nw-enrich/doc_raw.txt
```

If the read fails or the file is empty: log `[CRITICAL] Could not read doc {doc_id} — check permissions` and exit.

---

## Phase 2 — Detect Brand and Split Content

### 2.1 — Detect brand from doc title

The doc title follows the naming convention: `BRAND - YYYY-MM - Topic`
Examples: `SILK - 2026-06 - Oat Milk Barista`, `OIKOS - 2026-06 - High Protein Snacks`

```bash
python3 SCRIPTS_DIR/gdocs_helper.py get_doc_title \
  --doc-id "{doc_id}"
```

Parse the brand from the title (first segment before ` - `). Normalise to lowercase for the guidelines filename lookup.

**Brand → guidelines file mapping:**

| Doc title prefix | Guidelines file |
|---|---|
| ACTIVIA | activia.md |
| DANIMALS | danimals.md |
| DANNON | dannon.md |
| DANONE AWAY FROM HOME / DAFH | danoneawayfromhome.md |
| DUNKIN CREAMERS / DUNKIN | dunkincreamers.md |
| EVIAN | evian.md |
| FOLLOW YOUR HEART / FYH | followyourheart.md |
| HAPPY FAMILY | happyfamily.md |
| INTERNATIONAL DELIGHT / ID | internationaldelight.md |
| LIGHT & FIT / LIGHT+FIT | lightandfit.md |
| MITACS | mitacs.md |
| OIKOS | oikos.md |
| REMIX YOGURT / REMIX | remixyogurt.md |
| SILK | silk.md |
| SO DELICIOUS | sodelicious.md |
| STOK | stok.md |
| TOO GOOD / TWO GOOD | toogood.md |
| YOCRUNCH / YO CRUNCH | yocrunch.md |

If the brand cannot be determined: ask the user to confirm which brand this doc belongs to before proceeding.

### 2.2 — Load brand guidelines

```python
brand_guidelines = open(f"{GUIDELINES_DIR}/{brand_file}").read()
```

If the file does not exist: log `[FLAG] Brand guidelines file not found for detected brand {brand_name}. Proceeding without brand context — review output carefully.`

### 2.3 — Split doc at the marker

```python
content = open("/tmp/nw-enrich/doc_raw.txt").read()
MARKER = "--- NW ENRICH BELOW ---"

if MARKER not in content:
    raise SystemExit("[ERROR] Marker '--- NW ENRICH BELOW ---' not found in doc. "
                     "Paste the NW keyword list at the bottom of the doc above this marker, then re-run.")

parts = content.split(MARKER, 1)
original_content = parts[0].rstrip()
nw_keywords_raw   = parts[1].strip()
```

Write to temp files:
```bash
# written via Python to avoid shell escaping issues
python3 -c "
content = open('/tmp/nw-enrich/doc_raw.txt').read()
marker = '--- NW ENRICH BELOW ---'
parts = content.split(marker, 1)
open('/tmp/nw-enrich/original_content.txt', 'w').write(parts[0].rstrip())
open('/tmp/nw-enrich/nw_keywords.txt', 'w').write(parts[1].strip() if len(parts) > 1 else '')
"
```

Log: `[INFO] Original content: {N} chars | NW keyword section: {M} chars`

If `nw_keywords_raw` is empty: log `[WARN] Marker found but no keywords below it. Nothing to enrich.` and exit.

---

## Phase 3 — Build Enrichment Prompt

Write the prompt to `/tmp/nw-enrich/enrich_prompt.txt`:

```
You are a senior SEO content writer at Digitad. Your task is to enrich an existing piece of on-site content for {brand_name} using Neuronwriter keyword/entity recommendations.

=== BRAND GUIDELINES ===
{brand_guidelines}

=== TASK ===
The content below has already been written and approved for structure. Your job is to:

1. READ the NW keyword/entity list and identify which concepts, topics, or terms are MISSING or UNDERDEVELOPED in the existing content.
2. REWRITE the content to naturally cover those gaps — weaving missing concepts into existing sentences or adding brief, relevant passages where appropriate.
3. NEVER stuff keywords. If a term does not fit naturally into the context of the page, skip it. Coverage through concept > coverage through exact phrase.
4. NEVER introduce competitor brand names, even if they appear in the NW list.
5. MAINTAIN the existing content structure exactly: same heading hierarchy (H1, H2, H3), same section order, same FAQ questions (only rewrite the answers if coverage warrants it).
6. APPLY all brand compliance rules from the Brand Guidelines above: banned words, required disclaimers, vocabulary restrictions, tone, and legal constraints. These override everything else.
7. APPLY SEO best practices:
   - Primary keyword appears in the H1, first paragraph, at least one H2, and the meta description (if present)
   - Secondary/NW keywords distributed naturally across H2s, body copy, and FAQ answers
   - No keyword repetition within 100 words of itself
   - Heading hierarchy must be logical and unbroken (no jumping H1 → H3)
   - Internal link anchors must use natural language, never exact-match keyword strings
8. OUTPUT the full rewritten content — not a diff, not a summary. The complete page, ready to replace the original.
9. Do NOT include any annotation, commentary, or explanation in the output. Pure publishable content only.
10. Em dashes (—): maximum 2 per page total. Never in bullet lists.
11. If the page includes a meta title and meta description at the top, rewrite them to reflect any new NW coverage.

=== NEURONWRITER KEYWORDS / ENTITIES TO INCORPORATE ===
{nw_keywords_raw}

=== ORIGINAL CONTENT TO ENRICH ===
{original_content}
```

---

## Phase 4 — Generate Enriched Content

```bash
python3 -c "
import anthropic, sys, os
client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY', ''))
prompt = open('/tmp/nw-enrich/enrich_prompt.txt').read()
msg = client.messages.create(
    model='claude-opus-4-8',
    max_tokens=8000,
    messages=[{'role': 'user', 'content': prompt}]
)
print(msg.content[0].text)
" > /tmp/nw-enrich/enriched_content.txt
```

If the API call fails: log `[WARN] Content generation failed — doc not modified.` and exit without touching the doc.

---

## Phase 5 — Write Enriched Content Back to Doc

Replace the entire doc content (everything above the marker AND the marker section) with the enriched content:

```bash
python3 SCRIPTS_DIR/gdocs_helper.py replace_doc_content \
  --doc-id "{doc_id}" \
  --content-file "/tmp/nw-enrich/enriched_content.txt"
```

This replaces the full doc body. The NW keyword section and marker are gone. The enriched content is the complete document.

If the write fails: log `[CRITICAL] Failed to write enriched content back to doc. The original is unchanged. Enriched content saved locally at /tmp/nw-enrich/enriched_content.txt` — do not retry automatically.

---

## Phase 6 — Coverage Summary

After the doc is updated, output a short summary to chat:

```
NW Enrich — {brand_name} — {doc_title}
Doc updated:     YES
Brand context:   {brand_file} loaded
Model used:      claude-opus-4-8

NW keyword coverage (estimated):
  Incorporated: [list key topics/entities woven in]
  Skipped:      [list terms skipped and why — e.g. "competitor name", "did not fit context", "already well-covered"]

Compliance checks applied:
  [list any brand-specific rules enforced — e.g. "0g added sugar (not 'zero sugar')", "no 'healthy' claim", "probiotic strain name included"]

Review the doc before publishing:
  {doc_url}
```

---

## Error Handling

| Scenario | Action |
|---|---|
| No doc URL provided | Print usage and exit |
| Doc not readable | Log CRITICAL, exit |
| Marker not found in doc | Explain expected format, exit without modifying |
| Brand not detected from title | Ask user to confirm brand, then continue |
| Brand guidelines file missing | Proceed with SEO-only enrichment, flag to user |
| NW keyword section empty | Log WARN, exit without modifying |
| Claude API call fails | Log WARN, exit without modifying doc |
| Doc write-back fails | Log CRITICAL, save enriched content locally, do not retry |

---

## Notes for the Writer

- This skill modifies the doc in place. The original content is not versioned — if you need to compare, duplicate the doc before running.
- NW score must still be checked manually: open the NW analysis, paste the enriched content, record the score.
- If the NW keyword list included competitor names, check the Skipped section in the summary to confirm they were not incorporated.
- Legal/compliance rules from the brand guidelines always take precedence over NW keyword coverage.
