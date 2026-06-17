"""
api_clients.py  —  seo-geo-technical-audit-v13
===============================================
Shared module — exposes initialised API client objects for all connected
services. Imported by init_session.py, fetch_data.py, generate_gsheet.py,
and upload_exports.py. Do not run directly.

All functions load ~/.config/digitad/.env first (fallback to local .env at
the skill root). A RuntimeError is raised if a required key is missing.

SE RANKING NOTE
---------------
This module provides a REST API client for automated scripted fetches
(used by fetch_data.py). The SE Ranking MCP connection available in Claude
Code handles interactive use during audit sessions — no Python client is
needed for that path. The se_ranking mode in audit-session-config.json
controls which approach is active for a given session.
"""

import os
import requests
from dotenv import load_dotenv

# ── ENV LOADING ───────────────────────────────────────────────────────────────
_ENV_PRIMARY = os.path.expanduser("~/.config/digitad/.env")
_ENV_FALLBACK = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")

def _load_env():
    """Load .env from ~/.config/digitad/.env, falling back to skill root .env."""
    if os.path.isfile(_ENV_PRIMARY):
        load_dotenv(_ENV_PRIMARY)
        return _ENV_PRIMARY
    elif os.path.isfile(_ENV_FALLBACK):
        load_dotenv(_ENV_FALLBACK)
        return _ENV_FALLBACK
    else:
        load_dotenv()  # last resort — current directory
        return "current directory"

_ENV_PATH = _load_env()


def get_env_path():
    """Return the path of the .env file that was loaded."""
    return _ENV_PATH


def _require(key):
    """Return env var value, raising RuntimeError if absent or empty."""
    val = os.getenv(key, "").strip()
    if not val:
        raise RuntimeError(
            f"Required environment variable '{key}' is missing or empty. "
            f"Check {_ENV_PATH} and ensure the key is populated."
        )
    return val


# ── SCREAMING FROG ────────────────────────────────────────────────────────────
def get_sf_client():
    """
    Returns a requests.Session pre-configured for the Screaming Frog API.
    SF API runs locally — no authentication key required.
    SF must be running with API enabled: Preferences > API > Enable REST API.
    """
    sf_url = os.getenv("SF_API_URL", "http://localhost:8775/").strip()
    session = requests.Session()
    session.base_url = sf_url
    return session


# ── SE RANKING ────────────────────────────────────────────────────────────────
def get_se_ranking_client():
    """
    Returns a requests.Session with SE Ranking Authorization header set.
    Used by fetch_data.py for automated pulls (API mode).
    For interactive use during audits, use the SE Ranking MCP connection
    in Claude Code instead — no Python client needed for that path.
    """
    api_key = _require("SE_RANKING_API_KEY")
    session = requests.Session()
    session.headers.update({"Authorization": f"Token {api_key}"})
    return session


# ── MAJESTIC ─────────────────────────────────────────────────────────────────
def get_majestic_client():
    """Returns a requests.Session with the Majestic API key accessible."""
    api_key = _require("MAJESTIC_API_KEY")
    session = requests.Session()
    session.majestic_key = api_key
    return session


# ── GOOGLE SERVICE ACCOUNT (Sheets / Drive / Docs) ───────────────────────────
def _get_google_credentials(scopes):
    """Build Google credentials — prefers OAuth2 token (GOOGLE_TOKEN_FILE) over service account."""
    token_file = os.getenv("GOOGLE_TOKEN_FILE", "").strip()
    if token_file and os.path.isfile(token_file):
        from google.oauth2.credentials import Credentials
        return Credentials.from_authorized_user_file(token_file, scopes)
    from google.oauth2.service_account import Credentials as SACredentials
    sa_path = _require("GOOGLE_SERVICE_ACCOUNT_JSON")
    if not os.path.isfile(sa_path):
        raise RuntimeError(
            f"Google service account JSON not found at: {sa_path}\n"
            f"Update GOOGLE_SERVICE_ACCOUNT_JSON in {_ENV_PATH}."
        )
    return SACredentials.from_service_account_file(sa_path, scopes=scopes)


def get_google_sheets_client():
    """
    Returns an authenticated gspread client.
    Requires: google-auth, gspread, GOOGLE_SERVICE_ACCOUNT_JSON in .env.
    """
    import gspread
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = _get_google_credentials(scopes)
    return gspread.authorize(creds)


def get_google_drive_client():
    """
    Returns a Google Drive API v3 service object (googleapiclient).
    Requires: google-api-python-client, GOOGLE_SERVICE_ACCOUNT_JSON in .env.
    """
    from googleapiclient.discovery import build
    scopes = [
        "https://www.googleapis.com/auth/drive",
        "https://www.googleapis.com/auth/drive.file",
    ]
    creds = _get_google_credentials(scopes)
    return build("drive", "v3", credentials=creds)


def get_google_docs_client():
    """
    Returns a Google Docs API v1 service object (googleapiclient).
    Requires: google-api-python-client, GOOGLE_SERVICE_ACCOUNT_JSON in .env.
    """
    from googleapiclient.discovery import build
    scopes = [
        "https://www.googleapis.com/auth/documents",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = _get_google_credentials(scopes)
    return build("docs", "v1", credentials=creds)


def get_google_sheets_service():
    """
    Returns a Google Sheets API v4 service object (googleapiclient).
    Used for batchUpdate formatting operations not available via gspread.
    """
    from googleapiclient.discovery import build
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = _get_google_credentials(scopes)
    return build("sheets", "v4", credentials=creds)


# ── PAGESPEED INSIGHTS ────────────────────────────────────────────────────────
def get_psi_client():
    """
    Returns a requests.Session with PSI API key accessible as session.psi_key.
    PSI API key improves rate limits but is not strictly required for single-URL tests.
    """
    api_key = _require("PSI_API_KEY")
    session = requests.Session()
    session.psi_key = api_key
    return session


# ── GOOGLE SEARCH CONSOLE ─────────────────────────────────────────────────────
def get_gsc_client():
    """
    Returns a GSC API service object using OAuth2 user credentials.
    Requires GSC_CLIENT_SECRETS_JSON — a service account cannot be used unless
    it has been added as a verified user in the GSC property.
    """
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    import pickle

    secrets_path = _require("GSC_CLIENT_SECRETS_JSON")
    if not os.path.isfile(secrets_path):
        raise RuntimeError(
            f"GSC client secrets JSON not found at: {secrets_path}\n"
            f"Update GSC_CLIENT_SECRETS_JSON in {_ENV_PATH}."
        )
    scopes = ["https://www.googleapis.com/auth/webmasters.readonly"]
    token_path = os.path.join(os.path.dirname(secrets_path), "gsc_token.pickle")
    creds = None

    if os.path.isfile(token_path):
        with open(token_path, "rb") as f:
            creds = pickle.load(f)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(secrets_path, scopes)
            creds = flow.run_local_server(port=0)
        with open(token_path, "wb") as f:
            pickle.dump(creds, f)

    return build("searchconsole", "v1", credentials=creds)


# ── GOOGLE ANALYTICS 4 ───────────────────────────────────────────────────────
def get_ga4_client():
    """
    Returns a GA4 Data API service object.
    Uses the same service account as Sheets/Drive — the SA must have Viewer
    access in the GA4 property (grant it under Admin > Property Access Management).
    """
    from google.analytics.data_v1beta import BetaAnalyticsDataClient
    sa_path = _require("GOOGLE_SERVICE_ACCOUNT_JSON")
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = sa_path
    return BetaAnalyticsDataClient()


# ── MOZ ───────────────────────────────────────────────────────────────────────
def get_moz_client():
    """
    Returns a requests.Session configured for Moz Links API v2 with HMAC auth.
    Endpoint: https://lsapi.seomoz.com/v2/url_metrics
    """
    import base64
    access_id = _require("MOZ_ACCESS_ID")
    secret_key = _require("MOZ_SECRET_KEY")
    token = base64.b64encode(f"{access_id}:{secret_key}".encode()).decode()
    session = requests.Session()
    session.headers.update({
        "Authorization": f"Basic {token}",
        "Content-Type": "application/json",
    })
    return session


# ── WHOIS XML API ─────────────────────────────────────────────────────────────
def get_whois_client():
    """
    Returns a requests.Session with the WHOIS XML API key accessible.
    Endpoint: https://www.whoisxmlapi.com/whoisserver/WhoisService
    """
    api_key = _require("WHOIS_API_KEY")
    session = requests.Session()
    session.whois_key = api_key
    return session
