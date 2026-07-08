#!/usr/bin/env python3
"""
Google Drive + Docs helper for monthly-content-planner.

Commands:
  ensure_folder --parent-id ID --name "FOLDER NAME"
  copy_template --template-id ID --dest-folder-id ID --title "DOC TITLE"
  populate_brief --doc-id ID --keyword KW --secondary SEC --heading H1
                 --url URL --nw-link NW_URL --brand BRAND_KEY
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

    # Search for existing folder with this name inside parent
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

    # Create folder
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

    # Copy the template document
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
def populate_brief(doc_id, keyword, secondary, heading, url, nw_link, brand):
    """
    Fill in the Editorial Information table in the copied template.
    Uses Google Docs API replaceAllText to swap placeholder tokens.

    The template is expected to have these placeholder strings in its table:
      {{KEYWORD}}, {{SECONDARY_KEYWORD}}, {{TITLE}}, {{URL}}, {{NW_LINK}}
    
    If the template does not use placeholders (blank cells), we fall back to
    a table-cell targeting approach.
    """
    docs = docs_service()

    # First, attempt replaceAllText approach
    requests = [
        _replace_req("{{KEYWORD}}", keyword),
        _replace_req("{{SECONDARY_KEYWORD}}", secondary),
        _replace_req("{{TITLE}}", heading),
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
        # Only accept as done if at least one replacement actually happened
        total_replaced = sum(
            r.get("replaceAllTextResponse", {}).get("occurrencesChanged", 0)
            for r in resp.get("replies", [])
        )
        if total_replaced > 0:
            print(json.dumps({"ok": True, "method": "replaceAllText", "replacements": total_replaced, "doc_id": doc_id}))
            return
    except HttpError:
        pass

    # Fallback: read doc, find the table, write to specific cells.
    # Rules: match label text → insert value into the right-column cell.
    # Insertions are sorted high-to-low index so earlier indices aren't shifted.
    doc = docs.documents().get(documentId=doc_id).execute()
    body_content = doc.get("body", {}).get("content", [])

    # Ordered matchers: (label_predicate, value) — first match wins per row.
    fill_rules = [
        (lambda l: "secondary keyword" in l or ("secondary" in l and "keyword" in l), secondary),
        (lambda l: "keyword" in l and "secondary" not in l and "meta" not in l and "url" not in l, keyword),
        (lambda l: l.strip().startswith("title") and "meta" not in l,                  heading),
        (lambda l: "url" in l and "neuronwriter" not in l,                             url),
    ]

    # Collect (insert_index, text) — one entry per matched row.
    inserts = []  # list of (doc_index, text)

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
                    # Find the first text element in the value cell to get insert index
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
                    break  # only one rule per row

    # Handle NW link: find the "NEURONWRITER BRIEF:" paragraph and append after ":"
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
        # Sort highest index first so insertions don't shift earlier positions
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
        args = p.parse_args(sys.argv[2:])
        populate_brief(args.doc_id, args.keyword, args.secondary,
                       args.heading, args.url, args.nw_link, args.brand)

    else:
        print(f"Unknown command: {cmd}", file=sys.stderr)
        sys.exit(1)
