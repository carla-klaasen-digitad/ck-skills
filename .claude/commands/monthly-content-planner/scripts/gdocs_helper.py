#!/usr/bin/env python3
"""
Google Drive + Docs helper for monthly-content-planner.

Commands:
  ensure_folder --parent-id ID --name "FOLDER NAME"
  copy_template --template-id ID --dest-folder-id ID --title "DOC TITLE"
  populate_brief --doc-id ID --keyword KW --secondary SEC --heading H1
                 --url URL --nw-link NW_URL --brand BRAND_KEY
  scrape_url --url URL
  append_content --doc-id ID --type TYPE
                 --original-file PATH --optimised-file PATH
                 [--heading HEADING]
"""

import sys, os, json, re, argparse, warnings
warnings.filterwarnings("ignore")

from dotenv import load_dotenv
load_dotenv("/Users/carlaklaasen/claude_code/.env")

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

SCOPES = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/documents",
]


def get_creds():
    creds = Credentials(
        token=None,
        refresh_token=os.getenv("GOOGLE_REFRESH_TOKEN", ""),
        token_uri=os.getenv("GOOGLE_TOKEN_URI", "https://oauth2.googleapis.com/token"),
        client_id=os.getenv("GOOGLE_CLIENT_ID", ""),
        client_secret=os.getenv("GOOGLE_CLIENT_SECRET", ""),
        scopes=SCOPES,
    )
    creds.refresh(Request())
    return creds


def drive_service():
    return build("drive", "v3", credentials=get_creds())


def docs_service():
    return build("docs", "v1", credentials=get_creds())


# ─── ensure_folder ─────────────────────────────────────────────────────────────
def ensure_folder(parent_id, folder_name):
    drive = drive_service()

    q = (
        f"mimeType='application/vnd.google-apps.folder' "
        f"and name='{folder_name.replace(chr(39), chr(92)+chr(39))}' "
        f"and '{parent_id}' in parents "
        f"and trashed=false"
    )
    results = drive.files().list(q=q, fields="files(id,name)").execute()
    files = results.get("files", [])

    if files:
        print(json.dumps({"folder_id": files[0]["id"], "created": False, "name": folder_name}))
        return

    meta = {
        "name": folder_name,
        "mimeType": "application/vnd.google-apps.folder",
        "parents": [parent_id],
    }
    folder = drive.files().create(body=meta, fields="id").execute()
    print(json.dumps({"folder_id": folder["id"], "created": True, "name": folder_name}))


# ─── copy_template ─────────────────────────────────────────────────────────────
def copy_template(template_id, dest_folder_id, title):
    drive = drive_service()

    copy_meta = {"name": title, "parents": [dest_folder_id]}
    new_file = drive.files().copy(
        fileId=template_id,
        body=copy_meta,
        fields="id,webViewLink"
    ).execute()

    doc_id = new_file["id"]
    doc_url = new_file.get("webViewLink", f"https://docs.google.com/document/d/{doc_id}/edit")
    print(json.dumps({"doc_id": doc_id, "doc_url": doc_url, "title": title}))


# ─── populate_brief ────────────────────────────────────────────────────────────
def populate_brief(doc_id, keyword, secondary, heading, url, nw_link, brand, search_demand=""):
    """
    Fill in the Editorial Information table in the copied template.
    Uses replaceAllText for {{PLACEHOLDER}} templates, falls back to cell targeting.

    Table row mapping:
      Keyword row           → keyword
      Secondary Keyword     → secondary
      Meta Title row        → heading  (heading value = default meta title)
      Search Demand / Volume → search_demand
      URL row               → url
      NW Brief/Link         → nw_link
    """
    docs = docs_service()

    requests = [
        _replace_req("{{KEYWORD}}", keyword),
        _replace_req("{{SECONDARY_KEYWORD}}", secondary),
        _replace_req("{{TITLE}}", heading),
        _replace_req("{{META_TITLE}}", heading),
        _replace_req("{{SEARCH_DEMAND}}", search_demand),
        _replace_req("{{SEARCH_VOLUME}}", search_demand),
        _replace_req("{{MONTHLY_SEARCH_VOLUME}}", search_demand),
        _replace_req("{{URL}}", url),
        _replace_req("{{NW_LINK}}", nw_link),
        _replace_req("{{NEURONWRITER_LINK}}", nw_link),
        _replace_req("{{NEURONWRITER_BRIEF}}", nw_link),
    ]

    try:
        resp = docs.documents().batchUpdate(
            documentId=doc_id,
            body={"requests": requests}
        ).execute()
        total_replaced = sum(
            r.get("replaceAllTextResponse", {}).get("occurrencesChanged", 0)
            for r in resp.get("replies", [])
        )
        if total_replaced > 0:
            print(json.dumps({"ok": True, "method": "replaceAllText", "replacements": total_replaced, "doc_id": doc_id}))
            return
    except HttpError:
        pass

    doc = docs.documents().get(documentId=doc_id).execute()
    body_content = doc.get("body", {}).get("content", [])

    # Row label → value mapping
    fill_rules = [
        (lambda l: "secondary keyword" in l or ("secondary" in l and "keyword" in l), secondary),
        (lambda l: "keyword" in l and "secondary" not in l and "meta" not in l and "url" not in l, keyword),
        (lambda l: "meta" in l and "title" in l, heading),          # Meta Title → heading
        (lambda l: l.strip().startswith("title") and "meta" not in l, heading),  # fallback plain Title
        (lambda l: any(p in l for p in ("search demand", "search volume", "monthly search", "monthly volume")), search_demand),
        (lambda l: "url" in l and "neuronwriter" not in l and "nw" not in l, url),
    ]

    inserts = []

    for elem in body_content:
        if "table" not in elem:
            continue
        for row in elem["table"].get("tableRows", []):
            cells = row.get("tableCells", [])
            if len(cells) < 2:
                continue
            label_text = _cell_text(cells[0]).lower().strip()
            value_cell  = cells[1]

            for predicate, val in fill_rules:
                if predicate(label_text) and val:
                    for cell_elem in value_cell.get("content", []):
                        para = cell_elem.get("paragraph", {})
                        for pe in para.get("elements", []):
                            idx = pe.get("startIndex")
                            if idx is not None:
                                inserts.append((idx, val))
                                break
                        else:
                            continue
                        break
                    break

    if nw_link:
        for elem in body_content:
            for paragraph in _walk_paragraphs(elem):
                para_text = _para_text(paragraph).lower()
                if "neuronwriter" in para_text and "brief" in para_text:
                    end = paragraph.get("endIndex", 0)
                    if end > 1:
                        inserts.append((end - 1, " " + nw_link))
                    break

    if inserts:
        inserts.sort(key=lambda x: x[0], reverse=True)
        batch = [_insert_text_req(idx, text) for idx, text in inserts]
        try:
            docs.documents().batchUpdate(
                documentId=doc_id, body={"requests": batch}
            ).execute()
        except Exception as e:
            print(json.dumps({"ok": False, "error": str(e), "doc_id": doc_id}), file=sys.stderr)
            sys.exit(1)

    print(json.dumps({"ok": True, "method": "cell_targeting", "fields_written": len(inserts), "doc_id": doc_id}))


# ─── scrape_url ────────────────────────────────────────────────────────────────
def scrape_url(url):
    """Scrape on-page body content from a URL, stripping nav/header/footer."""
    import urllib.request
    try:
        from bs4 import BeautifulSoup, Comment
        _bs4_available = True
    except ImportError:
        _bs4_available = False

    JUNK_TAGS = ["script", "style", "noscript", "nav", "footer", "header",
                 "aside", "form", "iframe", "svg", "button", "picture"]
    # Class/id patterns that indicate site chrome, not page content
    JUNK_CLASS = re.compile(
        r'(?:^|\s)(?:nav(?:igation)?|menu|header|footer|sidebar|breadcrumb|'
        r'cookie|popup|modal|overlay|banner|promo|social|share|related|'
        r'widget|advertisement|subnav|utility|site-header|site-footer|'
        r'skip-link|back-to-top)(?:\s|$)',
        re.IGNORECASE
    )

    def _is_junk(tag):
        classes = " ".join(tag.get("class", []))
        tag_id = tag.get("id", "")
        return bool(JUNK_CLASS.search(classes) or JUNK_CLASS.search(tag_id))

    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=20) as resp:
            raw_html = resp.read().decode("utf-8", errors="replace")

        if _bs4_available:
            soup = BeautifulSoup(raw_html, "html.parser")

            # Remove HTML comments
            for c in soup.find_all(string=lambda t: isinstance(t, Comment)):
                c.extract()

            # Remove known junk tags outright
            for tag_name in JUNK_TAGS:
                for t in soup.find_all(tag_name):
                    t.decompose()

            # Remove elements whose class/id indicate site chrome
            # Collect first, then decompose (safe modification pattern)
            junk_els = [t for t in soup.find_all(True)
                        if t.parent is not None and _is_junk(t)]
            for t in junk_els:
                if t.parent is not None:
                    t.decompose()

            # Pick the most relevant content container
            content_el = (
                soup.find("main") or
                soup.find("article") or
                soup.find(attrs={"id": re.compile(r'^(?:content|main|page-content|primary)$', re.I)}) or
                soup.find(attrs={"class": re.compile(r'\b(?:page-content|post-content|entry-content|product-content)\b', re.I)}) or
                soup.body or
                soup
            )

            # Use get_text with a newline separator, then clean up
            raw_text = content_el.get_text(separator="\n")
        else:
            # Fallback: strip tags manually
            raw_text = re.sub(r'<[^>]+>', ' ', raw_html)

        # Post-process: normalize whitespace, remove duplicates, filter nav noise
        lines = raw_text.split("\n")
        seen = set()
        clean = []
        for line in lines:
            line = line.strip()
            if not line:
                if clean and clean[-1] != "":
                    clean.append("")
                continue
            # Skip exact-duplicate lines
            if line in seen:
                continue
            # Skip lines that look like nav labels: ≤4 words, no sentence-ending punctuation,
            # no digits (product specs kept), length ≤ 40 chars
            words = line.split()
            if (len(words) <= 4
                    and not any(c in line for c in ".!?,;:")
                    and not re.search(r'\d', line)
                    and len(line) <= 40):
                seen.add(line)
                continue
            seen.add(line)
            clean.append(line)

        text = "\n".join(clean).strip()
        text = re.sub(r"\n{3,}", "\n\n", text)
        print(json.dumps({"ok": True, "url": url, "text": text, "chars": len(text)}))

    except Exception as e:
        print(json.dumps({"ok": False, "url": url, "error": str(e), "text": ""}))


# ─── Markdown → Google Docs formatting helpers ────────────────────────────────

def _parse_inline_formatting(text, apply_underlines=True):
    """
    Strip [U]...[/U], **bold**, ***bold+italic***, *italic*, _italic_ from text.
    Returns (plain_text, [(start_offset, end_offset, format_type), ...])
    """
    pattern = re.compile(
        r'\[U\](.*?)\[/U\]'       # [U] underline
        r'|\*\*\*(.*?)\*\*\*'     # ***bold+italic***
        r'|\*\*(.*?)\*\*'         # **bold**
        r'|\*(.*?)\*'             # *italic*
        r'|_(.*?)_',              # _italic_
        re.DOTALL
    )

    result_parts = []
    ranges = []
    pos = 0
    last_end = 0

    for m in pattern.finditer(text):
        before = text[last_end:m.start()]
        result_parts.append(before)
        pos += len(before)
        start = pos

        if m.group(1) is not None:       # [U]...[/U]
            inner = m.group(1)
            result_parts.append(inner)
            pos += len(inner)
            if apply_underlines and inner:
                ranges.append((start, pos, "underline"))
        elif m.group(2) is not None:     # ***bold+italic***
            inner = m.group(2)
            result_parts.append(inner)
            pos += len(inner)
            if inner:
                ranges.append((start, pos, "bold"))
                ranges.append((start, pos, "italic"))
        elif m.group(3) is not None:     # **bold**
            inner = m.group(3)
            result_parts.append(inner)
            pos += len(inner)
            if inner:
                ranges.append((start, pos, "bold"))
        elif m.group(4) is not None:     # *italic*
            inner = m.group(4)
            result_parts.append(inner)
            pos += len(inner)
            if inner:
                ranges.append((start, pos, "italic"))
        elif m.group(5) is not None:     # _italic_
            inner = m.group(5)
            result_parts.append(inner)
            pos += len(inner)
            if inner:
                ranges.append((start, pos, "italic"))

        last_end = m.end()

    result_parts.append(text[last_end:])
    return "".join(result_parts), ranges


def _inline_style_req(start, end, fmt):
    """Build an updateTextStyle request for bold/italic/underline."""
    if start >= end:
        return None
    style_field = {"bold": "bold", "italic": "italic", "underline": "underline"}.get(fmt)
    if not style_field:
        return None
    return {
        "updateTextStyle": {
            "range": {"startIndex": start, "endIndex": end},
            "textStyle": {style_field: True},
            "fields": style_field,
        }
    }


def _build_section_heading(title, cursor):
    """Insert a HEADING_1 label (ORIGINAL / OPTIMISED). Returns (requests, new_cursor)."""
    text = title + "\n"
    reqs = [
        {"insertText": {"location": {"index": cursor}, "text": text}},
        {
            "updateParagraphStyle": {
                "range": {"startIndex": cursor, "endIndex": cursor + len(text)},
                "paragraphStyle": {"namedStyleType": "HEADING_1"},
                "fields": "namedStyleType",
            }
        },
    ]
    return reqs, cursor + len(text)


def _build_plain_paragraphs(text, cursor):
    """
    Insert scraped original text as NORMAL_TEXT paragraphs (no markdown parsing).
    Returns (requests, new_cursor).
    """
    requests = []
    paragraphs = re.split(r'\n{2,}', text.strip())
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        insert_text = para + "\n"
        requests.append({"insertText": {"location": {"index": cursor}, "text": insert_text}})
        cursor += len(insert_text)
    # Trailing blank line after section
    requests.append({"insertText": {"location": {"index": cursor}, "text": "\n"}})
    cursor += 1
    return requests, cursor


def _build_markdown_requests(text, cursor, apply_underlines=True):
    """
    Parse markdown text into Google Docs API requests with proper formatting.

    Supported:
      # / ## / ### / #### headings      → HEADING_1 … HEADING_4
      - item / * item                   → bullet list
      **bold**, ***bold+italic***        → bold / bold+italic
      *italic*, _italic_                → italic
      [U]...[/U]                        → underline (only when apply_underlines=True)

    Returns (requests, new_cursor).
    """
    requests = []
    lines = text.split("\n")
    pending_bullets = []  # consecutive bullet lines not yet flushed

    def flush_bullets():
        nonlocal cursor
        if not pending_bullets:
            return
        bullet_start = cursor
        for bline in pending_bullets:
            plain, iranges = _parse_inline_formatting(bline, apply_underlines)
            itext = plain + "\n"
            requests.append({"insertText": {"location": {"index": cursor}, "text": itext}})
            for (s, e, t) in iranges:
                req = _inline_style_req(cursor + s, cursor + e, t)
                if req:
                    requests.append(req)
            cursor += len(itext)
        bullet_end = cursor
        if bullet_end > bullet_start:
            requests.append({
                "createParagraphBullets": {
                    "range": {"startIndex": bullet_start, "endIndex": bullet_end},
                    "bulletPreset": "BULLET_DISC_CIRCLE_SQUARE",
                }
            })
        pending_bullets.clear()

    HEADING_STYLES = {
        1: "HEADING_1", 2: "HEADING_2", 3: "HEADING_3",
        4: "HEADING_4", 5: "HEADING_5", 6: "HEADING_6",
    }

    for line in lines:
        stripped = line.strip()

        # Empty line
        if not stripped:
            flush_bullets()
            requests.append({"insertText": {"location": {"index": cursor}, "text": "\n"}})
            cursor += 1
            continue

        # Bullet line: -, *, •, or numbered (1. 2. etc.)
        bullet_m = re.match(r'^[-*•]\s+(.*)', line) or re.match(r'^\d+\.\s+(.*)', line)
        if bullet_m:
            pending_bullets.append(bullet_m.group(1))
            continue

        # Non-bullet — flush any pending bullets first
        flush_bullets()

        # Heading detection — two patterns:
        #   Pattern A: [U]## Heading text[/U]  → whole new heading wrapped in [U]
        #   Pattern B: ## Heading text          → normal heading (may have inline [U] markers)
        h_level, raw_heading, heading_is_new = None, None, False

        pa = re.match(r'^\[U\](#{1,6})\s+(.*?)\[/U\]$', stripped)
        if pa:
            h_level = min(len(pa.group(1)), 6)
            raw_heading = pa.group(2).strip()
            heading_is_new = True
        else:
            pb = re.match(r'^(#{1,6})\s+(.*)', stripped)
            if pb:
                h_level = min(len(pb.group(1)), 6)
                raw_heading = pb.group(2).strip()

        if h_level is not None:
            plain, iranges = _parse_inline_formatting(raw_heading, apply_underlines)
            itext = plain + "\n"
            requests.append({"insertText": {"location": {"index": cursor}, "text": itext}})
            requests.append({
                "updateParagraphStyle": {
                    "range": {"startIndex": cursor, "endIndex": cursor + len(itext)},
                    "paragraphStyle": {"namedStyleType": HEADING_STYLES[h_level]},
                    "fields": "namedStyleType",
                }
            })
            # Apply underline across the full heading if it was [U]-wrapped as a whole
            if apply_underlines and heading_is_new:
                req = _inline_style_req(cursor, cursor + len(itext) - 1, "underline")
                if req:
                    requests.append(req)
            for (s, e, t) in iranges:
                req = _inline_style_req(cursor + s, cursor + e, t)
                if req:
                    requests.append(req)
            cursor += len(itext)
            continue

        # Horizontal rule (--- or ***)
        if re.match(r'^[-*_]{3,}$', stripped):
            flush_bullets()
            requests.append({"insertText": {"location": {"index": cursor}, "text": "\n"}})
            cursor += 1
            continue

        # Normal paragraph
        plain, iranges = _parse_inline_formatting(line, apply_underlines)
        itext = plain + "\n"
        requests.append({"insertText": {"location": {"index": cursor}, "text": itext}})
        for (s, e, t) in iranges:
            req = _inline_style_req(cursor + s, cursor + e, t)
            if req:
                requests.append(req)
        cursor += len(itext)

    flush_bullets()
    return requests, cursor


# ─── _strip_internal_links ─────────────────────────────────────────────────────

def _strip_internal_links(text):
    """
    Strip internal link lists and navigation sections from generated content.

    Removes:
      - Sections with headings like "Internal Links", "Related Articles", etc.
      - "SHOP NOW" standalone lines (product carousel CTAs)
      - "WHERE TO BUY" / "FIND US" navigation lines
      - Any markdown link-list block (lines of the form [text](url) with 3+ consecutive)
    """
    # Strip sections headed by internal-link / related-content headings
    text = re.sub(
        r'(?m)^#{1,4}\s*(?:internal links?|related (?:articles?|content|links?|pages?)|'
        r'you may also like|see also|navigation|further reading)\s*\n'
        r'(?:.*\n)*?(?=\n#{1,4}\s|\Z)',
        '',
        text,
        flags=re.IGNORECASE,
    )

    # Remove standalone CTA / nav lines
    cta_pattern = re.compile(
        r'^\s*(?:shop now|where to buy|find us(?: near you)?|buy now|'
        r'learn more|find (?:a store|stores?|us)|get it now|order now)\s*$',
        re.IGNORECASE | re.MULTILINE,
    )
    text = cta_pattern.sub('', text)

    # Remove lines that are purely a markdown link: [anchor](url)
    text = re.sub(r'^\s*\[.+?\]\(https?://[^\)]+\)\s*$', '', text, flags=re.MULTILINE)

    # Collapse runs of 3+ blank lines to 2
    text = re.sub(r'\n{3,}', '\n\n', text)

    return text.strip()


# ─── clear_content_sections ────────────────────────────────────────────────────

def clear_content_sections(doc_id):
    """
    Delete everything from the first ORIGINAL/OPTIMISED HEADING_1 to the end of
    the document. Used before re-appending corrected content.

    Returns {"ok": True, "deleted_chars": N} or {"ok": False, "reason": "..."}.
    """
    docs = docs_service()
    doc = docs.documents().get(documentId=doc_id).execute()
    body_content = doc.get("body", {}).get("content", [])

    cut_start = None
    doc_end = None

    for elem in body_content:
        para = elem.get("paragraph", {})
        style = para.get("paragraphStyle", {}).get("namedStyleType", "")
        if style == "HEADING_1":
            raw = "".join(
                e.get("textRun", {}).get("content", "")
                for e in para.get("elements", [])
            ).strip().upper()
            if raw in ("ORIGINAL", "OPTIMISED") and cut_start is None:
                cut_start = elem.get("startIndex")
        doc_end = elem.get("endIndex")

    if cut_start is None:
        print(json.dumps({"ok": False, "reason": "no ORIGINAL/OPTIMISED heading found", "doc_id": doc_id}))
        return

    # Delete from cut_start to doc_end-1 (keep the mandatory trailing \n)
    delete_end = doc_end - 1
    if delete_end <= cut_start:
        print(json.dumps({"ok": False, "reason": "nothing to delete", "doc_id": doc_id}))
        return

    try:
        docs.documents().batchUpdate(
            documentId=doc_id,
            body={"requests": [{
                "deleteContentRange": {
                    "range": {"startIndex": cut_start, "endIndex": delete_end}
                }
            }]}
        ).execute()
        print(json.dumps({"ok": True, "doc_id": doc_id, "deleted_from": cut_start, "deleted_to": delete_end}))
    except Exception as e:
        print(json.dumps({"ok": False, "error": str(e), "doc_id": doc_id}), file=sys.stderr)
        sys.exit(1)


# ─── append_content ────────────────────────────────────────────────────────────
def append_content(doc_id, content_type, original_file, optimised_file, heading=""):
    """
    Appends content to a Google Doc with proper formatting:
      ORIGINAL section  — scraped text as plain paragraphs (no markdown)
      OPTIMISED section — Claude-generated markdown formatted into Docs styles

    [U]...[/U] markers → underline (applied only for Optimization workflows)
    **bold** → bold, ## heading → HEADING_2, - bullet → bullet list, etc.
    Internal link lists and SHOP NOW CTAs are stripped automatically.
    """
    docs = docs_service()

    original_text = ""
    if original_file and os.path.exists(original_file):
        with open(original_file, encoding="utf-8") as f:
            original_text = f.read().strip()

    optimised_text = ""
    if optimised_file and os.path.exists(optimised_file):
        with open(optimised_file, encoding="utf-8") as f:
            optimised_text = f.read().strip()

    if not optimised_text:
        print(json.dumps({"ok": False, "error": "optimised_file empty or missing", "doc_id": doc_id}))
        sys.exit(1)

    # Strip internal link sections and navigation CTAs
    optimised_text = _strip_internal_links(optimised_text)

    is_pure_creation = (
        bool(re.search(r"creation|nouveau|new", content_type, re.IGNORECASE)) and
        not bool(re.search(r"optimization|optimisation", content_type, re.IGNORECASE))
    )
    apply_underlines = not is_pure_creation

    # Get current doc end index
    doc = docs.documents().get(documentId=doc_id).execute()
    body_content = doc.get("body", {}).get("content", [])
    end_index = body_content[-1].get("endIndex", 1) if body_content else 1
    cursor = end_index - 1

    batch_requests = []

    # Separator before first section
    batch_requests.append({"insertText": {"location": {"index": cursor}, "text": "\n"}})
    cursor += 1

    # ORIGINAL section
    if original_text:
        h_reqs, cursor = _build_section_heading("ORIGINAL", cursor)
        batch_requests.extend(h_reqs)
        p_reqs, cursor = _build_plain_paragraphs(original_text, cursor)
        batch_requests.extend(p_reqs)

    # OPTIMISED section
    h_reqs, cursor = _build_section_heading("OPTIMISED", cursor)
    batch_requests.extend(h_reqs)
    c_reqs, cursor = _build_markdown_requests(optimised_text, cursor, apply_underlines)
    batch_requests.extend(c_reqs)

    # Submit — split into chunks of 500 requests to stay within API limits
    chunk_size = 500
    for i in range(0, len(batch_requests), chunk_size):
        chunk = batch_requests[i:i + chunk_size]
        try:
            docs.documents().batchUpdate(
                documentId=doc_id,
                body={"requests": chunk}
            ).execute()
        except Exception as e:
            print(json.dumps({"ok": False, "error": str(e), "doc_id": doc_id}), file=sys.stderr)
            sys.exit(1)

    print(json.dumps({
        "ok": True,
        "doc_id": doc_id,
        "has_original": bool(original_text),
        "underlines": apply_underlines,
        "requests_sent": len(batch_requests),
    }))


# ─── Doc traversal helpers ─────────────────────────────────────────────────────

def _replace_req(find, replace):
    return {
        "replaceAllText": {
            "containsText": {"text": find, "matchCase": True},
            "replaceText": replace,
        }
    }

def _insert_text_req(index, text):
    return {"insertText": {"location": {"index": index}, "text": text}}

def _cell_text(cell):
    texts = []
    for elem in cell.get("content", []):
        for pe in elem.get("paragraph", {}).get("elements", []):
            texts.append(pe.get("textRun", {}).get("content", ""))
    return "".join(texts)

def _cell_end_index(cell):
    content = cell.get("content", [])
    if not content:
        return None
    last = content[-1]
    para = last.get("paragraph", {})
    elems = para.get("elements", [])
    if elems:
        return elems[-1].get("endIndex")
    return None

def _walk_paragraphs(elem):
    if "paragraph" in elem:
        yield elem["paragraph"]
    if "table" in elem:
        for row in elem["table"].get("tableRows", []):
            for cell in row.get("tableCells", []):
                for c in cell.get("content", []):
                    yield from _walk_paragraphs(c)

def _para_text(para):
    return "".join(e.get("textRun", {}).get("content", "") for e in para.get("elements", []))


# ─── CLI dispatch ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""

    if cmd == "ensure_folder":
        p = argparse.ArgumentParser()
        p.add_argument("--parent-id"); p.add_argument("--name")
        args = p.parse_args(sys.argv[2:])
        ensure_folder(args.parent_id, args.name)

    elif cmd == "copy_template":
        p = argparse.ArgumentParser()
        p.add_argument("--template-id"); p.add_argument("--dest-folder-id")
        p.add_argument("--title")
        args = p.parse_args(sys.argv[2:])
        copy_template(args.template_id, args.dest_folder_id, args.title)

    elif cmd == "populate_brief":
        p = argparse.ArgumentParser()
        p.add_argument("--doc-id"); p.add_argument("--keyword", default="")
        p.add_argument("--secondary", default=""); p.add_argument("--heading", default="")
        p.add_argument("--url", default=""); p.add_argument("--nw-link", default="")
        p.add_argument("--brand", default="")
        p.add_argument("--search-demand", default="")
        args = p.parse_args(sys.argv[2:])
        populate_brief(args.doc_id, args.keyword, args.secondary,
                       args.heading, args.url, args.nw_link, args.brand,
                       args.search_demand)

    elif cmd == "scrape_url":
        p = argparse.ArgumentParser()
        p.add_argument("--url")
        args = p.parse_args(sys.argv[2:])
        scrape_url(args.url)

    elif cmd == "append_content":
        p = argparse.ArgumentParser()
        p.add_argument("--doc-id")
        p.add_argument("--type", default="")
        p.add_argument("--original-file", default="")
        p.add_argument("--optimised-file", default="")
        p.add_argument("--heading", default="")
        args = p.parse_args(sys.argv[2:])
        append_content(args.doc_id, args.type, args.original_file,
                       args.optimised_file, args.heading)

    elif cmd == "clear_content_sections":
        p = argparse.ArgumentParser()
        p.add_argument("--doc-id")
        args = p.parse_args(sys.argv[2:])
        clear_content_sections(args.doc_id)

    else:
        print(f"Unknown command: {cmd}", file=sys.stderr)
        sys.exit(1)
