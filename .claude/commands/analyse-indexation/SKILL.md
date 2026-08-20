---
name: seo.analyse-indexation
description: >
  Analyzes the Google indexation status of a site's indexable URLs. Runs a local Screaming Frog
  crawl, extracts the indexable URLs returning a 200 status, then queries the Google Search
  Console URL Inspection API (MCP google-search-console) for each URL. Produces a 3-column CSV
  (Indexable URLs, Indexation Status, Comments). Use when the user wants to audit URL indexation,
  check which pages are indexed by Google, mentions "indexation status", "indexed URLs",
  "GSC inspection", "/seo.analyse-indexation".
user-invocable: true
---

# Indexation Status: Google Indexation Audit

This skill audits the Google indexation status of a site's indexable URLs. Full workflow:

0. **External tool check (blocking)**: don't launch anything if a required tool is missing
1. Local Screaming Frog crawl: **always a fresh crawl**
2. Extraction of indexable URLs returning a 200 status
3. Querying the GSC URL Inspection API for each URL
4. Generation of a 3-column CSV (data source)
5. Formatting of the final deliverable as XLSX in Digitad colors (red header, Poppins font)

## Arguments

- `$ARGUMENTS`: Free form. The site URL to analyze plus optional flags.
  - Example: `https://www.example.com/`
  - Example: `https://www.example.com/ --site sc-domain:example.com`

## Flags

| Flag | Effect |
|------|-------|
| `--site <siteUrl>` | GSC property URL (e.g., `https://www.example.com/` or `sc-domain:example.com`). If omitted, the skill calls `list_sites` and proposes an automatic match. |
| `--account <alias>` | GSC account alias. If omitted, uses the default account. |
| `--prefix <url-prefix>` | Limits the analysis to URLs matching this prefix (e.g., `https://www.example.com/fr_ca/`). Can be repeated for multiple prefixes: `--prefix /fr_ca/ --prefix /en_ca/`. Useful for multi-locale sites. |
| `--limit <n>` | Caps the number of URLs to inspect (useful for testing). Default: all. |
| `--resume` | Resumes an interrupted analysis from the partial CSV. |

---

## Step 0: External tool check (BLOCKING)

> **Hard rule**: this is the **very first thing to do**, before any crawl or analysis. If a **required** tool is missing, **don't launch anything**: inform the user of what's missing and how to fix it, then **stop cleanly**. Never work around a missing tool or fabricate results.

### Tools required by mode

| Tool | Required? | How to check | If missing |
|-------|----------|---------------------|-----------|
| **Python 3** | Always (CSV extraction + deliverable writing) | `command -v python3` | Stop. Ask the user to install Python 3. |
| **Screaming Frog** (local app, **licensed**) | Always (a fresh crawl is launched on every run) | `test -f "/Applications/Screaming Frog SEO Spider.app/Contents/MacOS/ScreamingFrogSEOSpiderLauncher"` | Stop. Suggest installing SF. Reminder: `--headless` mode requires an **active paid license** (the free version doesn't run in CLI). |
| **MCP google-search-console** | Always (core of the skill: URL inspection) | Call `mcp__google-search-console__list_sites` | Stop. Ask the user to connect/authorize the MCP google-search-console. Without it, the indexation audit is impossible. |

### Checks to run in parallel at startup

```bash
# 1. Is Python 3 available?
command -v python3 >/dev/null && echo "PYTHON_OK" || echo "PYTHON_MISSING"

# 2. Is Screaming Frog installed?
test -f "/Applications/Screaming Frog SEO Spider.app/Contents/MacOS/ScreamingFrogSEOSpiderLauncher" \
  && echo "SF_OK" || echo "SF_MISSING"

# 3. No SF instance already running (GUI or headless)?
pgrep -fl "ScreamingFrogSEOSpider" | head -3
```

And **in parallel**, MCP call: `mcp__google-search-console__list_sites`, which both validates the GSC connection and identifies the property matching the domain (reused in Step 3).

### Decision

- **All required tools OK** → continue to Step 1.
- **A required tool is missing** → display a clear summary of what's missing, then **stop without launching anything**.

Example blocking message:

```
⛔ Cannot launch the indexation audit. Missing tools:
  - MCP google-search-console: not connected → authorize it, it's required for URL inspection.
  - Screaming Frog: not installed (or not licensed) → install it and activate the license (required for headless mode).

I won't launch anything until this is resolved.
```

### Case: SF already running

- If the process is running **in `--headless` mode** (visible in `pgrep -fl`): a crawl is in progress, wait or kill it with `pkill -f ScreamingFrogSEOSpider`.
- If the process is running **without `--headless`** (GUI open): Screaming Frog is open in the graphical interface. The headless crawl cannot start in parallel. Ask the user to close the application manually (also offer `pkill -f ScreamingFrogSEOSpider` as an alternative, warning of the risk of losing an unsaved GUI crawl).

### Case: ambiguous GSC property

- Prefer `sc-domain:example.com` (domain property, broader) if available.
- Otherwise prefer the exact URL property (`https://www.example.com/`).
- If there are multiple matches, ask the user for confirmation.

---

## Step 1: Screaming Frog crawl

> **Hard rule**: this skill always launches a **fresh crawl**. There is no reuse of an existing crawl. Every run starts from a clean crawl to guarantee an up-to-date indexation status.

### Standard case: new crawl

- **Output directory**: `screaming-frog/output/<domain>/<YYYY-MM-DD>-indexation/` (dated subfolder so older crawls aren't overwritten). Extract the domain from the URL and strip `www.` (e.g., `https://www.example.com/` → `example.com`).
- `--headless` mode mandatory, launched via `nohup` in the background.
- Monitoring: wait for completion via `until ! pgrep -f "ScreamingFrogSEOSpider.jar" > /dev/null; do sleep 15; done` (in `run_in_background`).

> **Important**: this skill only needs the `internal_all.csv` file (or `interne_tous.csv` in FR locale). No need for all the GEO exports if all you want is indexation. **Recommended minimal crawl**: `Internal:All` tab only.

**Minimal crawl (recommended)**:

```bash
OUTPUT_DIR="screaming-frog/output/<domain>/$(date +%Y-%m-%d)-indexation"
mkdir -p "$OUTPUT_DIR"

nohup "/Applications/Screaming Frog SEO Spider.app/Contents/MacOS/ScreamingFrogSEOSpiderLauncher" \
  --headless \
  --crawl "<URL>" \
  --output-folder "$(pwd)/$OUTPUT_DIR" \
  --export-tabs "Internal:All" \
  > "$OUTPUT_DIR/crawl.log" 2>&1 &

echo "PID: $!"
```

Always ask the user whether they prefer a minimal crawl or a full GEO crawl (the GEO crawl then follows the conventions of the `seo.crawl-screaming-frog-local` skill).

### Multi-locale case: analysis by URL prefix

If `--prefix` is provided (one or more), launch one crawl per prefix, starting from each root. Example for `--prefix https://www.example.com/fr_ca/ --prefix https://www.example.com/en_ca/`:

```bash
for PREFIX in "https://www.example.com/fr_ca/" "https://www.example.com/en_ca/"; do
  LOCALE=$(echo "$PREFIX" | sed -E 's|.*/([a-z_]+)/?$|\1|')
  OUT="screaming-frog/output/<domain>/$(date +%Y-%m-%d)-indexation-$LOCALE"
  mkdir -p "$OUT"
  nohup "/Applications/.../ScreamingFrogSEOSpiderLauncher" --headless \
    --crawl "$PREFIX" --output-folder "$(pwd)/$OUT" --export-tabs "Internal:All" \
    > "$OUT/crawl.log" 2>&1 &
  wait $!  # or explicit monitor
done
```

In Step 2, **filter afterward** to keep only URLs starting with one of the prefixes (SF often discovers out-of-scope URLs via internal links).

---

## Step 2: Extraction of indexable 200 URLs

Read the internal CSV (encoding `utf-8-sig`) and filter on 3 conditions:

- Status Code == `200`
- Indexability == `Indexable`
- Content Type contains `text/html`

**Important (SF locale)**: Screaming Frog exports column headers in the language of its interface. The script must handle **both locales** (English and French):

| Field | EN | FR |
|-------|----|----|
| URL | `Address` | `Adresse` |
| Code | `Status Code` | `Code HTTP` |
| Indexability | `Indexability` | `Indexabilité` |
| Content type | `Content Type` | `Type de contenu` |

```python
import csv, glob, os

# Auto-detect the internal CSV (EN or FR)
crawl_dir = "screaming-frog/output/<domain>/<YYYY-MM-DD>-indexation"
candidates = [f"{crawl_dir}/internal_all.csv", f"{crawl_dir}/interne_tous.csv"]
input_path = next((p for p in candidates if os.path.exists(p)), None)
assert input_path, f"No internal CSV found in {crawl_dir}"

# FR / EN mapping
COL = {
    "address": ["Address", "Adresse"],
    "status": ["Status Code", "Code HTTP"],
    "indexability": ["Indexability", "Indexabilité"],
    "content_type": ["Content Type", "Type de contenu"],
}

def pick(row, key):
    for col in COL[key]:
        if col in row:
            return row[col]
    return ""

# Optional: filter by prefix (--prefix mode)
prefixes = []  # e.g., ["https://www.example.com/fr_ca/", "https://www.example.com/en_ca/"]

urls = []
total = 0
with open(input_path, "r", encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
    for row in reader:
        total += 1
        if (pick(row, "status").strip() == "200"
            and pick(row, "indexability").strip() == "Indexable"
            and "text/html" in pick(row, "content_type").lower()):
            url = pick(row, "address")
            if not prefixes or any(url.startswith(p) for p in prefixes):
                urls.append(url)

urls = sorted(set(urls))
print(f"Total URLs crawled: {total} | Indexable 200 HTML: {len(urls)}")

# Save the list for step 4 (sub-agent)
with open(f"{crawl_dir}/indexable_urls.txt", "w") as f:
    for u in urls:
        f.write(u + "\n")
```

**Report to the user**:
- Total number of URLs crawled
- Number of indexable 200 URLs retained
- GSC quota consumed (`X / 2000 daily`)

---

## Step 3: GSC quota and property check

### 3.1 Identify the GSC property

If `--site` is not provided, list the available properties via the MCP:

```
mcp__google-search-console__list_sites
```

Then match against the crawled domain. Prefer in this order:
1. Exact domain property (`sc-domain:example.com`)
2. Exact URL property (`https://www.example.com/`)
3. Ask the user for confirmation if there are multiple matches or ambiguity.

### 3.2 Warn about quota

The URL Inspection API is limited to **2000 requests/day/property** and **~600 requests/minute**.

If `len(urls) > 2000`, warn the user and offer to:
- Limit to 2000 via `--limit 2000`
- Sample (first N URLs, or priority URLs)
- Spread over several days (use `--resume`)

---

## Step 4: GSC URL-by-URL inspection (via sub-agent)

> **Hard rule**: for > 30 URLs, **always delegate to a `general-purpose` sub-agent**. Reasons: (1) parallelization in batches of 15, much faster; (2) the 100-500 verbose GSC API responses don't clutter the main agent's context; (3) the main agent stays responsive to the user.
>
> Below 30 URLs, the main agent can make the calls directly in parallel batches of 15 within a single response.

### Standard prompt for the sub-agent

Always pass **absolute paths** (`/Users/...`), not relative paths, since the sub-agent may have a different cwd.

```
Task: perform N GSC URL Inspections for <domain> and produce a CSV.

CONTEXT
- Source file: /Users/melissarebillou/screaming-frog/output/<domain>/<YYYY-MM-DD>-indexation/indexable_urls.txt (N URLs, one per line)
- GSC property: `<sc-domain:domain.com OR https://www.domain.com/>`
- MCP: `mcp__google-search-console__inspect_url` (parameters: siteUrl, inspectionUrl)

WHAT YOU NEED TO DO

1. Read indexable_urls.txt (N URLs).

2. Inspect each URL via `mcp__google-search-console__inspect_url` with siteUrl="<GSC property>". Launch in PARALLEL BATCHES of 15 URLs (15 tool calls in the same response). Wait for each batch to finish before the next.

3. Parse `Coverage State: <value>` from each response (the "=== Index Status ===" block). If absent → "Inspection failed".

4. Write /Users/melissarebillou/screaming-frog/output/<domain>/<YYYY-MM-DD>-indexation/inspection_results.csv (header `url,coverage_state`, utf-8 encoding, via Python's `csv` module). Save incrementally every 50 URLs.

RETURN (under 200 words)
- Total inspected / failures
- Full Coverage State distribution (sorted descending with count and %)
- Pattern by sub-section if relevant (e.g., /fr/* vs /en/*, /blog/* vs /products/*)
- Path of the CSV

DO NOT: map to Indexed/Not Indexed (the main agent handles that), verbose dump, call list_sites
```

### Response mapping (to apply in the main agent after the sub-agent)

The MCP response format is structured text (NOT JSON) with a block:

```
=== Index Status ===
Coverage State: <value>
Indexing State: INDEXING_ALLOWED
Page Fetch State: SUCCESSFUL
Robots.txt State: ALLOWED
Last Crawl: 2026-05-20T21:28:47Z
Google Canonical: https://...
User Canonical: https://...
```

### Mapping rules → final CSV

- **Column B `Indexation Status`**:
  - `Indexed` if `Coverage State` starts with `"Submitted and indexed"` OR `"Indexed"`
  - `Unknown` if `Coverage State` == `"Inspection failed"`
  - `Not Indexed` in all other cases

- **Column C `Comments`**:
  - Empty if Indexed (the "Submitted and indexed" label is implicit)
  - Raw `coverageState` in all other cases (e.g., `Crawled - currently not indexed`, `Discovered - currently not indexed`, `Page with redirect`, `Duplicate without user-selected canonical`, `Duplicate, Google chose different canonical than user`, `Submitted URL not selected as canonical`, `Blocked by robots.txt`, `Excluded by 'noindex' tag`, `Soft 404`, `URL is unknown to Google`)

### Rate limit handling

- The GSC API limits to **~600 req/min** and **2000 req/day/property**.
- Batches of 15 in parallel = ~10-15 req/sec, safe.
- On a 429 error (quota exceeded), the sub-agent should pause 60 sec and retry once, then save state for `--resume`.

---

## Step 5: Final CSV generation

### File name

**Unique and mandatory** format, always in English:

```
[Current Month] [Current Year] - [Site Name] - Coverage Analysis.csv
```

- **Current month**: month name in English (e.g., `May`, `June`), forced to English even if the Mac's locale is French.
- **Current year**: 4-digit year.
- **Site name**: the domain without `www.` (e.g., `example.com`).
- **Literal suffix**: ` - Coverage Analysis`.

Example: `May 2026 - example.com - Coverage Analysis.csv`

Full path:

```
screaming-frog/output/<domain>/May 2026 - example.com - Coverage Analysis.csv
```

> The final CSV goes in the **parent** folder (`<domain>/`), not in the `<YYYY-MM-DD>-indexation/` subfolder. This way you can find it easily at the domain root, independent of the crawl used.

### Format

3 columns, `utf-8-sig` encoding (for Excel/Sheets compatibility):

```csv
Indexable URLs,Indexation Status,Comments
https://www.example.com/,Indexed,
https://www.example.com/page-a,Not Indexed,Crawled - currently not indexed
https://www.example.com/page-b,Not Indexed,Discovered - currently not indexed
```

### Reference code

```python
import csv, datetime

# English month name guaranteed, independent of system locale
MONTHS_EN = ["January", "February", "March", "April", "May", "June",
             "July", "August", "September", "October", "November", "December"]
today = datetime.date.today()
domain = "example.com"  # domain without www.
label = f"{MONTHS_EN[today.month - 1]} {today.year} - {domain} - Coverage Analysis"

output_path = f"screaming-frog/output/{domain}/{label}.csv"
with open(output_path, "w", encoding="utf-8-sig", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Indexable URLs", "Indexation Status", "Comments"])
    for row in results:
        writer.writerow([row["url"], row["status"], row["comment"]])
```

### Statistics to report to the user

At the end of the run, display:

| Metric | Value |
|----------|--------|
| URLs analyzed | 847 |
| Indexed | 812 (95.9%) |
| Not Indexed | 35 (4.1%) |
| Inspection failures | 0 |

Then detail the top `coverageState` values among the `Not Indexed`:

```
Top reasons for non-indexation:
- Crawled - currently not indexed: 18
- Discovered - currently not indexed: 12
- Duplicate without user-selected canonical: 5
```

---

## Step 6: Digitad formatting (XLSX deliverable)

The final deliverable is an **Excel `.xlsx` file formatted in Digitad brand colors**, generated from the Step 5 CSV. Since a CSV can't carry styling, the XLSX is the **deliverable presented to the client**.

### Dependency

This step uses `openpyxl`. Check it's available, otherwise install it:

```bash
python3 -c "import openpyxl" 2>/dev/null || pip3 install openpyxl
```

### Digitad brand guidelines to apply

| Element | Value |
|---------|--------|
| Font (all cells) | **Poppins** |
| **Row 1 (table header)** | **red `#b9001c`** background, **white `#ffffff`** text, **bold** |
| Table body | black text `#1a1a1a` (gray 800, softer than pure black) |
| Alternating rows (zebra striping) | gray 100 `#f5f5f5` every other row |
| Borders | gray 200 `#e5e5e5` |

> **Absolute brand rule**: text on a red background is **always white** (`#ffffff`). Never black/gray/red on red.

### File name

Same format as the CSV, `.xlsx` extension:

```
screaming-frog/output/<domain>/May 2026 - example.com - Coverage Analysis.xlsx
```

### Reference code

```python
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

# Digitad brand guidelines
RED     = "FFB9001C"   # #b9001c (ARGB, FF prefix = opaque)
WHITE   = "FFFFFFFF"
BLACK   = "FF1A1A1A"   # gray 800
GRAY100 = "FFF5F5F5"   # zebra striping
GRAY200 = "FFE5E5E5"   # borders
FONT    = "Poppins"

wb = openpyxl.Workbook()
ws = wb.active
ws.title = "Coverage Analysis"

headers = ["Indexable URLs", "Indexation Status", "Comments"]
ws.append(headers)
for row in results:  # results = list of dicts {url, status, comment}
    ws.append([row["url"], row["status"], row["comment"]])

thin = Side(style="thin", color=GRAY200)
border = Border(left=thin, right=thin, top=thin, bottom=thin)

# Row 1: red header, white text, bold, Poppins
for cell in ws[1]:
    cell.fill = PatternFill("solid", fgColor=RED)
    cell.font = Font(name=FONT, bold=True, color=WHITE, size=11)
    cell.alignment = Alignment(vertical="center")
    cell.border = border

# Body: black Poppins, gray 100 zebra striping every other row
for i, row in enumerate(ws.iter_rows(min_row=2), start=2):
    fill = PatternFill("solid", fgColor=GRAY100) if i % 2 == 0 else None
    for cell in row:
        cell.font = Font(name=FONT, color=BLACK, size=10)
        cell.border = border
        if fill:
            cell.fill = fill

# Readable column widths + freeze header
ws.column_dimensions["A"].width = 70
ws.column_dimensions["B"].width = 20
ws.column_dimensions["C"].width = 45
ws.freeze_panes = "A2"

xlsx_path = f"screaming-frog/output/{domain}/{label}.xlsx"  # label = "May 2026 - example.com - Coverage Analysis"
wb.save(xlsx_path)
```

> **Poppins note**: `openpyxl` doesn't embed the font, it just writes its name. On a machine where Poppins is installed (Digitad's case), Excel/Sheets display it; otherwise automatic fallback. The raw CSV from Step 5 remains stored as the data source (and for `--resume`).

---

## Final output

Report to the user:

- **Formatted XLSX deliverable (Digitad)**: `screaming-frog/output/<domain>/[Month] [Year] - <domain> - Coverage Analysis.xlsx` (e.g., `May 2026 - example.com - Coverage Analysis.xlsx`)
- **Source CSV**: `screaming-frog/output/<domain>/[Month] [Year] - <domain> - Coverage Analysis.csv`
- **Stats**: recap table (URLs analyzed, Indexed, Not Indexed, top reasons)
- **Recommended action** for Not Indexed URLs based on the dominant `coverageState`:
  - `Crawled - currently not indexed` → improve content quality / internal linking
  - `Discovered - currently not indexed` → submit via GSC + boost internal linking
  - `Duplicate without user-selected canonical` → add canonical tags
  - `Page with redirect` → verify intent (may be normal)

---

## Notes

- **Local crawl by default** ([[feedback_crawl_local]]). No VM, no SSH.
- **Never guess the GSC property**: always go through `list_sites` to confirm.
- **Respect the GSC quota**: 2000 URLs/day/property. Beyond that, spread out or sample.
- **No Slack message** ([[feedback_no_slack]]).
- The final deliverable is an **XLSX formatted in Digitad colors** (red header `#b9001c`, Poppins font), generated in Step 6. The 3-column CSV remains produced upstream as the data source.
