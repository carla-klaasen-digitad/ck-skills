"""
init_session.py  —  seo-geo-technical-audit-v13
================================================
Interactive session initialisation script. Run once at the start of every
audit session, before Phase 0.

    python3 scripts/init_session.py

What it does:
  1. Locates and loads ~/.config/digitad/.env (fallback: skill root .env)
  2. Tests connectivity for each configured API
  3. Collects client name, site URL, and per-source API vs manual mode
  4. Confirms Google Drive folders for main deliverables and export sheets
  5. Writes audit-session-config.json to the skill root
  6. Prints a summary table and "Session initialised." confirmation

Do not proceed to Phase 0 until this script prints "Session initialised."

SE RANKING NOTE
---------------
SE Ranking supports two modes (Option C):
  - "mcp"  — Claude Code uses the SE Ranking MCP directly during the audit
             for interactive queries. No API key required for this path.
  - "api"  — fetch_data.py calls the SE Ranking REST API using SE_RANKING_API_KEY.
             Use this when you want fully automated data pulls without Claude interaction.

REQUIREMENTS
------------
  pip install requests google-auth google-auth-oauthlib google-api-python-client
              gspread python-dotenv
"""

import argparse
import glob
import json
import os
import sys
import datetime
import requests

# Resolve paths relative to the skill root (one directory up from scripts/)
SKILL_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Common directories to scan for SF config files (user can save them anywhere)
SF_SCAN_DIRS = [
    os.path.expanduser("~"),
    os.path.expanduser("~/Documents"),
    os.path.expanduser("~/Downloads"),
    os.path.expanduser("~/Desktop"),
]
ENV_PRIMARY   = os.path.expanduser("~/.config/digitad/.env")
ENV_FALLBACK  = os.path.join(SKILL_ROOT, ".env")
CONFIG_OUTPUT = os.path.join(SKILL_ROOT, "audit-session-config.json")

# ── ENV LOADING ───────────────────────────────────────────────────────────────
def load_env():
    from dotenv import load_dotenv
    if os.path.isfile(ENV_PRIMARY):
        load_dotenv(ENV_PRIMARY)
        print(f"  Loaded: {ENV_PRIMARY}")
        return ENV_PRIMARY
    elif os.path.isfile(ENV_FALLBACK):
        load_dotenv(ENV_FALLBACK)
        print(f"  Loaded (fallback): {ENV_FALLBACK}")
        return ENV_FALLBACK
    else:
        print(f"\n  No .env file found.")
        print(f"  Expected: {ENV_PRIMARY}")
        ans = input("  Create it now interactively? (yes/no): ").strip().lower()
        if ans == "yes":
            create_env_interactively()
            load_dotenv(ENV_PRIMARY)
            return ENV_PRIMARY
        else:
            print("  Proceeding without .env — all APIs will be SKIPPED.")
            return None


def create_env_interactively():
    """Walk the user through creating ~/.config/digitad/.env key by key."""
    os.makedirs(os.path.dirname(ENV_PRIMARY), exist_ok=True)
    keys = [
        ("SF_API_URL",                  "Screaming Frog API URL", "http://localhost:8775/"),
        ("SE_RANKING_API_KEY",          "SE Ranking API key", ""),
        ("MAJESTIC_API_KEY",            "Majestic API key", ""),
        ("GOOGLE_SERVICE_ACCOUNT_JSON", "Google service account JSON path", ""),
        ("GDRIVE_MAIN_DIR_ID",          "Google Drive folder ID — main deliverables", ""),
        ("GDRIVE_EXPORTS_DIR_ID",       "Google Drive folder ID — export sheets", ""),
        ("GDRIVE_HTML_DIR_ID",          "Google Drive folder ID — HTML reports (optional)", ""),
        ("PSI_API_KEY",                 "PageSpeed Insights API key", ""),
        ("GSC_CLIENT_SECRETS_JSON",     "GSC OAuth2 client secrets JSON path", ""),
        ("GSC_PROPERTY_URL",            "GSC property URL", ""),
        ("GA4_PROPERTY_ID",             "GA4 property ID", ""),
        ("MOZ_ACCESS_ID",               "Moz Access ID", ""),
        ("MOZ_SECRET_KEY",              "Moz Secret Key", ""),
        ("WHOIS_API_KEY",               "WHOIS XML API key", ""),
    ]
    lines = []
    for key, label, default in keys:
        prompt = f"  {label}" + (f" [{default}]" if default else "") + ": "
        val = input(prompt).strip() or default
        lines.append(f"{key}={val}")
    with open(ENV_PRIMARY, "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"\n  Written: {ENV_PRIMARY}")


# ── API CONNECTION TESTS ──────────────────────────────────────────────────────
def test_sf():
    url = os.getenv("SF_API_URL", "http://localhost:8775/").rstrip("/")
    key = os.getenv("SF_API_URL", "").strip()
    if not key:
        return "SKIPPED", "SF_API_URL not set"
    try:
        r = requests.get(f"{url}/system/status", timeout=5)
        data = r.json()
        if data.get("status") == "ok":
            return "PASS", f"Screaming Frog API responding at {url}"
        return "FAIL", f"Unexpected response: {data}"
    except Exception as e:
        return "FAIL", str(e)


def test_se_ranking(mode):
    if mode == "mcp":
        return "MCP", "SE Ranking MCP mode selected — interactive use via Claude Code"
    api_key = os.getenv("SE_RANKING_API_KEY", "").strip()
    if not api_key:
        return "SKIPPED", "SE_RANKING_API_KEY not set"
    try:
        r = requests.get(
            "https://api4.seranking.com/sites",
            headers={"Authorization": f"Token {api_key}"},
            timeout=10,
        )
        if r.status_code == 200:
            return "PASS", "SE Ranking API responding"
        return "FAIL", f"HTTP {r.status_code}: {r.text[:100]}"
    except Exception as e:
        return "FAIL", str(e)


def test_majestic():
    api_key = os.getenv("MAJESTIC_API_KEY", "").strip()
    if not api_key:
        return "SKIPPED", "MAJESTIC_API_KEY not set"
    try:
        r = requests.get(
            "https://developer.majestic.com/api/json",
            params={
                "app_api_key": api_key,
                "cmd": "GetIndexItemInfo",
                "items": 1,
                "item0": "example.com",
            },
            timeout=10,
        )
        if r.status_code == 200:
            return "PASS", "Majestic API responding"
        return "FAIL", f"HTTP {r.status_code}: {r.text[:100]}"
    except Exception as e:
        return "FAIL", str(e)


def test_google_drive():
    sa_path = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON", "").strip()
    dir_id  = os.getenv("GDRIVE_MAIN_DIR_ID", "").strip()
    if not sa_path or not dir_id:
        return "SKIPPED", "GOOGLE_SERVICE_ACCOUNT_JSON or GDRIVE_MAIN_DIR_ID not set"
    if not os.path.isfile(sa_path):
        return "FAIL", f"Service account JSON not found: {sa_path}"
    try:
        from googleapiclient.discovery import build
        from google.oauth2.service_account import Credentials
        creds = Credentials.from_service_account_file(
            sa_path,
            scopes=["https://www.googleapis.com/auth/drive"],
        )
        svc = build("drive", "v3", credentials=creds)
        svc.files().list(q=f"'{dir_id}' in parents", pageSize=1).execute()
        return "PASS", f"Google Drive accessible — folder {dir_id}"
    except Exception as e:
        return "FAIL", str(e)


def test_psi():
    api_key = os.getenv("PSI_API_KEY", "").strip()
    if not api_key:
        return "SKIPPED", "PSI_API_KEY not set"
    try:
        r = requests.get(
            "https://www.googleapis.com/pagespeedonline/v5/runPagespeed",
            params={"url": "https://example.com", "key": api_key},
            timeout=30,
        )
        if r.status_code == 200:
            return "PASS", "PageSpeed Insights API responding"
        return "FAIL", f"HTTP {r.status_code}: {r.text[:100]}"
    except Exception as e:
        return "FAIL", str(e)


def test_gsc():
    secrets = os.getenv("GSC_CLIENT_SECRETS_JSON", "").strip()
    if not secrets:
        return "SKIPPED", "GSC_CLIENT_SECRETS_JSON not set"
    if not os.path.isfile(secrets):
        return "FAIL", f"GSC secrets file not found: {secrets}"
    token_path = os.path.join(os.path.dirname(secrets), "gsc_token.pickle")
    if os.path.isfile(token_path):
        return "PASS", "GSC token present — credentials available"
    return "WARN", "GSC secrets found but no token yet — first run will prompt browser auth"


def test_ga4():
    sa_path     = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON", "").strip()
    property_id = os.getenv("GA4_PROPERTY_ID", "").strip()
    if not sa_path or not property_id:
        return "SKIPPED", "GOOGLE_SERVICE_ACCOUNT_JSON or GA4_PROPERTY_ID not set"
    try:
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = sa_path
        from google.analytics.data_v1beta import BetaAnalyticsDataClient
        from google.analytics.data_v1beta.types import RunReportRequest, DateRange, Metric
        client = BetaAnalyticsDataClient()
        client.run_report(RunReportRequest(
            property=f"properties/{property_id}",
            date_ranges=[DateRange(start_date="today", end_date="today")],
            metrics=[Metric(name="sessions")],
        ))
        return "PASS", f"GA4 API responding for property {property_id}"
    except Exception as e:
        return "FAIL", str(e)


def test_moz():
    access_id  = os.getenv("MOZ_ACCESS_ID", "").strip()
    secret_key = os.getenv("MOZ_SECRET_KEY", "").strip()
    if not access_id or not secret_key:
        return "SKIPPED", "MOZ_ACCESS_ID or MOZ_SECRET_KEY not set"
    try:
        import base64
        token = base64.b64encode(f"{access_id}:{secret_key}".encode()).decode()
        r = requests.post(
            "https://lsapi.seomoz.com/v2/url_metrics",
            headers={"Authorization": f"Basic {token}", "Content-Type": "application/json"},
            json={"targets": ["example.com/"]},
            timeout=10,
        )
        if r.status_code == 200:
            return "PASS", "Moz API responding"
        return "FAIL", f"HTTP {r.status_code}: {r.text[:100]}"
    except Exception as e:
        return "FAIL", str(e)


def test_whois():
    api_key = os.getenv("WHOIS_API_KEY", "").strip()
    if not api_key:
        return "SKIPPED", "WHOIS_API_KEY not set"
    try:
        r = requests.get(
            "https://www.whoisxmlapi.com/whoisserver/WhoisService",
            params={
                "domainName": "example.com",
                "apiKey": api_key,
                "outputFormat": "JSON",
            },
            timeout=10,
        )
        if r.status_code == 200:
            return "PASS", "WHOIS XML API responding"
        return "FAIL", f"HTTP {r.status_code}: {r.text[:100]}"
    except Exception as e:
        return "FAIL", str(e)


# ── DRIVE DIRECTORY VALIDATION ────────────────────────────────────────────────
def validate_drive_folder(folder_id, label):
    """Test write access by creating and immediately deleting a test file."""
    sa_path = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON", "").strip()
    if not sa_path or not folder_id:
        return False, "Service account or folder ID missing"
    try:
        from googleapiclient.discovery import build
        from google.oauth2.service_account import Credentials
        from googleapiclient.http import MediaInMemoryUpload
        creds = Credentials.from_service_account_file(
            sa_path,
            scopes=["https://www.googleapis.com/auth/drive"],
        )
        svc = build("drive", "v3", credentials=creds)
        # Create test file
        meta = {"name": "_init_test_delete_me.txt", "parents": [folder_id]}
        media = MediaInMemoryUpload(b"init_test", mimetype="text/plain")
        f = svc.files().create(body=meta, media_body=media, fields="id").execute()
        # Delete it immediately
        svc.files().delete(fileId=f["id"]).execute()
        return True, f"{label} folder accessible and writable"
    except Exception as e:
        return False, str(e)


# ── SCREAMING FROG CONFIG INSPECTION ─────────────────────────────────────────
def _sf_base_url():
    return os.getenv("SF_API_URL", "http://localhost:8775").rstrip("/")


def _list_sf_configs_via_api():
    """
    Call the SF REST API to list saved configurations.
    Returns a list of config name strings, or None if SF is not reachable.
    """
    try:
        url = f"{_sf_base_url()}/api/system/config/list"
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            data = r.json()
            # SF returns either a list of strings or list of objects
            if isinstance(data, list):
                return [c if isinstance(c, str) else c.get("name", str(c)) for c in data]
            return []
        return None
    except Exception:
        return None


def _list_sf_configs_filesystem():
    """
    Scan common user directories for Screaming Frog .seospiderconfig files.
    SF configs are saved wherever the user chooses — there is no fixed system path.
    Searches ~, ~/Documents, ~/Downloads, ~/Desktop up to 2 levels deep.
    Returns a list of (display_name, full_path) tuples.
    """
    found = {}  # path -> basename, deduped by path
    for base_dir in SF_SCAN_DIRS:
        if not os.path.isdir(base_dir):
            continue
        # Depth 0 (base dir itself) and depth 1 (immediate subdirs)
        for root, dirs, files in os.walk(base_dir):
            depth = root.replace(base_dir, "").count(os.sep)
            if depth > 1:
                dirs[:] = []  # prune — don't go deeper
                continue
            for fname in files:
                if fname.endswith(".seospiderconfig"):
                    full = os.path.join(root, fname)
                    if full not in found:
                        found[full] = fname
    return [(name, path) for path, name in found.items()]


def _match_config(config_names, client_name):
    """Return the first config name that contains the client name (case-insensitive)."""
    needle = client_name.lower().replace(" ", "").replace("-", "")
    for name in config_names:
        haystack = name.lower().replace(" ", "").replace("-", "")
        if needle in haystack:
            return name
    return None


def check_sf_config(client_name):
    """
    Check for a Screaming Frog saved configuration matching client_name.

    Returns a dict:
        sf_running       bool   — True if the SF REST API responded
        method           str    — "rest_api" | "filesystem" | "none"
        configs          list   — all available config names found
        matched          str|None — the first config name matching client_name
        found            bool   — True if a matching config was found
    """
    result = {
        "sf_running": False,
        "method": "none",
        "configs": [],
        "matched": None,
        "found": False,
    }

    # 1. Try REST API
    api_configs = _list_sf_configs_via_api()
    if api_configs is not None:
        result["sf_running"] = True
        result["method"] = "rest_api"
        result["configs"] = api_configs
        matched = _match_config(api_configs, client_name)
        if matched:
            result["matched"] = matched
            result["found"] = True
        return result

    # 2. Fallback: filesystem scan
    fs_configs = _list_sf_configs_filesystem()  # list of (name, path) tuples
    if fs_configs:
        result["method"] = "filesystem"
        result["configs"] = [name for name, _ in fs_configs]
        result["config_paths"] = {name: path for name, path in fs_configs}
        config_names = result["configs"]
        matched = _match_config(config_names, client_name)
        if matched:
            result["matched"] = matched
            result["matched_path"] = result["config_paths"].get(matched)
            result["found"] = True

    return result


# ── DRIVE-ONLY VALIDATION ─────────────────────────────────────────────────────
def validate_drive_only():
    """
    Load .env and validate Google Drive connection + configured folder IDs.
    Used by the Phase 0 workbook format step when Google Sheet is selected.
    Returns True if Drive is accessible and writable, False otherwise.
    """
    load_env()
    status, msg = test_google_drive()
    print(f"\nDrive connection: {status} — {msg}")
    if status != "PASS":
        return False

    all_ok = True
    for env_key, label in [
        ("GDRIVE_MAIN_DIR_ID",    "Main deliverables folder"),
        ("GDRIVE_EXPORTS_DIR_ID", "Export sheets folder"),
    ]:
        folder_id = os.getenv(env_key, "").strip()
        if folder_id:
            ok, detail = validate_drive_folder(folder_id, label)
            icon = "✓" if ok else "✗"
            print(f"  [{icon}] {label}: {detail}")
            if not ok:
                all_ok = False
        else:
            print(f"  [–] {label}: not configured ({env_key} not set)")
    return all_ok


# ── INTERACTIVE COLLECTION ────────────────────────────────────────────────────
def ask_api_mode(source_label, api_status, default="yes"):
    """Ask whether to use API or manual mode for a data source."""
    if api_status in ("SKIPPED", "FAIL"):
        print(f"    {source_label}: API not available ({api_status}) — defaulting to manual mode")
        return "manual"
    if api_status == "MCP":
        return "mcp"
    ans = input(f"    Use API to auto-fetch {source_label}? (yes/no) [{default}]: ").strip().lower()
    return "api" if (ans == "yes" or (ans == "" and default == "yes")) else "manual"


def parse_folder_id(raw):
    """Extract folder ID from a Drive URL or return as-is if it looks like an ID."""
    raw = raw.strip()
    if "drive.google.com" in raw:
        # https://drive.google.com/drive/folders/FOLDER_ID
        import re
        m = re.search(r"/folders/([a-zA-Z0-9_-]+)", raw)
        if m:
            return m.group(1)
    return raw


# ── MAIN ──────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="SEO & GEO Audit — Session Initialiser v13",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--validate-drive-only",
        action="store_true",
        help="Validate Google Drive connection and folder access, then exit.",
    )
    parser.add_argument(
        "--check-sf-config",
        metavar="CLIENT_NAME",
        help="Check for a Screaming Frog config matching CLIENT_NAME, then exit.",
    )
    args = parser.parse_args()

    # ── Fast-exit modes ──────────────────────────────────────────────────────
    if args.validate_drive_only:
        ok = validate_drive_only()
        sys.exit(0 if ok else 1)

    if args.check_sf_config:
        result = check_sf_config(args.check_sf_config)
        print(json.dumps(result, indent=2))
        sys.exit(0 if result["found"] else 1)

    # ── Full interactive flow ─────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("  SEO & GEO Audit — Session Initialisation")
    print("  v13 | Digitad")
    print("=" * 60)

    # 1. Load .env
    print("\n[1/5] Loading environment...")
    env_path = load_env()

    # 2. SE Ranking mode selection (before running tests)
    print("\n[2/5] SE Ranking mode selection")
    print("  SE Ranking supports two modes:")
    print("    (a) MCP  — Claude Code uses the SE Ranking MCP connection")
    print("               interactively during audits. No API key needed.")
    print("    (b) API  — fetch_data.py pulls data via REST API using SE_RANKING_API_KEY.")
    se_mode_raw = input("  Select SE Ranking mode (a=MCP / b=API) [a]: ").strip().lower()
    se_mode_pref = "mcp" if (se_mode_raw in ("", "a", "mcp")) else "api"

    # 3. Run connection tests
    print("\n[3/5] Testing API connections...")
    results = {}
    tests = [
        ("screaming_frog", "Screaming Frog",     lambda: test_sf()),
        ("se_ranking",     "SE Ranking",          lambda: test_se_ranking(se_mode_pref)),
        ("majestic",       "Majestic",            test_majestic),
        ("google_drive",   "Google Drive",        test_google_drive),
        ("psi",            "PageSpeed Insights",  test_psi),
        ("gsc",            "Google Search Console", test_gsc),
        ("ga4",            "Google Analytics 4",  test_ga4),
        ("moz",            "Moz",                 test_moz),
        ("whois",          "WHOIS XML API",        test_whois),
    ]

    for key, label, fn in tests:
        status, msg = fn()
        results[key] = {"status": status, "label": label, "msg": msg}
        icon = {"PASS": "✓", "FAIL": "✗", "SKIPPED": "–", "MCP": "⬡", "WARN": "!"}.get(status, "?")
        print(f"  [{icon}] {label:<30} {status:<8} {msg}")

    # Handle failures
    for key, info in results.items():
        if info["status"] == "FAIL":
            print(f"\n  ⚠️  {info['label']} is failing: {info['msg']}")
            print("  Options: (1) fix the key now  (2) manual mode  (3) skip entirely")
            choice = input("  Choice [2]: ").strip() or "2"
            if choice == "1":
                new_val = input(f"  Enter new value for {key.upper()}_API_KEY (or path): ").strip()
                # Update the .env file
                if env_path and os.path.isfile(env_path):
                    with open(env_path, "r") as f:
                        content = f.read()
                    import re
                    env_key = key.upper() + "_API_KEY"
                    if env_key in content:
                        content = re.sub(f"{env_key}=.*", f"{env_key}={new_val}", content)
                    else:
                        content += f"\n{env_key}={new_val}"
                    with open(env_path, "w") as f:
                        f.write(content)
                    os.environ[env_key] = new_val
                    print(f"  Updated {env_key}. Re-run init_session.py to re-test.")
            elif choice == "3":
                results[key]["status"] = "SKIPPED"

    # 4. Collect session details
    print("\n[4/5] Session configuration")
    client_name = input("  Client name (for file naming, e.g. YoCrunch): ").strip()
    site_url    = input("  Site URL (e.g. https://www.example.com): ").strip()
    today       = datetime.date.today().strftime("%B %Y")
    audit_date  = input(f"  Audit date [{today}]: ").strip() or today

    # API mode selections
    print("\n  Data source modes:")
    api_modes = {}
    source_map = [
        ("screaming_frog", "Screaming Frog crawl data"),
        ("se_ranking",     "SE Ranking AI/GEO data"),
        ("majestic",       "Majestic backlink data"),
        ("psi",            "PageSpeed Insights"),
        ("gsc",            "Google Search Console"),
        ("ga4",            "Google Analytics 4"),
        ("moz",            "Moz DA/Spam Score"),
        ("whois",          "WHOIS domain data"),
    ]
    for key, label in source_map:
        if key == "se_ranking":
            api_modes[key] = se_mode_pref
            print(f"    SE Ranking: {se_mode_pref.upper()} mode (selected earlier)")
        else:
            api_modes[key] = ask_api_mode(label, results.get(key, {}).get("status", "SKIPPED"))

    # 5. Google Drive folder confirmation
    print("\n[5/5] Confirm Google Drive folders")

    gdrive_main = os.getenv("GDRIVE_MAIN_DIR_ID", "").strip()
    gdrive_exports = os.getenv("GDRIVE_EXPORTS_DIR_ID", "").strip()
    gdrive_html = os.getenv("GDRIVE_HTML_DIR_ID", "").strip()

    print("  Main deliverables folder (workbook, executive summary):")
    raw_main = input(f"  Paste folder URL or ID [{gdrive_main or 'required'}]: ").strip()
    if raw_main:
        gdrive_main = parse_folder_id(raw_main)

    print("  Export sheets folder (Phase 4 CSVs, conditional outputs):")
    raw_exports = input(f"  Paste folder URL or ID [{gdrive_exports or 'required'}]: ").strip()
    if raw_exports:
        gdrive_exports = parse_folder_id(raw_exports)

    print("  HTML reports folder (optional):")
    raw_html = input(f"  Paste folder URL or ID [{gdrive_html or 'leave blank to skip'}]: ").strip()
    if raw_html:
        gdrive_html = parse_folder_id(raw_html)

    # Validate Drive folders
    if gdrive_main and results.get("google_drive", {}).get("status") == "PASS":
        ok, msg = validate_drive_folder(gdrive_main, "Main deliverables")
        print(f"  Drive write test — main:    {'✓ ' + msg if ok else '✗ ' + msg}")
    if gdrive_exports and results.get("google_drive", {}).get("status") == "PASS":
        ok, msg = validate_drive_folder(gdrive_exports, "Exports")
        print(f"  Drive write test — exports: {'✓ ' + msg if ok else '✗ ' + msg}")

    # Write audit-session-config.json
    config = {
        "client_name":        client_name,
        "site_url":           site_url,
        "session_date":       audit_date,
        "api_modes":          api_modes,
        "gdrive_main_dir_id":    gdrive_main,
        "gdrive_exports_dir_id": gdrive_exports,
        "gdrive_html_dir_id":    gdrive_html,
    }
    with open(CONFIG_OUTPUT, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    print(f"\n  Written: {CONFIG_OUTPUT}")

    # Summary table
    print("\n" + "=" * 60)
    print("  CONNECTION SUMMARY")
    print("=" * 60)
    print(f"  {'Service':<30} {'Status':<10} {'Mode':<10}")
    print(f"  {'-'*30} {'-'*10} {'-'*10}")
    for key, label, _ in tests:
        status = results.get(key, {}).get("status", "–")
        mode   = api_modes.get(key, "–")
        print(f"  {label:<30} {status:<10} {mode:<10}")

    print("\n" + "=" * 60)
    print(f"  Client:        {client_name}")
    print(f"  Site URL:      {site_url}")
    print(f"  Audit date:    {audit_date}")
    print(f"  Config file:   {CONFIG_OUTPUT}")
    print("=" * 60)
    print("\n  Session initialised. Proceed with Phase 0 in Claude Code.\n")


if __name__ == "__main__":
    main()
