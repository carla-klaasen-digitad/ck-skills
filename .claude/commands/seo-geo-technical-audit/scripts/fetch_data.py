"""
fetch_data.py  —  seo-geo-technical-audit-v13
==============================================
Fetches data from connected APIs to replace manual CSV/PDF exports.
Called by Claude Code during Phase 0 when a data file is missing and
the corresponding API is configured in audit-session-config.json.

    python3 scripts/fetch_data.py --source [source_name] --domain [domain] --output [path]

SOURCES
-------
Run with --list-sources to see all available sources.

SE RANKING NOTE
---------------
When se_ranking mode is "mcp" in audit-session-config.json, SE Ranking
sources are skipped here — Claude Code handles them interactively via the
MCP connection. When mode is "api", this script fetches them directly.

REQUIREMENTS
------------
  pip install requests python-dotenv
  (google-analytics-data required only for ga4 sources)
"""

import argparse
import csv
import json
import os
import sys

# Resolve skill root from scripts/ location
SKILL_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(SKILL_ROOT, "audit-session-config.json")

# Add scripts/ to path for api_clients import
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import api_clients

# ── CONFIG LOADING ────────────────────────────────────────────────────────────
def load_config():
    if not os.path.isfile(CONFIG_PATH):
        sys.exit(
            f"ERROR: audit-session-config.json not found at {CONFIG_PATH}\n"
            "Run python3 scripts/init_session.py first."
        )
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def check_mode(config, api_key):
    """Return the configured mode string, or 'manual' if not set."""
    return config.get("api_modes", {}).get(api_key, "manual")


# ── SCREAMING FROG HELPERS ────────────────────────────────────────────────────
SF_SOURCES = {
    "sf-4xx":           ("response_codes", {"filter": "4xx"}),
    "sf-3xx":           ("response_codes", {"filter": "3xx"}),
    "sf-titles":        ("page_titles",    {}),
    "sf-meta":          ("meta_description", {}),
    "sf-h1":            ("h1",             {}),
    "sf-h2":            ("h2",             {}),
    "sf-alt":           ("images",         {"filter": "missing_alt"}),
    "sf-canonicals":    ("canonicals",     {"filter": "canonicalised"}),
    "sf-internal-links":("internal",       {}),
    "sf-external-urls": ("external_urls",  {}),
    "sf-schema":        ("structured_data", {}),
    "sf-urls":          ("urls",           {}),
    "sf-mixed":         ("security",       {"filter": "mixed_content"}),
    "sf-headers":       ("response_headers", {}),
    "sf-content-all":   ("content",        {}),
}

def fetch_sf(source, domain, output_path, config):
    if check_mode(config, "screaming_frog") == "manual":
        print(f"Source '{source}' is configured for manual mode — skipping API fetch.")
        print(f"Upload the corresponding Screaming Frog CSV export manually.")
        sys.exit(0)

    endpoint, params = SF_SOURCES[source]
    sf_url = os.getenv("SF_API_URL", "http://localhost:8775/").rstrip("/")
    import requests

    # Initiate crawl if domain provided and not yet crawled
    # (SF API auto-uses the last crawl if SF is already open with results)
    url = f"{sf_url}/{endpoint}"
    params["format"] = "csv"
    if domain:
        params["crawl_url"] = domain

    print(f"Fetching {source} for {domain}...")
    try:
        r = requests.get(url, params=params, timeout=60)
        r.raise_for_status()
    except Exception as e:
        print(f"ERROR: Screaming Frog API call failed: {e}")
        sys.exit(1)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(r.text)
    print(f"Written to {output_path}")


# ── SE RANKING HELPERS ────────────────────────────────────────────────────────
def fetch_se_ranking_aio(domain, output_path, config):
    mode = check_mode(config, "se_ranking")
    if mode == "mcp":
        print("SE Ranking is in MCP mode — use the SE Ranking MCP connection in Claude Code.")
        print("Claude will fetch AI Overview data interactively during the audit session.")
        sys.exit(0)
    if mode == "manual":
        print("SE Ranking is in manual mode — export se-ranking-aio.csv from SE Ranking manually.")
        sys.exit(0)

    import requests
    client = api_clients.get_se_ranking_client()
    print(f"Fetching SE Ranking AI Overview data for {domain}...")
    try:
        # SE Ranking API endpoint for AI Overview / SERP data
        r = client.get(
            "https://api4.seranking.com/research/us/summary/",
            params={"domain": domain},
            timeout=30,
        )
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        print(f"ERROR: SE Ranking API call failed: {e}")
        sys.exit(1)

    rows = []
    for item in data.get("keywords", []):
        rows.append({
            "Keyword":            item.get("keyword", ""),
            "AI Overview Present": "Yes" if item.get("ai_overview") else "No",
            "AI Overview Snippet": item.get("ai_overview_snippet", ""),
            "Position in AIO":    item.get("ai_overview_position", ""),
            "Date":               item.get("date", ""),
        })

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["Keyword", "AI Overview Present",
                                               "AI Overview Snippet", "Position in AIO", "Date"])
        writer.writeheader()
        writer.writerows(rows)
    print(f"Written to {output_path}")


def fetch_se_ranking_aivisibility(domain, output_path, config):
    mode = check_mode(config, "se_ranking")
    if mode == "mcp":
        print("SE Ranking is in MCP mode — use the SE Ranking MCP connection in Claude Code.")
        print("Claude will fetch AI Visibility data interactively during the audit session.")
        sys.exit(0)
    if mode == "manual":
        print("SE Ranking is in manual mode — export se-ranking-aivisibility.csv manually.")
        sys.exit(0)

    import requests
    client = api_clients.get_se_ranking_client()
    print(f"Fetching SE Ranking AI Visibility data for {domain}...")
    try:
        r = client.get(
            "https://api4.seranking.com/research/us/ai-visibility/",
            params={"domain": domain},
            timeout=30,
        )
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        print(f"ERROR: SE Ranking API call failed: {e}")
        sys.exit(1)

    rows = []
    for item in data.get("results", []):
        rows.append({
            "Keyword":        item.get("keyword", ""),
            "Platform":       item.get("platform", ""),
            "Mentioned":      "Yes" if item.get("mentioned") else "No",
            "Citation URL":   item.get("citation_url", ""),
            "Visibility Score": item.get("visibility_score", ""),
            "Date":           item.get("date", ""),
        })

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["Keyword", "Platform", "Mentioned",
                                               "Citation URL", "Visibility Score", "Date"])
        writer.writeheader()
        writer.writerows(rows)
    print(f"Written to {output_path}")


# ── PAGESPEED INSIGHTS ────────────────────────────────────────────────────────
def fetch_psi(strategy, domain, output_path, config):
    if check_mode(config, "psi") == "manual":
        print(f"PSI is in manual mode — run PageSpeed Insights manually and upload the PDF.")
        sys.exit(0)

    import requests
    api_key = os.getenv("PSI_API_KEY", "").strip()
    print(f"Fetching PageSpeed Insights ({strategy}) for {domain}...")

    params = {
        "url":      domain,
        "strategy": strategy,
    }
    if api_key:
        params["key"] = api_key

    try:
        r = requests.get(
            "https://www.googleapis.com/pagespeedonline/v5/runPagespeed",
            params=params,
            timeout=60,
        )
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        print(f"ERROR: PSI API call failed: {e}")
        sys.exit(1)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    # Save as JSON — all Lighthouse scoring fields preserved
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Written to {output_path}")

    # Print key scores for immediate reference
    cats = data.get("lighthouseResult", {}).get("categories", {})
    perf = cats.get("performance", {}).get("score", "–")
    print(f"  Performance score: {round(perf * 100) if isinstance(perf, float) else perf}")


# ── GOOGLE SEARCH CONSOLE ─────────────────────────────────────────────────────
def fetch_gsc_coverage(domain, output_path, config):
    if check_mode(config, "gsc") == "manual":
        print("GSC is in manual mode — export Coverage CSV from Google Search Console manually.")
        sys.exit(0)
    print(f"Fetching GSC Coverage data for {domain}...")
    try:
        client = api_clients.get_gsc_client()
        property_url = os.getenv("GSC_PROPERTY_URL", domain).strip()
        result = client.urlInspection().index().inspect(
            body={"inspectionUrl": property_url, "siteUrl": property_url}
        ).execute()
    except Exception as e:
        print(f"ERROR: GSC API call failed: {e}")
        sys.exit(1)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["URL", "Coverage State", "Last Crawled", "Indexing State"])
        writer.writeheader()
        idx = result.get("inspectionResult", {}).get("indexStatusResult", {})
        writer.writerow({
            "URL":             property_url,
            "Coverage State":  idx.get("verdict", ""),
            "Last Crawled":    idx.get("lastCrawlTime", ""),
            "Indexing State":  idx.get("indexingState", ""),
        })
    print(f"Written to {output_path}")


def fetch_gsc_performance(domain, output_path, config):
    if check_mode(config, "gsc") == "manual":
        print("GSC is in manual mode — export Performance CSV from Google Search Console manually.")
        sys.exit(0)
    print(f"Fetching GSC Performance data for {domain}...")
    try:
        client = api_clients.get_gsc_client()
        property_url = os.getenv("GSC_PROPERTY_URL", domain).strip()
        result = client.searchanalytics().query(
            siteUrl=property_url,
            body={
                "startDate": "2024-01-01",
                "endDate":   "2024-12-31",
                "dimensions": ["query", "page"],
                "rowLimit":  25000,
            }
        ).execute()
    except Exception as e:
        print(f"ERROR: GSC Performance API call failed: {e}")
        sys.exit(1)

    rows = result.get("rows", [])
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["query", "page", "clicks", "impressions", "ctr", "position"])
        writer.writeheader()
        for row in rows:
            writer.writerow({
                "query":       row["keys"][0] if len(row["keys"]) > 0 else "",
                "page":        row["keys"][1] if len(row["keys"]) > 1 else "",
                "clicks":      row.get("clicks", 0),
                "impressions": row.get("impressions", 0),
                "ctr":         row.get("ctr", 0),
                "position":    row.get("position", 0),
            })
    print(f"Written to {output_path} ({len(rows)} rows)")


# ── GOOGLE ANALYTICS 4 ───────────────────────────────────────────────────────
def fetch_ga4_traffic(output_path, config):
    if check_mode(config, "ga4") == "manual":
        print("GA4 is in manual mode — export Traffic Acquisition CSV from GA4 manually.")
        sys.exit(0)
    print("Fetching GA4 Traffic Acquisition data...")
    property_id = os.getenv("GA4_PROPERTY_ID", "").strip()
    if not property_id:
        print("ERROR: GA4_PROPERTY_ID not set in .env")
        sys.exit(1)
    try:
        from google.analytics.data_v1beta.types import (
            RunReportRequest, DateRange, Dimension, Metric
        )
        client = api_clients.get_ga4_client()
        request = RunReportRequest(
            property=f"properties/{property_id}",
            date_ranges=[DateRange(start_date="90daysAgo", end_date="today")],
            dimensions=[
                Dimension(name="sessionDefaultChannelGrouping"),
                Dimension(name="sessionSource"),
                Dimension(name="sessionMedium"),
            ],
            metrics=[
                Metric(name="sessions"),
                Metric(name="totalUsers"),
                Metric(name="bounceRate"),
            ],
        )
        response = client.run_report(request)
    except Exception as e:
        print(f"ERROR: GA4 API call failed: {e}")
        sys.exit(1)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Channel", "Source", "Medium", "Sessions", "Users", "Bounce Rate"])
        for row in response.rows:
            writer.writerow([
                row.dimension_values[0].value,
                row.dimension_values[1].value,
                row.dimension_values[2].value,
                row.metric_values[0].value,
                row.metric_values[1].value,
                row.metric_values[2].value,
            ])
    print(f"Written to {output_path}")


# ── MOZ ───────────────────────────────────────────────────────────────────────
def fetch_moz(domain, output_path, config):
    if check_mode(config, "moz") == "manual":
        print("Moz is in manual mode — export domain overview from Moz manually.")
        sys.exit(0)
    import requests
    print(f"Fetching Moz DA/Spam Score for {domain}...")
    try:
        client = api_clients.get_moz_client()
        r = client.post(
            "https://lsapi.seomoz.com/v2/url_metrics",
            json={"targets": [f"{domain}/"]},
            timeout=20,
        )
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        print(f"ERROR: Moz API call failed: {e}")
        sys.exit(1)

    results = data.get("results", [{}])[0]
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["Domain", "DA", "Spam Score",
                                               "Inbound Links", "Linking Domains"])
        writer.writeheader()
        writer.writerow({
            "Domain":          domain,
            "DA":              results.get("domain_authority", ""),
            "Spam Score":      results.get("spam_score", ""),
            "Inbound Links":   results.get("inbound_links", ""),
            "Linking Domains": results.get("linking_domains", ""),
        })
    print(f"Written to {output_path}")


# ── MAJESTIC ─────────────────────────────────────────────────────────────────
def fetch_majestic(domain, output_path, config):
    if check_mode(config, "majestic") == "manual":
        print("Majestic is in manual mode — export backlinks data from Majestic manually.")
        sys.exit(0)
    import requests
    print(f"Fetching Majestic data for {domain}...")
    try:
        client = api_clients.get_majestic_client()
        r = requests.get(
            "https://developer.majestic.com/api/json",
            params={
                "app_api_key": client.majestic_key,
                "cmd":         "GetIndexItemInfo",
                "items":       1,
                "item0":       domain,
                "datasource":  "fresh",
            },
            timeout=20,
        )
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        print(f"ERROR: Majestic API call failed: {e}")
        sys.exit(1)

    item = data.get("DataTables", {}).get("Results", {}).get("Data", [{}])[0]
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["Referring Domain", "Trust Flow",
                                               "Citation Flow", "Backlinks",
                                               "Domain", "RefDomains"])
        writer.writeheader()
        writer.writerow({
            "Referring Domain": domain,
            "Trust Flow":       item.get("TrustFlow", ""),
            "Citation Flow":    item.get("CitationFlow", ""),
            "Backlinks":        item.get("ExtBackLinks", ""),
            "Domain":           item.get("Domain", domain),
            "RefDomains":       item.get("RefDomains", ""),
        })
    print(f"Written to {output_path}")


# ── WHOIS ─────────────────────────────────────────────────────────────────────
def fetch_whois(domain, output_path, config):
    if check_mode(config, "whois") == "manual":
        print("WHOIS is in manual mode — copy WHOIS data to whois.txt manually.")
        sys.exit(0)
    import requests
    print(f"Fetching WHOIS data for {domain}...")
    try:
        client = api_clients.get_whois_client()
        r = requests.get(
            "https://www.whoisxmlapi.com/whoisserver/WhoisService",
            params={
                "domainName":  domain,
                "apiKey":      client.whois_key,
                "outputFormat": "JSON",
            },
            timeout=20,
        )
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        print(f"ERROR: WHOIS API call failed: {e}")
        sys.exit(1)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    record = data.get("WhoisRecord", {})
    result = {
        "domain":        record.get("domainName", domain),
        "creation_date": record.get("createdDate", ""),
        "expiry_date":   record.get("expiresDate", ""),
        "registrar":     record.get("registrarName", ""),
        "registrant":    record.get("registrant", {}).get("organization", ""),
    }
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"Written to {output_path}")
    print(f"  Domain:   {result['domain']}")
    print(f"  Created:  {result['creation_date']}")
    print(f"  Expires:  {result['expiry_date']}")
    print(f"  Registrar: {result['registrar']}")


# ── SOURCE DISPATCH TABLE ─────────────────────────────────────────────────────
ALL_SOURCES = list(SF_SOURCES.keys()) + [
    "se-ranking-aio", "se-ranking-aivisibility",
    "psi-desktop", "psi-mobile",
    "gsc-coverage", "gsc-performance", "gsc-mobile",
    "ga4-traffic", "ga4-events",
    "backlinks-majestic", "backlinks-moz",
    "whois",
]


# ── CLI ───────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="Fetch audit data from connected APIs — seo-geo-technical-audit v13"
    )
    parser.add_argument("--source",       required=False, help="Data source to fetch")
    parser.add_argument("--domain",       default="",     help="Target domain (e.g. example.com)")
    parser.add_argument("--output",       default="",     help="Output file path")
    parser.add_argument("--list-sources", action="store_true", help="List all available sources")
    args = parser.parse_args()

    if args.list_sources:
        print("\nAvailable sources:")
        for s in ALL_SOURCES:
            print(f"  --source {s}")
        sys.exit(0)

    if not args.source:
        parser.print_help()
        sys.exit(1)

    config = load_config()
    source = args.source
    domain = args.domain or config.get("site_url", "")
    output = args.output

    # Derive default output path from config if not given
    if not output:
        audit_dir = config.get("audit_dir", ".")
        output_csv = os.path.join(audit_dir, "Outputs", "CSV", f"{source}.csv")
        output_json = output_csv.replace(".csv", ".json")
        output = output_csv

    print(f"\nfetch_data.py — source: {source} — domain: {domain}")

    # Screaming Frog sources
    if source in SF_SOURCES:
        fetch_sf(source, domain, output, config)

    # SE Ranking
    elif source == "se-ranking-aio":
        fetch_se_ranking_aio(domain, output, config)
    elif source == "se-ranking-aivisibility":
        fetch_se_ranking_aivisibility(domain, output, config)

    # PageSpeed Insights
    elif source == "psi-desktop":
        fetch_psi("desktop", domain, output.replace(".csv", ".json"), config)
    elif source == "psi-mobile":
        fetch_psi("mobile", domain, output.replace(".csv", ".json"), config)

    # GSC
    elif source == "gsc-coverage":
        fetch_gsc_coverage(domain, output, config)
    elif source == "gsc-performance":
        fetch_gsc_performance(domain, output, config)
    elif source == "gsc-mobile":
        # GSC Core Web Vitals — fetch coverage and filter for CWV data
        fetch_gsc_coverage(domain, output, config)

    # GA4
    elif source in ("ga4-traffic", "ga4-events"):
        fetch_ga4_traffic(output, config)

    # Backlinks
    elif source == "backlinks-majestic":
        fetch_majestic(domain, output, config)
    elif source == "backlinks-moz":
        fetch_moz(domain, output, config)

    # WHOIS
    elif source == "whois":
        fetch_whois(domain, output.replace(".csv", ".json"), config)

    else:
        print(f"ERROR: Unknown source '{source}'. Run --list-sources to see options.")
        sys.exit(1)


if __name__ == "__main__":
    main()
