#!/usr/bin/env python3
"""
Neuronwriter API helper for the monthly-content-planner skill.
Usage:
  python neuronwriter_api.py create_analysis <project_id> <keyword> <country> <language> [secondary_kws_comma_sep]
  python neuronwriter_api.py update_meta <analysis_id> <title> <keyword> [secondary_kws_comma_sep]

Returns JSON with analysis_url and analysis_id on create_analysis.
"""

import sys
import os
import json
import time
import warnings
warnings.filterwarnings("ignore")

from dotenv import load_dotenv
load_dotenv("/Users/carlaklaasen/claude_code/.env")

try:
    import requests
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests", "-q"])
    import requests

API_KEY = os.getenv("NEURONWRITER_API_KEY", "")
BASE_URL = "https://app.neuronwriter.com/api/rest"

HEADERS = {
    "X-API-KEY": API_KEY,
    "Content-Type": "application/json",
}


def create_analysis(project_id: str, keyword: str, country: str, language: str, secondary_kws=None) -> dict:
    """
    Create a new analysis (query) in a NW project.
    Returns {"analysis_id": "...", "analysis_url": "..."}.
    """
    payload = {
        "project": project_id,
        "query": keyword,
        "country": country,
        "language": language,
    }
    if secondary_kws:
        payload["competitors_type"] = "auto"

    resp = requests.post(f"{BASE_URL}/query/add", headers=HEADERS, json=payload, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    # NW returns {"status": "ok", "query_id": "...", ...} or similar
    if data.get("status") != "ok" and "query_id" not in data:
        raise RuntimeError(f"NW create_analysis failed: {data}")

    query_id = data.get("query_id") or data.get("id") or data.get("data", {}).get("query_id")
    if not query_id:
        raise RuntimeError(f"NW create_analysis: could not find query_id in response: {data}")

    analysis_url = f"https://app.neuronwriter.com/analysis/view/{query_id}"
    return {"analysis_id": query_id, "analysis_url": analysis_url}


def update_meta(analysis_id: str, title: str, keyword: str, secondary_kws=None) -> dict:
    """
    Update an existing NW analysis with title, target keyword, and secondary keywords.
    Returns {"status": "ok"} or raises.
    """
    payload = {
        "query_id": analysis_id,
        "title": title,
        "keyword": keyword,
    }
    if secondary_kws:
        payload["secondary_keywords"] = secondary_kws

    resp = requests.post(f"{BASE_URL}/query/update", headers=HEADERS, json=payload, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    if data.get("status") != "ok":
        raise RuntimeError(f"NW update_meta failed: {data}")
    return data


def wait_for_analysis_ready(analysis_id: str, max_wait: int = 120) -> dict:
    """
    Poll the NW API until the analysis is fully processed or timeout.
    Returns {"status": "ready", "analysis_id": "...", "analysis_url": "..."}.
    """
    analysis_url = f"https://app.neuronwriter.com/analysis/view/{analysis_id}"
    elapsed = 0
    interval = 10

    while elapsed < max_wait:
        resp = requests.get(
            f"{BASE_URL}/query/get",
            headers=HEADERS,
            params={"query_id": analysis_id},
            timeout=30,
        )
        if resp.status_code == 200:
            data = resp.json()
            state = data.get("status") or data.get("state") or ""
            if state in ("ready", "done", "completed", "ok"):
                return {"status": "ready", "analysis_id": analysis_id, "analysis_url": analysis_url}
            if state in ("error", "failed"):
                raise RuntimeError(f"NW analysis failed with state: {state}")

        time.sleep(interval)
        elapsed += interval

    # Return optimistically — the URL exists even if analysis is still processing
    return {"status": "processing", "analysis_id": analysis_id, "analysis_url": analysis_url}


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""

    if cmd == "create_analysis":
        # create_analysis <project_id> <keyword> <country> <language> [secondary_kws_comma]
        project_id = sys.argv[2]
        keyword = sys.argv[3]
        country = sys.argv[4] if len(sys.argv) > 4 else "us"
        language = sys.argv[5] if len(sys.argv) > 5 else "en"
        sec_raw = sys.argv[6] if len(sys.argv) > 6 else ""
        secondary = [k.strip() for k in sec_raw.split(",") if k.strip()] if sec_raw else []

        result = create_analysis(project_id, keyword, country, language, secondary)
        # Brief processing pause before returning URL
        time.sleep(3)
        print(json.dumps(result))

    elif cmd == "update_meta":
        # update_meta <analysis_id> <title> <keyword> [secondary_kws_comma]
        analysis_id = sys.argv[2]
        title = sys.argv[3]
        keyword = sys.argv[4]
        sec_raw = sys.argv[5] if len(sys.argv) > 5 else ""
        secondary = [k.strip() for k in sec_raw.split(",") if k.strip()] if sec_raw else []

        result = update_meta(analysis_id, title, keyword, secondary)
        print(json.dumps(result))

    elif cmd == "wait_ready":
        # wait_ready <analysis_id> [max_wait_seconds]
        analysis_id = sys.argv[2]
        max_wait = int(sys.argv[3]) if len(sys.argv) > 3 else 120
        result = wait_for_analysis_ready(analysis_id, max_wait)
        print(json.dumps(result))

    else:
        print("Unknown command. Use: create_analysis | update_meta | wait_ready", file=sys.stderr)
        sys.exit(1)
