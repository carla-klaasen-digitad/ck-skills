"""
activity_log.py  —  seo-geo-technical-audit-v6
================================================
Parses the Claude Code session JSONL and generates a full audit activity log
.md file covering: chronological user actions, token usage by time block,
processing durations, files generated, and session totals.

Run this at the end of an audit session (or on demand at any point).

HOW TO USE
----------
1. Find your session ID:
   - Run: ls ~/.claude/projects/<project-slug>/
   - The session ID is the .jsonl filename without the extension
   - e.g. d98a5eeb-90b4-45a1-83bb-291f5ee6874a

2. Set CLIENT_NAME, AUDIT_DATE, AUDIT_DIR, and SESSION_ID below.

3. Run: python3 activity_log.py

The output file is written to:
  {AUDIT_DIR}/Outputs/{CLIENT_NAME} - Audit Activity Log - {AUDIT_DATE}.md

FINDING YOUR PROJECT SLUG
--------------------------
The project slug maps from your AUDIT_DIR path. Example:
  /Users/jane/claude_code/acme_audit  →  -Users-jane-claude_code-acme_audit
List all project slugs with:
  ls ~/.claude/projects/

REQUIREMENTS
------------
  Python 3.7+ (stdlib only — no pip installs needed)
"""

import json
import os
import re
from collections import defaultdict
from datetime import datetime, timezone

# ── CLIENT CONFIGURATION ─────────────────────────────────────────────────────
AUDIT_DIR   = "/path/to/client/audit/directory"
CLIENT_NAME = "Client Name"
AUDIT_DATE  = "Month YYYY"

# Session ID: the .jsonl filename (without .jsonl extension) found at:
#   ~/.claude/projects/<project-slug>/<SESSION_ID>.jsonl
SESSION_ID  = "paste-session-id-here"

# ── PATHS ─────────────────────────────────────────────────────────────────────
HOME        = os.path.expanduser("~")
PROJECTS    = os.path.join(HOME, ".claude", "projects")
OUT_MD      = os.path.join(
    AUDIT_DIR, "Outputs",
    f"{CLIENT_NAME} - Audit Activity Log - {AUDIT_DATE}.md"
)

# ── HELPERS ───────────────────────────────────────────────────────────────────
def find_jsonl(session_id):
    """
    Search all project directories for a .jsonl matching the session ID.
    Returns the full path or raises FileNotFoundError.
    """
    for project_slug in os.listdir(PROJECTS):
        candidate = os.path.join(PROJECTS, project_slug, f"{session_id}.jsonl")
        if os.path.isfile(candidate):
            return candidate
    raise FileNotFoundError(
        f"Session JSONL not found for ID: {session_id}\n"
        f"Searched under: {PROJECTS}\n"
        f"Check SESSION_ID is correct and the session exists."
    )


def fmt_ts(ts):
    """ISO timestamp → readable UTC string."""
    if not ts:
        return ""
    try:
        dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d %H:%M UTC")
    except Exception:
        return ts[:16]


def load_events(jsonl_path):
    events = []
    with open(jsonl_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return events


def extract_user_messages(events):
    """Return list of (timestamp, text) for real human messages only."""
    msgs = []
    for e in events:
        if e.get("type") != "user" or e.get("isSidechain"):
            continue
        content = e.get("message", {}).get("content", "")
        if isinstance(content, list):
            text = " ".join(
                c.get("text", "") for c in content
                if isinstance(c, dict) and c.get("type") == "text"
            ).strip()
        else:
            text = str(content).strip()
        # Skip empty, tool results, compact commands, and interruptions
        if (not text
                or len(text) <= 3
                or text.startswith("[Request interrupted")
                or "<local-command" in text
                or "<command-name>" in text
                or "<command-stdout>" in text):
            continue
        # Truncate context-summary injections (these are very long)
        if text.startswith("This session is being continued from a previous"):
            text = "[Context reset — session summary injected]"
        msgs.append((e.get("timestamp", ""), text))
    return msgs


def extract_token_buckets(events):
    """
    Aggregate token usage by minute bucket.
    Returns dict of { 'YYYY-MM-DD HH:MM UTC': {input, output, cache_write, cache_read, calls} }
    """
    buckets = defaultdict(lambda: {"input": 0, "output": 0, "cache_write": 0, "cache_read": 0, "calls": 0})
    for e in events:
        if e.get("type") != "assistant" or e.get("isSidechain"):
            continue
        usage = e.get("message", {}).get("usage", {})
        if not usage:
            continue
        i  = usage.get("input_tokens", 0)
        o  = usage.get("output_tokens", 0)
        cw = usage.get("cache_creation_input_tokens", 0)
        cr = usage.get("cache_read_input_tokens", 0)
        if i + o + cw + cr == 0:
            continue
        ts = e.get("timestamp", "")
        try:
            dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
            bucket = dt.strftime("%Y-%m-%d %H:%M UTC")
        except Exception:
            bucket = ts[:16]
        buckets[bucket]["input"]       += i
        buckets[bucket]["output"]      += o
        buckets[bucket]["cache_write"] += cw
        buckets[bucket]["cache_read"]  += cr
        buckets[bucket]["calls"]       += 1
    return buckets


def extract_durations(events):
    """Return list of (timestamp, duration_seconds) for timed turns."""
    durations = []
    for e in events:
        if e.get("type") == "system" and e.get("subtype") == "turn_duration":
            durations.append((e.get("timestamp", ""), e.get("durationMs", 0) / 1000))
    return durations


def compute_totals(events):
    total_input = total_output = total_cw = total_cr = 0
    for e in events:
        if e.get("type") != "assistant" or e.get("isSidechain"):
            continue
        usage = e.get("message", {}).get("usage", {})
        if usage:
            total_input  += usage.get("input_tokens", 0)
            total_output += usage.get("output_tokens", 0)
            total_cw     += usage.get("cache_creation_input_tokens", 0)
            total_cr     += usage.get("cache_read_input_tokens", 0)
    assistant_turns = sum(
        1 for e in events
        if e.get("type") == "assistant" and not e.get("isSidechain")
        and e.get("message", {}).get("usage")
    )
    user_turns = len(extract_user_messages(events))
    total_dur = sum(
        e.get("durationMs", 0) / 1000
        for e in events
        if e.get("type") == "system" and e.get("subtype") == "turn_duration"
    )
    all_ts = sorted(e.get("timestamp", "") for e in events if e.get("timestamp"))
    session_start = fmt_ts(all_ts[0])  if all_ts else "—"
    session_end   = fmt_ts(all_ts[-1]) if all_ts else "—"
    return {
        "input": total_input, "output": total_output,
        "cache_write": total_cw, "cache_read": total_cr,
        "total": total_input + total_output + total_cw + total_cr,
        "assistant_turns": assistant_turns, "user_turns": user_turns,
        "active_s": total_dur,
        "session_start": session_start, "session_end": session_end,
    }


def top_output_turns(events, n=10):
    """Return the N turns with highest output token count."""
    turns = []
    for e in events:
        if e.get("type") != "assistant" or e.get("isSidechain"):
            continue
        usage = e.get("message", {}).get("usage", {})
        o = usage.get("output_tokens", 0) if usage else 0
        if o > 0:
            turns.append((o, e.get("timestamp", "")))
    turns.sort(reverse=True)
    return turns[:n]


def count_context_resets(events):
    resets = 0
    for e in events:
        if e.get("type") != "user" or e.get("isSidechain"):
            continue
        content = e.get("message", {}).get("content", "")
        if isinstance(content, str) and "This session is being continued from a previous" in content:
            resets += 1
    return resets


# ── REPORT BUILDER ────────────────────────────────────────────────────────────
def build_report(events, session_id):
    totals      = compute_totals(events)
    user_msgs   = extract_user_messages(events)
    buckets     = extract_token_buckets(events)
    durations   = extract_durations(events)
    top_turns   = top_output_turns(events)
    resets      = count_context_resets(events)

    h, m = divmod(int(totals["active_s"]), 3600)
    m, s = divmod(m, 60)
    active_fmt = f"{h}h {m}m {s}s" if h else f"{m}m {s}s"

    lines = []
    a = lines.append

    # ── Header
    a(f"# {CLIENT_NAME} — Audit Activity Log — {AUDIT_DATE}")
    a("")
    a(f"Session ID: `{session_id}`")
    a(f"Model: claude-sonnet-4-6")
    a("")
    a("---")
    a("")

    # ── Session Overview
    a("## Session Overview")
    a("")
    a("| Field | Value |")
    a("|---|---|")
    a(f"| Start | {totals['session_start']} |")
    a(f"| End   | {totals['session_end']} |")
    a(f"| Active processing time | {active_fmt} ({int(totals['active_s'])}s across {len(durations)} timed turns) |")
    a(f"| Context resets | {resets} |")
    a(f"| User turns | {totals['user_turns']} |")
    a(f"| Assistant turns | {totals['assistant_turns']} |")
    a("")
    a("---")
    a("")

    # ── Token Usage
    a("## Token Usage")
    a("")
    a("| Category | Tokens |")
    a("|---|---|")
    a(f"| Input (new) | {totals['input']:,} |")
    a(f"| Output | {totals['output']:,} |")
    a(f"| Cache writes | {totals['cache_write']:,} |")
    a(f"| Cache reads | {totals['cache_read']:,} |")
    a(f"| **Total processed** | **{totals['total']:,}** |")
    a("")
    a("> Cache reads are billed at a significantly lower rate than input tokens.")
    a("> Output tokens reflect the volume of generated content (phase files, reports, scripts).")
    a("")
    a("---")
    a("")

    # ── User Message Timeline
    a("## User Message Timeline")
    a("")
    a("Chronological record of all user inputs during the session.")
    a("")
    a("| Time (UTC) | Message (truncated to 300 chars) |")
    a("|---|---|")
    for ts, text in user_msgs:
        safe = text[:300].replace("|", "\\|").replace("\n", " ")
        a(f"| {fmt_ts(ts)} | {safe} |")
    a("")
    a("---")
    a("")

    # ── Token Usage by Minute
    a("## Token Usage by Minute")
    a("")
    a("Each row = one clock minute with at least one assistant response.")
    a("")
    a("| Time (UTC) | Calls | Input | Output | Cache Write | Cache Read |")
    a("|---|---|---|---|---|---|")
    for bucket in sorted(buckets.keys()):
        b = buckets[bucket]
        a(f"| {bucket} | {b['calls']} | {b['input']:,} | {b['output']:,} | {b['cache_write']:,} | {b['cache_read']:,} |")
    a("")
    a("---")
    a("")

    # ── Turn Durations
    a("## Turn Durations")
    a("")
    a("Timed turns only (system turn_duration events). Excludes sub-second tool calls.")
    a("")
    a("| Time (UTC) | Duration |")
    a("|---|---|")
    for ts, secs in durations:
        if secs >= 3600:
            dur_str = f"{secs/3600:.1f}h"
        elif secs >= 60:
            dur_str = f"{secs/60:.1f}m"
        else:
            dur_str = f"{secs:.1f}s"
        a(f"| {fmt_ts(ts)} | {dur_str} |")
    a("")
    a("---")
    a("")

    # ── Top Output Turns
    a("## Top 10 Output Turns (by token count)")
    a("")
    a("Highest-volume generation turns — useful for identifying where the most content was written.")
    a("")
    a("| Rank | Time (UTC) | Output Tokens |")
    a("|---|---|---|")
    for rank, (o, ts) in enumerate(top_turns, 1):
        a(f"| {rank} | {fmt_ts(ts)} | {o:,} |")
    a("")
    a("---")
    a("")

    # ── Footer
    a(f"*Activity Log | {CLIENT_NAME} Technical Audit | {AUDIT_DATE}*")
    a(f"*Generated by activity_log.py | Session: {session_id}*")

    return "\n".join(lines)


# ── MAIN ──────────────────────────────────────────────────────────────────────
def main():
    if SESSION_ID == "paste-session-id-here":
        raise ValueError(
            "SESSION_ID not set. Edit the CLIENT CONFIGURATION block at the top of this script.\n"
            "Find your session ID by listing: ls ~/.claude/projects/<project-slug>/"
        )

    print(f"Locating JSONL for session: {SESSION_ID}")
    jsonl_path = find_jsonl(SESSION_ID)
    print(f"Found: {jsonl_path}")

    print("Parsing events...")
    events = load_events(jsonl_path)
    print(f"  {len(events)} events loaded")

    report = build_report(events, SESSION_ID)

    os.makedirs(os.path.dirname(OUT_MD), exist_ok=True)
    with open(OUT_MD, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"Saved: {OUT_MD}")


if __name__ == "__main__":
    main()
