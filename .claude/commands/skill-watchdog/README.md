# skill-watchdog

Passive monitoring layer that runs alongside any other skill. Tracks spec compliance, pipeline integrity, silent failures, and output quality. Logs findings to a session file and produces a confidence score at the end.

## What It Does

- Monitors every tool call made during skill execution
- Flags deviations from the skill spec (missing steps, wrong output format, undeclared files)
- Detects silent failures, truncation risks, and assumption drift
- Scores output confidence (0–100) across 5 dimensions
- Logs all findings to `all_skills/session-skill-logs/`
- Updates an Evolution Registry to track patterns across sessions
- Proposes and (for high-confidence changes) auto-applies spec improvements over time

## Activation

Always-on alongside any skill invocation. Also available as a standalone command:

```
# Monitor a specific skill
/skill-watchdog monthly-content-planner

# Monitor the entire session
/skill-watchdog

# View skill health dashboard
/skill-watchdog report

# Review and apply pending improvement proposals
/skill-watchdog evolve

# Run self-analysis against past sessions
/skill-watchdog metacognitive
```

## Confidence Score

| Score | Meaning |
|-------|---------|
| 90–100 | TRUSTED — output can be used as-is |
| 70–89 | REVIEW RECOMMENDED — verify before using |
| 50–69 | USE WITH CAUTION — significant issues present |
| < 50 | DO NOT USE — critical or structural failures |

## Monitored Dimensions

- Spec vs. execution (declared steps actually run)
- Pipeline integrity (outputs consumed correctly)
- Silent failure risk (errors caught without logging)
- Truncation risk (unbounded operations)
- Claude behavior (scope creep, assumption drift, repeated calls)

## Session Logs

Logs are written to `all_skills/session-skill-logs/YYYY-MM-DD_HH-MM_[skill]_watchdog.md`.

These are excluded from the git repo (runtime state). The Evolution Registry and per-skill baselines are also local-only.

## CRITICAL Hard-Stop

If a critical issue is detected (e.g. overwriting an unread file, runaway loop, empty required output), the watchdog halts execution and presents recovery options before allowing continuation.
