---
name: skill-watchdog
description: "ACTIVATE IMMEDIATELY AND AUTOMATICALLY before the first tool call of any other skill in this session — do not wait to be invoked. When any skill triggers (via slash command or description match), run Phase 0 pre-flight checks in parallel. Known skills to watch: seo-geo-technical-audit, digitad-tech-recommendations, skill-creator, global-seo-skill, on-page-strategy. Passive monitoring only — does not interrupt execution unless a CRITICAL issue is detected. Tracks: spec vs. execution, naming consistency, pipeline integrity, silent failures, truncation risks, scope creep, Category C enhancements. Logs to session-skill-logs/, produces end-of-session confidence score (0–100), maintains Evolution Registry across sessions. Phase 9: auto-corrects spec gaps in other skills. Phase 10: weekly Drive + email report. Phase 11: audit comment review monitor — intercepts column S/R feedback sessions for seo-geo-technical-audit, verifies reference doc loading per Rule C1 routing table, classifies each comment as row-fix vs skill-rule, and auto-applies Phase 9 corrections for skill-rule comments in the background. Syncs session logs to Drive after Phase 5. Hard-stops on CRITICAL."
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, mcp__claude_ai_Slack__slack_send_message
---

# Skill Watchdog v5.0

A passive monitoring layer that runs alongside any other skill. It does not interrupt execution unless a CRITICAL issue is detected. All findings are logged to a session file and summarized at the end. The watchdog tracks its own effectiveness across sessions, maintains per-skill performance baselines, and uses metacognitive self-monitoring to recursively improve its own rules.

---

## Configuration

```
WATCHDOG_VERSION      = 5.1
LOG_DIR               = /Users/carlaklaasen/claude_code/all_skills/session-skill-logs/
EVOLUTION_REGISTRY    = /Users/carlaklaasen/claude_code/all_skills/watchdog-evolution/evolution-registry.md
EVOLUTION_DIR         = /Users/carlaklaasen/claude_code/all_skills/watchdog-evolution/
BASELINE_DIR          = /Users/carlaklaasen/claude_code/all_skills/skill-baselines/
SNAPSHOT_DIR          = /Users/carlaklaasen/claude_code/all_skills/watchdog-evolution/self-snapshots/
METACOGNITIVE_LOG     = /Users/carlaklaasen/claude_code/all_skills/watchdog-evolution/metacognitive-log.md
ESCALATION_THRESHOLD  = 2      # same issue recurring N times → promote one severity level
EVOLUTION_TRIGGER     = 3      # sessions count gate for improvement proposals
BASELINE_SESSIONS_MIN = 3      # min sessions before anomaly detection activates
AUTONOMY_TIER_MAX     = 3      # max autonomy tier to act without user input (1, 2, or 3)
SNAPSHOT_RETENTION    = 10     # max self-snapshots to keep before pruning oldest
METACOGNITIVE_TRIGGER = every_3_sessions_or_regression  # auto | regression | manual | every_N_sessions_or_regression

# Drive + reporting config
DRIVE_PARENT_FOLDER_ID      = 1L9wIqvNqdeRkLQ6Y_PAuQftvif1okpwj
DRIVE_WEEKLY_REPORTS_FOLDER = watchdog-weekly-reports/
DRIVE_FEEDBACK_INBOX_FOLDER = watchdog-feedback-inbox/
DRIVE_SESSION_LOGS_FOLDER   = watchdog-session-logs/
WEEKLY_REPORT_EMAIL         = carla.klaasen@digitad.ca
WEEKLY_REPORT_SCHEDULE      = Friday 08:45 EST
FEEDBACK_WATCH_INTERVAL     = 30m   # local cron poll interval for feedback inbox

# Slack notification config
# For a DM to yourself: go to your Slack profile → click "..." → Copy member ID (starts with U)
# That member ID is your DM channel identifier (e.g. U01A2BCDE3F)
SLACK_DM_TARGET             = [your-slack-member-id]   # e.g. U01A2BCDE3F
SLACK_NOTIFICATIONS         = end-of-session            # options: disabled | critical-only | all-flags | end-of-session
```

---

## Activation

**Standard monitoring:** `/skill-watchdog [skill-name]`
Wraps the named skill's execution with full monitoring.

**Session-wide monitoring:** `/skill-watchdog`
Monitors the entire session without targeting a specific skill.

**Evolution mode:** `/skill-watchdog evolve`
Reviews pending self-improvement proposals and applies approved ones. See Phase 6.

**Health dashboard:** `/skill-watchdog report`
Reads the Evolution Registry and prints a formatted health summary across all monitored skills. See Phase 7.

**Metacognitive analysis:** `/skill-watchdog metacognitive`
Runs the watchdog's self-monitoring loop against its own past session logs. See Phase 8.

**Rollback:** `/skill-watchdog rollback [proposal-N]` or `/skill-watchdog rollback last`
Reverts a self-modification using a stored pre-snapshot. See Phase 6.4.

**Backfill:** `/skill-watchdog backfill`
Scans all session logs in LOG_DIR, detects gaps in the Evolution Registry and per-skill baselines, and retroactively writes all missing entries. Run after importing historic session logs or recovering from a WD-04 gap.

**Correct skill:** `/skill-watchdog correct [skill-name]`
Runs Phase 9 (Active Skill Correction) against the named skill. Reads that skill's session logs and baseline, classifies root causes, and either auto-applies or proposes spec corrections. See Phase 9.

**Apply feedback:** `/skill-watchdog apply-feedback`
Runs Phase 10.3 (Feedback Inbox Processing) immediately. Reads all JSON files in DRIVE_FEEDBACK_INBOX_FOLDER, applies approved changes to local skill files, and archives processed files. Normally run by local cron every FEEDBACK_WATCH_INTERVAL.

**Audit comment review:** `/skill-watchdog review-comments`
Activates Phase 11 explicitly for the current seo-geo-technical-audit comment review session. Normally auto-activated — use this command to manually trigger if Phase 11 did not auto-start.

---

## Phase 0 — Pre-flight Validation

Before any skill execution begins, run these checks. Fail fast on blockers; log warnings for concerns.

### Skill File Checks

1. Locate the skill file at `/Users/carlaklaasen/.claude/commands/[skill-name].md` or `/Users/carlaklaasen/.claude/commands/[skill-name]/SKILL.md`.
2. Verify the file exists and is readable. If not: surface `[CRITICAL]` — skill file not found, halt.
3. Parse frontmatter. Verify these fields are present and non-empty: `name`, `description`, `allowed-tools`.
4. If any required frontmatter field is missing: log `[FLAG] — CB-05: Malformed skill spec: missing field [X]`.
5. Extract `allowed-tools` list. Log any tool in `allowed-tools` that appears to be restricted in the current session: `[WARN] — Required tool [X] may be restricted`.

### Directory Checks

6. Verify `LOG_DIR` exists. Create it if not.
7. Verify `EVOLUTION_DIR` exists. Create it if not.
8. Verify `BASELINE_DIR` exists. Create it if not.
9. Verify `SNAPSHOT_DIR` exists. Create it if not.
10. Check for any paths the skill declares as output destinations. If a declared output path's parent directory does not exist: log `[WARN] — Output directory does not exist: [path]`.

### Evolution Registry Check

11. Check if `EVOLUTION_REGISTRY` exists. If not, create it using the blank template (see Evolution Registry Format section). Log `[INFO] — Evolution Registry initialized (first run)`.
12. If the registry exists, read it and extract:
    - Watchdog version recorded in registry
    - Sessions since last self-improvement proposal
    - Any high-frequency categories (fired in >75% of tracked sessions)
    - Any dead rules (0 fires in last 10 sessions)
    - Total session count

13. If the registry version differs from `WATCHDOG_VERSION`: log `[INFO] — Watchdog upgraded since last run: [old version] → [new version]`. Update the registry version field.

14. If high-frequency categories exist, surface at session start:
    ```
    [Watchdog] Heads-up: "[Category]" has triggered in N of your last M sessions. Monitoring closely.
    ```

15. If dead rules exist, surface at session start:
    ```
    [Watchdog] Note: Rule [ID] "[Rule name]" has not fired in 10 sessions. It may be over-restrictive or no longer applicable.
    ```

### 0.5 — Baseline Lookup

16. Check if `BASELINE_DIR/[skill-name].md` exists.
    - If yes: read it and extract `Sessions on record`, `All-time avg` confidence, `Most Fired Rules`, and `Anomaly Thresholds`.
    - If no: create the baseline file from the template (see Per-Skill Baseline File format). Log `[INFO] — Baseline file initialized for [skill-name] (first session for this skill)`.

17. If `Sessions on record` >= `BASELINE_SESSIONS_MIN`: anomaly detection is active. Surface:
    ```
    [Watchdog] Baseline loaded for [skill-name]:
      Avg confidence (last N sessions): N/100
      Most fired rules: [IDs]
      Anomaly thresholds: confidence < N, issues > N
      Anomaly detection: ACTIVE
    ```
    If `Sessions on record` < `BASELINE_SESSIONS_MIN`:
    ```
    [Watchdog] Baseline for [skill-name]: N session(s) on record — anomaly detection inactive until N sessions reached.
    ```

### 0.6 — Watchdog Self-Integrity Check

18. Read the SKILL.md file for the watchdog itself. Compute a lightweight checksum: line count + character count.
19. Check if `SNAPSHOT_DIR` contains any post-snapshot file. If yes: compare the checksum of the most recent post-snapshot's declared `Line count` and `Character count` against the current SKILL.md.
20. If they differ AND no apply event is recorded in the Evolution Registry for today's date: log `[FLAG] — Watchdog SKILL.md was modified outside Evolution Mode (checksum mismatch). Verify intentional.`
21. If no snapshots exist yet: log `[INFO] — No prior watchdog snapshot found (expected on first run or fresh install)`.

### Session Skill Stack Check

22. Check whether another skill is already active in this session. If so:
    - Record all active skills in the session header under `Active skills in session`
    - Tag each Output Fingerprint entry with the skill name that produced it
    - Orphan detection (PI-02) applies only to outputs tagged with the currently active skill
    - Log `[INFO] — Cross-skill session detected: [skill-A] + [skill-B]. Contamination isolation active.`

### Global Flat File Shadow Check

22b. For the primary monitored skill, check if a global flat file exists at `~/.claude/commands/[skill-name].md` (a flat `.md` file, not a folder). Do this by attempting to read `/Users/carlaklaasen/.claude/commands/[skill-name].md`.
- If it exists AND a project-level directory version also exists at `/Users/carlaklaasen/claude_code/.claude/commands/[skill-name]/SKILL.md`: log `[FLAG] — CB-05: Global flat file detected that shadows the project-level skill: ~/.claude/commands/[skill-name].md. Claude Code loads global flat files before project-level directories. The running skill may be the older global version, not the project version. Archive or remove the global flat file unless this is intentional. To fix: move the file to ~/.claude/commands/_archived/[skill-name]-archived.md`
- If no global flat file found: log `[INFO] — No global flat file conflict detected for [skill-name]`. No action needed.

### Orphaned Session Log Check

22c. Scan LOG_DIR for any session log files matching `*_[skill-name]_watchdog.md` that contain an `## End-of-Session Summary` section but have no corresponding row in the Evolution Registry's Session History table (match by date and skill name). For each such orphaned session found:
- Write the missing registry row now using the end-of-session summary data from the log file (Tier 2 auto-mitigate: WD-04).
- Log `[WARN] WD-04 auto-mitigated: orphaned session log found for [date] [skill-name] — registry row written retroactively.`

This check runs at every session start and ensures the registry stays current even when Phase 5 did not complete in a prior session.

### Formalized Session Resume

23. Before creating a new log file: check if a partial log already exists for the same skill and calendar date (format: `YYYY-MM-DD_*_[skill-name]_watchdog.md`).
24. If a partial log exists:
    - Append a `## Session Resumed — [HH:MM]` section to the existing file.
    - **Re-read the Spec Registry from the existing partial log file** — do NOT re-derive it from the skill spec. This preserves declarations made before context was lost.
    - Re-run pre-flight checks in full. Append results as a new Pre-flight table in the resumed section.
    - Do not create a new log file.
    - Log `[INFO] — Session resumed from partial log. Spec Registry restored from prior log entries (not re-derived).`

---

## Phase 1 — Session Initialization

1. Create a timestamped log file at:
   `LOG_DIR/YYYY-MM-DD_HH-MM_[skill-name]_watchdog.md`

2. Write (or append) the session header:

   ```
   # Watchdog Session: [skill-name]
   **Date:** YYYY-MM-DD HH:MM
   **Invocation:** /[full command as typed]
   **Watchdog version:** 5.0
   **Monitoring mode:** [targeted / session-wide]
   **Active skills in session:** [skill-name] [+ others if cross-skill]

   ## Session Metadata
   | Field | Value |
   |---|---|
   | watchdog_self_hash | [line_count:char_count of SKILL.md] |
   | baseline_confidence_for_skill | [N/100 or "—" if < BASELINE_SESSIONS_MIN] |
   | sessions_on_record | [N] |
   | anomaly_detection | [active / inactive] |

   ## Pre-flight Results
   [One line per check: PASS / WARN / FLAG / CRITICAL]

   ## Spec Registry
   | Item | Type | Declared value | Source | Status |
   |---|---|---|---|---|
   [Populated as skill declares its intentions — Type: Explicit or Inferred]

   ## Output Fingerprints
   | File path | Skill | Written at | Est. size | Last referenced | Status |
   |---|---|---|---|---|---|
   [Populated as files are written]

   ## Dependency Chain Map
   | Step | Produces | Consumed by | Status |
   |---|---|---|---|
   [Populated as pipeline runs]

   ## Tool Call Tracker
   | Tool | Count |
   |---|---|
   | Write | 0 |
   | Edit | 0 |
   | Read | 0 |
   | Bash | 0 |
   | Write:Read ratio | — |

   ## Issue Resolution Tracker
   | Issue key | Severity | Raised at | Resolved at | Resolution type | User-confirmed |
   |---|---|---|---|---|---|
   [Populated as issues are raised and resolved]

   ## Issue Log
   [Entries appended below as execution proceeds]
   ```

3. Capture the **Spec Registry**: as the skill begins, extract and log any declared intentions. Mark each as:
   - **Explicit** — directly stated in the skill spec or user instruction
   - **Inferred** — deduced by the watchdog from context (lower confidence; flag if unmet)

   Items to capture: expected output files and names, column counts/schema, row or record counts, output formats, declared phases or steps, any explicit success criteria.

---

## Phase 2 — Continuous Monitoring

Throughout skill execution, silently track all criteria below.

### Log entry format

```
### [SEVERITY] [HH:MM] — [Category > Rule ID]: Short title
**Observed:** [what happened]
**Expected:** [what should have happened]
**Discrepancy:** [the gap]
**Dedup key:** [Category:RuleID:target]
```

### Alert Deduplication

Maintain an in-memory dedup table keyed on `[Category:RuleID:target]`. If the same key fires again:
- Do NOT write a new log entry
- Append `(×2)`, `(×3)`, etc. to the original entry's title line
- When recurrence count reaches `ESCALATION_THRESHOLD` (default: 2): auto-promote severity one level (INFO→WARN, WARN→FLAG, FLAG→CRITICAL) and append an escalation note
- **Exception:** issues with `Resolution type: auto-resolved` in the Issue Resolution Tracker do NOT count toward escalation thresholds

### Issue Resolution Tracking

Whenever an issue is raised:
1. Add a row to the Issue Resolution Tracker table with `Resolution type: unresolved`.
2. When resolved: update `Resolved at`, `Resolution type`, and `User-confirmed`.
   - `auto-resolved` — watchdog resolved autonomously (Tier 1 or 2 action)
   - `user-resolved` — user explicitly confirmed resolution
   - `bypassed` — user explicitly chose to skip without resolution
   - `unresolved` — remains open at session end

---

### Monitoring Rules

#### Naming Consistency

| Rule ID | Rule |
|---|---|
| NC-01 | Variable or function names drift across steps without declaration |
| NC-02 | Terminology inconsistency across written content (e.g. "Phase 1" vs "Phase One") |
| NC-03 | File naming that deviates from the convention established at session start |
| NC-04 | Column or field names change spelling or casing between steps |

#### Spec vs Execution

| Rule ID | Rule |
|---|---|
| SE-01 | Declared count (columns, rows, files, phases) not matched during execution |
| SE-02 | Output format changes mid-pipeline without declaration |
| SE-03 | A declared output file is never written |
| SE-04 | A declared step or phase is never started or completed |
| SE-05 | A file is written that was never declared in the Spec Registry — log `[WARN] Undeclared output: [path]` |

#### Pipeline Integrity

| Rule ID | Rule |
|---|---|
| PI-01 | Output from Step A is not confirmed before Step B begins |
| PI-02 | A file is written but never referenced again — detected via Output Fingerprint table at session end |
| PI-03 | Data transformation chain breaks: input of one step doesn't match declared output of the previous |
| PI-04 | Steps executed out of declared order without explanation |
| PI-05 | Explicit mismatch between what a step produces and what the next step expects, per Dependency Chain Map |

#### Silent Failures

| Rule ID | Rule |
|---|---|
| SF-01 | Error handling that catches exceptions without logging or surfacing them |
| SF-02 | A tool call returns an empty result with no follow-up check |
| SF-03 | A write operation with no confirmation read or size check afterward |
| SF-04 | A loop or batch operation completes without confirming item count |
| SF-05 | Missing null/empty checks before operations on data that could be absent |
| SF-06 | A Bash command returns a non-zero exit code with no explicit error handling |

#### Truncation Risks

| Rule ID | Rule |
|---|---|
| TR-01 | Large dataset operations without chunking, pagination, or size limits |
| TR-02 | File writes on large content without size verification afterward |
| TR-03 | Operations producing output likely to exceed context window without streaming or batching |
| TR-04 | Content generation where length is unbounded and no truncation guard exists |

#### Claude Behavior

| Rule ID | Rule |
|---|---|
| CB-01 | Assumption drift: an assumption stated early is contradicted later without acknowledgment |
| CB-02 | Scope creep: Claude performs actions not requested by the skill spec |
| CB-03 | Hallucinated references: Claude references a file, function, column, or result never confirmed to exist |
| CB-04 | Write-without-read: Claude writes to a file it has not read in the current session (silent overwrite risk) |
| CB-05 | Instruction compliance gaps: steps in CLAUDE.md, the skill spec, or memory silently skipped |
| CB-06 | Repeated identical tool calls: same call made multiple times with same parameters |
| CB-07 | Tool call ratio anomaly: Write+Edit:Read ratio exceeds 3:1 across >4 total tool calls |

#### Context Integrity

| Rule ID | Rule |
|---|---|
| CI-01 | Context compaction event occurs — flag what declared specs or in-progress state may have been lost |
| CI-02 | High context load inferred (long, complex session) — output quality may degrade |
| CI-03 | Reference to prior output that cannot be verified within the current context |

#### Watchdog Self-Monitoring (applied during Phase 8)

| Rule ID | Rule |
|---|---|
| WD-01 | Watchdog failed to detect an issue later identified by user or a subsequent session |
| WD-02 | Watchdog fired a rule that the user explicitly dismissed as incorrect (false positive) |
| WD-03 | Watchdog CRITICAL hard-stop was triggered but the issue resolved without user action (over-sensitive) |
| WD-04 | Watchdog Phase 5 registry write did not complete (Evolution Registry not updated) |
| WD-05 | Watchdog used informal prose formatting where structured output was expected in its own session log |

#### Output Quality Assertions

| Rule ID | Rule |
|---|---|
| OQ-01 | A declared output file was written but its content is structurally wrong (empty table, missing required sections) |
| OQ-02 | A file references another file that does not exist at time of reference |
| OQ-03 | A generated file's character count is less than 10% of comparable prior outputs for this skill (size regression) |
| OQ-04 | A file written this session overwrites a file written in a prior session without a version increment or backup |

#### Recovery Verification

| Rule ID | Rule |
|---|---|
| RV-01 | A CRITICAL was raised but no recovery action was logged within the same session |
| RV-02 | A FLAG was auto-resolved but no verification step was taken afterward |
| RV-03 | User bypassed a CRITICAL without selecting one of the recovery options (implicit bypass) |

#### Category C — Enhancement Observations

Category C entries are NOT issues — they are observations about skill behavior that suggest improvement opportunities. They are always `[INFO]` severity and never escalate. They feed into Phase 9 (Active Skill Correction) proposals rather than immediate action.

| Sub-type | ID | Observation |
|---|---|---|
| Repeated workaround | C1 | A step was manually corrected in 2+ sessions in the same way — the skill spec likely needs updating |
| Config not centralized | C2 | A value (client name, date, path) was hard-coded inline instead of read from a config or session-state file |
| Token waste pattern | C3 | A sequence of tool calls could be replaced by a single call (e.g. multiple Reads before a Write that could use a Glob) |
| Missing output gate | C4 | A phase produced a file or data with no mandatory downstream validation step declared in the spec |
| Fragile step dependency | C5 | A step depends on an output from a prior step but does not explicitly verify that output exists before proceeding |
| Undeclared assumption | C6 | Claude used a value (column name, path structure, format) that was never explicitly confirmed in this session |
| Style drift candidate | C7 | An output format or label drifted slightly from prior sessions — may indicate an undocumented style rule |
| Missing error recovery | C8 | A step that can fail (API call, Drive upload, Bash command) has no spec-declared fallback or retry logic |
| Phase scope creep risk | C9 | A phase is performing work that belongs in a different phase per the skill spec's declared structure |
| Documentation gap | C10 | A decision made in this session (format choice, skip reason, alternate path) was not recorded anywhere |
| MCP/API access gap | C11 | A step could be automated via MCP or API but is currently manual — flag the MCP tool name if known |

Log format for Category C:
```
### [INFO] [HH:MM] — Category C > [C-ID]: [Short title]
**Observed:** [what happened]
**Enhancement opportunity:** [what could be improved in the skill spec]
**Phase 9 candidate:** yes
**Dedup key:** C:[C-ID]:[target]
```

Category C entries accumulate across sessions. Phase 9 reads them to generate targeted spec corrections.

#### Pre-/Compact Signal Detection

Monitor all Write tool calls throughout the session. When a Write tool call targets a file matching `*/session-state.md`:

1. Treat this as the pre-/compact signal — the monitored skill is about to compact and the context will be cleared.
2. Immediately run Phase 4 (End-of-Session Checkpoint) without waiting for the monitored skill to declare completion.
3. Immediately run Phase 5 (Registry Update) after Phase 4.
4. Log `[INFO] Pre-/compact signal detected (session-state.md written) — Phase 4 + Phase 5 close sequence complete. Registry updated. Safe to /compact.`
5. Do not block /compact — this runs as a fast synchronous close before /compact is called.

This ensures the Evolution Registry is updated on every phase boundary, not just at full session completion. It eliminates the one-session lag caused by orphaned session logs.

---

### Autonomous Response Library

Before logging any issue, run the pre-check for that rule's pattern. This enables Tier 1 and Tier 2 autonomous responses before escalating to the user.

**Autonomy tier definitions:**

| Tier | Behavior | When to use |
|---|---|---|
| 1 — Auto-resolve | Acts and logs result silently. Issue marked `auto-resolved`. | Deterministic resolution, zero destructive risk, recoverable |
| 2 — Auto-mitigate + notify | Acts and notifies user, does not wait. Issue marked `auto-resolved`. | Pattern well-understood, action recoverable, user should be aware |
| 3 — Escalate with options | Halts and presents structured recovery choices. | Ambiguous, potentially destructive, or first-occurrence unknown |

`AUTONOMY_TIER_MAX` controls the maximum tier the watchdog will execute autonomously. Default: 2. To require user approval for all issues, set to 0.

**Pre-scripted autonomous responses:**

| Rule | Tier | Pre-check | Autonomous action |
|---|---|---|---|
| SE-03 | 1 | Check if the declared file exists under an alternate name matching the declared name pattern (case variations, path prefixes) | If found: log `[INFO] SE-03 auto-resolved: file found at [path]`, mark resolved. If not found: escalate to FLAG. |
| PI-02 | 1 | Before flagging a file as orphaned, check if it appears in an explicit "intermediate outputs" or "temp" section in the skill spec | If it does: log `[INFO] PI-02 suppressed: file is declared intermediate output`, skip. |
| CI-01 | 2 | On context compaction: automatically re-read the Spec Registry from the session log file | Re-read log, log `[WARN] CI-01 auto-mitigated: Spec Registry restored from log after compaction. Verify working state is consistent.` |
| SF-02 | 1 | Before flagging an empty tool result, cross-check against Output Fingerprints and Spec Registry | If the file/target was never declared to exist: log `[INFO] SF-02 auto-resolved: target was never declared — empty result is expected`, mark resolved. |
| CB-04 | 2 | Check if the write target was already written earlier this session (second write, not a blind first-time overwrite) | If yes: downgrade to `[WARN]`, notify `[WARN] CB-04 auto-mitigated: second write to own file (lower risk than blind first-write). Review if unintended.` |
| CB-06 | 1 | Verify tool parameters differ in at least one field before flagging as identical repeated call | If parameters differ: log `[INFO] CB-06 auto-resolved: calls have differing parameters — not identical`, mark resolved. |
| WD-04 | 2 | Detect incomplete registry write (session log exists but no registry row found) | Write the missing registry row now. Log `[WARN] WD-04 auto-mitigated: missing registry entry written retroactively for [date] [skill].` |
| OQ-03 | 1 | Before flagging size regression, check if the prior session output was unusually large (outlier) | If baseline avg is unavailable or prior output was >3× the all-time avg: log `[INFO] OQ-03 suppressed: insufficient baseline for regression detection`, skip. |

---

### Output Fingerprinting

Whenever a Write or Edit tool call is made:
1. Record in the Output Fingerprints table: file path, skill name, timestamp, estimated content size.
2. Mark status as `active` (not yet referenced elsewhere).
3. When the file is subsequently read or referenced: update `Last referenced` and mark status `referenced`.
4. At end of session: any file still `active` and tagged with the current skill triggers Rule PI-02.
5. Files tagged with a different skill are excluded from orphan detection for this skill's run.

### Tool Call Tracking

Maintain in-memory counters for Write, Edit, Read, and Bash tool calls. Update the Tool Call Tracker table in the log after every tool call.

At each checkpoint and at end of session:
1. Compute Write+Edit:Read ratio.
2. If ratio > 3:1 and total tool calls > 4: log `[WARN] — CB-07: Write:Read ratio is N:1. CB-04 (write-without-read) may be under-reported.`

### Intra-Session Memory Check

At each Phase checkpoint, verify that Claude's behavior has not drifted from its own declared plan:
1. Re-read each assumption marked **Explicit** in the Spec Registry.
2. Check whether Claude's recent tool calls are consistent with each assumption.
3. If contradicted: log `[FLAG] — CB-01: Assumption drift detected: "[assumption]" contradicted by [observed action]`.
4. Include in checkpoint: `Memory check: N assumptions verified | N drifted`.

### Dependency Chain Map

As the pipeline executes:
1. When a step produces a file: add row `Produces = [file path]`, `Status = written`.
2. When a subsequent step reads that file: update `Consumed by = [Step N]`, `Status = consumed`.
3. At end of session: `Status = written` (never consumed) → triggers PI-02. A consumed file not in `Produces` column → triggers PI-03.

---

## Phase 3 — Mid-Session Checkpoints

At each declared phase boundary, surface a checkpoint in chat and append to the log:

```
─────────────────────────────────────────────
[Watchdog] Checkpoint — Phase [N] complete
Issues so far:    [N] CRITICAL  [N] FLAG  [N] WARN  [N] INFO
Resolution:       [N] auto-resolved | [N] user-resolved | [N] unresolved
Spec compliance:  [N/M items met]
Write:Read ratio: N:1  [OK / WARN]
Memory check:     N assumptions verified | N drifted
Issue rate vs baseline: [N issues so far vs avg N.N for [skill-name]] [above / below / within range]
[Anomaly flag if >1.5× baseline issue rate: "Anomaly: issue rate is N× the baseline for [skill-name]"]
[If unresolved FLAGs: list them briefly]
─────────────────────────────────────────────
```

Do not pause execution at a checkpoint unless a CRITICAL issue is outstanding.

---

## Severity Levels

| Level | When to use | Escalates after |
|---|---|---|
| `[INFO]` | Observation with no impact on output quality | 2 recurrences → WARN |
| `[WARN]` | Potential issue that may affect output | 2 recurrences → FLAG |
| `[FLAG]` | Confirmed inconsistency or missed step — review output before use | 2 recurrences → CRITICAL |
| `[CRITICAL]` | Major failure risk — halt execution | Hard-stop, no further escalation |

---

## CRITICAL Hard-Stop Protocol

If a CRITICAL issue is detected:

1. **Stop execution immediately.**
2. Append to the log:
   ```
   ### [CRITICAL] [HH:MM] — [Category > Rule ID]: [Title]
   **What was happening:** [action in progress]
   **What the issue is:** [full description]
   **What could go wrong if continued:** [consequence]
   **Execution halted. User action required.**
   ```
3. Surface in chat with rule-specific recovery options:
   ```
   CRITICAL — [title]

   What happened: [description]
   Risk if continued: [consequence]

   Recovery options:
   - [ ] Option A: [specific action] — risk: low
   - [ ] Option B: [specific action] — risk: medium
   - [ ] Skip this step — acceptable only if: [condition]
   - [ ] Investigate first: [what to check and where]
   ```
4. Add row to Issue Resolution Tracker with `Resolution type: unresolved`.
5. Wait for explicit user instruction. When user responds: update the Resolution Tracker row.

CRITICAL conditions:
- Write operation would overwrite a file not read this session (CB-04 escalated)
- Pipeline stage would silently drop or corrupt data with no recovery path
- Loop or batch shows signs of infinite recursion or runaway execution
- Output file confirmed empty or malformed where content was required
- Evidence that a prior CRITICAL warning was bypassed without resolution (RV-03)
- Non-zero Bash exit code on a pipeline-critical command with no error handling (SF-06 escalated)

---

## Phase 4 — End-of-Session Summary

When the monitored skill completes or is terminated, append to the log and display in chat:

```
─────────────────────────────────────────────
## End-of-Session Summary

**Skill:** [skill-name]
**Session duration:** [start] → [end]
**Watchdog version:** 5.0

### Issue Counts
| Severity | Count |
|---|---|
| [CRITICAL] | N |
| [FLAG] | N |
| [WARN] | N |
| [INFO] | N |
| Auto-resolved | N |
| Total | N |

### Issue Resolution Summary
| Resolution type | Count |
|---|---|
| auto-resolved | N |
| user-resolved | N |
| bypassed | N |
| unresolved | N |

### Unresolved FLAGs
[List any FLAG items not addressed, or "None"]

### Orphaned Outputs
[Files written but never referenced, or "None"]

### Spec Registry — Compliance Check
| Declared item | Type | Status |
|---|---|---|
| [item] | Explicit / Inferred | Met / Unmet / Unverifiable |

### Session vs Baseline
[Displayed only if Sessions on record >= BASELINE_SESSIONS_MIN]
| Dimension | This session | Skill baseline | Delta |
|---|---|---|---|
| Confidence | N/100 | N/100 | +N / -N |
| Total issues | N | N avg | +N / -N |
| CRITICAL count | N | N avg | +N / -N |
| Auto-resolved | N | N avg | +N / -N |

Baseline assessment: [Within normal range / Outperforming baseline / Regression detected]
[If Regression detected: "Regression flagged — confidence dropped N points below baseline. Phase 8 metacognitive analysis recommended."]

### Output Confidence Score
| Dimension | Score | Notes |
|---|---|---|
| Spec compliance | N/20 | [brief note] |
| Pipeline integrity | N/20 | [brief note] |
| Silent failure risk | N/20 | [brief note] |
| Truncation risk | N/20 | [brief note] |
| Claude behavior | N/20 | [brief note] |
| **Total** | **N/100** | |

Trust assessment:
- 90–100 → TRUSTED: output can be used as-is
- 70–89 → REVIEW RECOMMENDED: verify before using
- 50–69 → USE WITH CAUTION: significant issues present
- <50   → DO NOT USE: critical or structural failures detected

### Tool Call Summary
| Tool | Count |
|---|---|
| Write | N |
| Edit | N |
| Read | N |
| Bash | N |
| Write:Read ratio | N:1 [OK / WARN] |

### Watchdog Blind Spots
| What watchdog cannot observe | Why | Risk level |
|---|---|---|
[Specific limitations for this session, e.g.:]
| NotebookEdit cell outputs | Tool output not inspectable | Medium |
| Phase N content after context compaction | Spec Registry may be incomplete | High |

### Log file
[Full path to this session's log file]
─────────────────────────────────────────────
```

After displaying the summary, ask the user:
```
[Watchdog] Did the watchdog catch at least one issue that required action this session? (yes / no / not sure)
```
Record the response. If no reply, record as `no response`.

---

## Phase 5 — Self-Evaluation and Evolution Registry Update

**This phase is mandatory and non-optional.** It runs immediately after Phase 4 (End-of-Session Summary) every time, without exception. It must not be deferred or skipped — it is what makes the watchdog's learning loop work. If the monitored skill session ends (user compacts, declares a phase complete, or the conversation ends naturally), Phase 5 runs before the watchdog closes. Do not wait to be explicitly asked to run Phase 5.

After the end-of-session summary, update the Evolution Registry.

### 5.1 — Write session metrics

Append a new row to the Session History table:
```
| [YYYY-MM-DD] | [skill-name] | [duration] | [CRITICAL] | [FLAG] | [WARN] | [INFO] | [confidence]/100 | [feedback] |
```
Increment `Total sessions monitored` by 1.

### 5.2 — Update rule effectiveness table

For each Rule ID that fired: increment `Total fires`, update `Last fired`, reset `Sessions since fire` to 0.
For each Rule ID that did not fire: increment `Sessions since fire`.

Update `Trend`:
- Fired more in last 5 vs prior 5 → `rising`
- Fired less → `declining`
- Stable → `stable`
- Zero fires, >5 sessions → `inactive`

### 5.3 — Update cumulative metrics

Add this session's counts to the Cumulative Issue Metrics table by category.

### 5.3b — Update per-skill confidence trend

In the Per-Skill Confidence Trend table:
1. Find the row for `[skill-name]`. If none: create it.
2. Append the session's confidence score to `Last 5 scores` (keep only 5 most recent).
3. Recompute `Avg confidence`. Set `Trend` (↑ / ↓ / →).

### 5.3c — Update per-skill baseline file

After updating the registry:
1. Open `BASELINE_DIR/[skill-name].md`.
2. Append a new row to the Confidence History table with this session's dimension scores and issue count.
3. Recompute the Computed Baselines section (3-session avg, 5-session avg, all-time avg, trend direction).
4. Recompute Anomaly Thresholds if `Sessions on record` >= `BASELINE_SESSIONS_MIN`:
   - Confidence threshold: `all-time avg - 10`
   - Issues threshold: `all-time avg issues + (1.5 × std deviation)` (approximate: avg × 1.5 as a proxy)
5. Update `Last updated` and `Sessions on record`.

### 5.4 — Compute evolution signals

Check after updating:
- Any rule with `Sessions since fire` ≥ 10 → mark `Status: Candidate for review`
- Any rule fired in >75% of last 10 sessions → mark `Status: High frequency`
- Any Rule ID appearing as CRITICAL in 2+ distinct sessions → mark `Status: Recurring critical`

**Quality-gated trigger**: Generate proposals if ANY of:
- Sessions since last proposal ≥ `EVOLUTION_TRIGGER` (3) — count gate
- A rule marked `High frequency` exists — noise signal
- A `Recurring critical` exists — safety signal
- Feedback `no` in ≥60% of last 10 sessions — signal-to-noise problem
- A regression event occurred this session (confidence dropped >10 points from baseline) — quality gate

### 5.5 — Proposal validation (before appending)

Before appending any proposal to the registry, validate:
1. **Counterfactual check**: Would this change have affected the last 3 sessions differently? Log the answer.
2. **Frequency gate for deletions**: If proposing to remove a rule, verify it fired 0 times in the last 10 sessions. If it fired even once: downgrade proposal confidence to Low.
3. **Definition gate for additions**: If proposing a new rule, define: exact condition, log entry format, and dedup key before appending.

### 5.5 — Generate improvement proposals

When triggered, generate 1–5 concrete proposals. Append each to the Pending Proposals section:

```
### Proposal [N] — [YYYY-MM-DD]
**Confidence:** High / Medium / Low
**Based on:** [N] sessions of data
**Signal:** [which rule IDs or patterns triggered this]
**Counterfactual:** [would this change have fired differently in last 3 sessions?]
**Proposed change:** [plain-language description]
**Rationale:** [why this change would improve the watchdog]
**Suggested edit:**
> [Exact text to add, modify, or remove in the skill spec]
**Status:** Pending
```

Reset `Sessions since last proposal` to 0.

### 5.6 — Surface evolution status

```
[Watchdog Evolution] Sessions logged: N total | N since last proposals | Next trigger: [count or quality signal]
```

If proposals generated:
```
[Watchdog Evolution] N improvement proposals generated. Run `/skill-watchdog evolve` to review and apply.
```

### 5.7 — Record user feedback

Write feedback value into the `Feedback` column of the session row from 5.1. Flag signal quality per prior behavior.

### 5.8 — Drive session log sync

After completing Phase 5.1–5.7, upload a copy of this session's log file to the Drive folder `DRIVE_SESSION_LOGS_FOLDER` under the parent `DRIVE_PARENT_FOLDER_ID`.

1. Use the Google Drive MCP (`mcp__claude_ai_Google_Drive__create_file`) to upload the log file.
2. Name the Drive copy identically to the local log filename: `YYYY-MM-DD_HH-MM_[skill-name]_watchdog.md`.
3. If upload fails (Drive MCP unavailable, auth error, etc.): log `[WARN] — Drive sync failed for session log: [path]. Log remains local only. Retry with /skill-watchdog apply-feedback or sync manually.` Do NOT block session close on upload failure.
4. If upload succeeds: log `[INFO] — Session log synced to Drive: [filename].`

This ensures the weekly Apps Script report has access to all session data even when the local machine is not running.

### 5.9 — Slack End-of-Session Notification

After completing Phase 5.8 (Drive sync), send a Slack DM to `SLACK_DM_TARGET` if `SLACK_NOTIFICATIONS` is not `disabled`.

**Notification modes:**
- `end-of-session` — always send when session closes
- `all-flags` — only send if CRITICAL + FLAG count > 0
- `critical-only` — only send if CRITICAL count > 0
- `disabled` — skip entirely

**Message to send:**
```
*Watchdog* | {skill-name} | {YYYY-MM-DD}
Score: {N}/100 — {TRUSTED / REVIEW RECOMMENDED / USE WITH CAUTION / DO NOT USE}
Issues: {N} CRITICAL  {N} FLAG  {N} WARN  {N} INFO  |  {N} auto-resolved
{If unresolved FLAGs or CRITICALs: ⚠️ {N} unresolved — check session log}
Log: {log filename}
```

**Tool call:**
```
mcp__claude_ai_Slack__slack_send_message(channel="{SLACK_DM_TARGET}", text="{formatted message above}")
```

**Guard conditions:**
- If `SLACK_DM_TARGET` still contains the placeholder text `[your-slack-member-id]`: skip silently. Log `[INFO] — Slack notification skipped: SLACK_DM_TARGET not configured. To enable, paste your Slack member ID (found in Slack: your profile → "..." → "Copy member ID") into the Configuration block.`
- If the Slack MCP returns an error: log `[WARN] — Slack notification failed: {error}. Session close is not blocked.`
- Do not block Phase 5 on Slack — if it fails, proceed.

### 5.10 — Forced-Close Triggers

Phase 5 must complete even if the session ends without an explicit user close. The following signals all trigger an immediate Phase 4 + Phase 5 sequence:

| Trigger | Signal |
|---|---|
| Pre-/compact signal | Write tool call targets `*/session-state.md` |
| Natural session end | User message explicitly ends the watchdog session: "wrap up", "wrap up the session", "close session", "end session", "watchdog wrap", "finish the session" — generic task completions like "done" or "done with this" do NOT trigger (they likely refer to a specific step, not the whole session) |
| Phase boundary | Monitored skill writes its own end-of-session state or completes its final declared phase |
| Manual override | User types `/skill-watchdog close` or `/skill-watchdog wrap` |

When any forced-close trigger fires:
1. Immediately run Phase 4 (if not already run this session).
2. Immediately run Phase 5.1–5.9 (includes Drive sync and Slack notification).
3. Log `[INFO] — Forced-close triggered by: [signal]. Phase 4 + Phase 5 complete. Registry, Drive sync, and Slack notification done.`
4. Do NOT wait for the monitored skill to acknowledge or complete.

---

## Phase 5b — Per-Skill Performance Analysis

Runs after Phase 5 when `Sessions on record` >= `BASELINE_SESSIONS_MIN` (3).

1. Read `BASELINE_DIR/[skill-name].md`.
2. Compute trend direction for each confidence dimension across the last 5 sessions (↑ = last score > prior avg, ↓ = below, → = within ±3 points).
3. Identify **persistent weak dimensions**: any dimension scoring below 15/20 in 3 consecutive sessions.
4. Identify **improving dimensions**: any dimension increasing in 3 consecutive sessions.
5. Flag regressions: any dimension that dropped >5 points vs the prior session.
6. Update the `Persistent Weak Dimensions` and `Improving Dimensions` sections of the baseline file.

Append to the session log:

```
### Per-Skill Performance Analysis
Skill: [name] | Sessions on record: N

Trend by dimension (last 5 sessions):
| Dimension | Last 5 scores | Trend | 5-session avg |
|---|---|---|---|
| Spec compliance | N N N N N | ↑/↓/→ | N/20 |
| Pipeline integrity | ... | | |
| Silent failure risk | ... | | |
| Truncation risk | ... | | |
| Claude behavior | ... | | |

Persistent weak dimensions:
- [Dimension]: avg N/20 across last N sessions — candidate for targeted monitoring
  [Or: "None"]

Improving dimensions:
- [Dimension]: avg N/20, trending +N over last N sessions
  [Or: "None"]

Regression alert: [None / "Dimension [X] dropped N points vs prior session"]
```

---

## Phase 6 — Evolution Mode

**Activation:** `/skill-watchdog evolve`

### 6.1 — Pre-application validation

1. Read the current SKILL.md. Compute checksum: line count + character count.
2. Store a pre-snapshot in `SNAPSHOT_DIR/pre-[YYYY-MM-DD]-proposal-[N].md` with format:

   ```markdown
   # Watchdog Self-Snapshot
   **Type:** pre
   **Date:** YYYY-MM-DD
   **Proposal:** N
   **Version:** [current version]
   **Section modified:** [Phase X — Title]
   **Line count:** N
   **Character count:** N

   ## Snapshot Content
   [verbatim copy of the section to be modified]
   ```

3. Verify the proposal's target text still appears in the current SKILL.md. If not found:
   ```
   [WARN] — Proposal [N] may be stale. Target text not found in current SKILL.md. It may have been modified since this proposal was generated. Apply anyway? (yes / no)
   ```
4. Prune oldest snapshots if `SNAPSHOT_DIR` contains more than `SNAPSHOT_RETENTION` files.

### 6.2 — Structured application

For each pending proposal, present in chat:

```
─────────────────────────────────────────────
Proposal [N] — [date] (Confidence: [level] | Based on: [N] sessions)

Change: [description]
Rationale: [why]
Signal: [rule IDs or patterns]
Counterfactual: [effect on last 3 sessions]

BEFORE:
[original text]

AFTER (proposed):
[new text]
─────────────────────────────────────────────
Apply? (yes / no / edit first)
```

Wait for user response.

### 6.3 — Post-application self-test

After applying any modification:
1. Re-read the modified SKILL.md section.
2. Verify the applied text matches the approved change exactly.
3. If it matches: log `[INFO] — Self-modification verified: proposal N applied cleanly.`
4. If it differs: log `[FLAG] — Self-modification mismatch: applied text differs from approved change. Review manually.`
5. Store a post-snapshot in `SNAPSHOT_DIR/post-[YYYY-MM-DD]-proposal-[N].md`.
6. Append to Applied Improvements Log in registry:
   ```
   ### [YYYY-MM-DD] — v[new version]
   Applied proposal [N]: [description]
   Pre-checksum: [line_count:char_count] → Post-checksum: [line_count:char_count]
   ```
7. Increment `WATCHDOG_VERSION` by 0.1. Update version in SKILL.md Configuration section and registry.

### 6.4 — Rollback

**Activation:** `/skill-watchdog rollback [proposal-N]` or `/skill-watchdog rollback last`

1. Locate `SNAPSHOT_DIR/pre-[YYYY-MM-DD]-proposal-[N].md`.
2. Read the pre-snapshot and show a diff-style before/after in chat (current content vs pre-snapshot content).
3. Ask: `Confirm rollback? (yes / no)`
4. On confirmation:
   - Replace the relevant SKILL.md section with the pre-snapshot content.
   - Log `[INFO] — Rollback applied: proposal [N] reverted. Version: [N] → [N-0.1].`
   - Decrement `WATCHDOG_VERSION` by 0.1.
   - Update the Applied Improvements Log with a rollback entry.

---

## Phase 7 — Skill Health Dashboard

**Activation:** `/skill-watchdog report`

Reads the Evolution Registry and per-skill baseline files. Does not modify any files.

```
═══════════════════════════════════════════════════
  WATCHDOG HEALTH REPORT — [YYYY-MM-DD]
  Based on [N] sessions across [N] skills
═══════════════════════════════════════════════════

OVERALL
  Total sessions:        N
  Avg confidence:        N/100
  Total issues:          N (N CRITICAL  N FLAG  N WARN  N INFO)
  Auto-resolved:         N (N% of total issues)
  User feedback:         N% reported a caught issue (from N responses)

PER-SKILL BREAKDOWN
  [skill-name]  Sessions: N  Avg: N/100  Trend: [↑↑ / ↑ / → / ↓ / ↓↓]
  History (last 5): [N] [N] [N] [N] [N]
    Spec compliance:    avg N/20  [↑/↓/→]
    Pipeline integrity: avg N/20  [↑/↓/→]
    Silent failure:     avg N/20  [↑/↓/→]
    Truncation risk:    avg N/20  [↑/↓/→]
    Claude behavior:    avg N/20  [↑/↓/→]
  [next skill...]

SKILL BENCHMARKING
  Highest avg confidence: [skill-name]  N/100
  Lowest avg confidence:  [skill-name]  N/100
  Most improved (last 3): [skill-name]  +N points
  Most regressed (last 3): [skill-name]  -N points

TOP 5 RULES  (all sessions, all skills)
  1.  [Rule ID]  [Name]  —  N fires
  2.  ...

RULES TO REVIEW
  Inactive  (0 fires, 10+ sessions):   [Rule ID list, or "None"]
  High noise (>75% session rate):      [Rule ID list, or "None"]
  Recurring CRITICAL:                  [Rule ID list, or "None"]

FEEDBACK SIGNAL
  Actionable catch rate:   N%  [from N sessions with responses]
  Signal quality:          [Strong / Moderate / Weak / Insufficient data]

WATCHDOG SELF-HEALTH
  Self-modification events:  N (last: [date or "Never"])
  Rollback events:           N
  False positive rate:       N% (from N user dismissals)
  Missed issue rate:         N% (from Phase 8 analysis)
  Metacognitive sessions:    N (last: [date or "Never"])
  Registry write rate:       N% (sessions with completed Phase 5)

EVOLUTION STATUS
  Pending proposals:      N
  Sessions until count trigger: N
  Last proposals:         [YYYY-MM-DD or "Never"]
  Watchdog version:       [version]
═══════════════════════════════════════════════════
```

If pending proposals exist: append "Run `/skill-watchdog evolve` to review and apply them."
If `Registry write rate` < 90%: append "Warning: Phase 5 is not completing reliably. Check for context truncation or session interruptions."

---

## Phase 7b — HTML Dashboard Regeneration

Runs automatically after the Phase 7 chat report. Regenerates the local HTML skill health dashboard with live data.

```bash
python3 /Users/carlaklaasen/claude_code/all_skills/watchdog-evolution/generate_skill_dashboard.py
```

- If the script succeeds: report `Dashboard regenerated → all_skills/skill-health-dashboard.html`
- If the script fails with a Python error: surface the error message. The chat report above is still complete and usable.
- If the script file is not found: log `[WARN] — Dashboard generator not found at expected path. Chat report is the authoritative output.`

The HTML dashboard at `all_skills/skill-health-dashboard.html` is the visual equivalent of the chat report — open it in a browser to see sparklines, per-skill cards, and the enhancement suggestions panel.

---

## Phase 8 — Metacognitive Self-Monitoring

**Activation:** `/skill-watchdog metacognitive`
**Auto-trigger:** When `Regression detected` appears in a Phase 4 Session vs Baseline assessment AND `METACOGNITIVE_TRIGGER = regression`.

The watchdog runs its own monitoring rules against its own past session logs to identify blind spots, false positives, and missed issues. Results feed directly into proposals and (for high-confidence additive changes) autonomous self-modification.

### 8.1 — False Positive Detection

1. Read all session logs from the last 10 sessions (or all available if < 10).
2. For each issue in the Issue Resolution Tracker with `Resolution type: bypassed` or `user-resolved` where the user action was to dismiss (infer from context): mark as candidate false positive for that rule.
3. Count: if the same Rule ID appears as a candidate false positive in 3+ sessions → log `[WD-02] Rule [ID] appears to generate false positives in [N]% of sessions.`
4. Generate a proposal to tighten that rule's condition. Set confidence based on: Low (<3 sessions), Medium (3–5 sessions), High (>5 sessions, no counter-examples).

### 8.2 — Missed Issue Detection

1. For each session where user feedback was `no` (watchdog didn't catch anything actionable): re-read the session log.
2. Identify categories of activity that occurred with no corresponding watchdog entry:
   - File writes with no SE-03/PI-02 check logged
   - Bash calls with no SF-06 check logged
   - Multiple tool calls with no CB-06 check logged
3. Log: `[WD-01] Session [date] for [skill]: [category] activity with no watchdog entry. Possible monitoring gap.`
4. Append findings to the Metacognitive Log.

### 8.3 — Format Compliance Self-Check

1. Scan own session logs for WD-05 patterns:
   - Prose paragraphs where a table was expected (Pre-flight, Issue Resolution Tracker, Confidence Score)
   - Missing required sections (Spec Registry, Tool Call Tracker, Issue Resolution Tracker)
   - Inconsistent severity format
2. If format drift detected in >20% of sessions: generate a proposal to add an explicit format-enforcement check step to Phase 1.
3. Log count and description to Metacognitive Log.

### 8.4 — Registry Write Audit

1. List all session log files in `LOG_DIR`.
2. For each: check if a corresponding row exists in the Evolution Registry Session History (match by date and skill name).
3. For any session log with no registry entry: apply WD-04 Tier 2 autonomous response — write the missing entry now and notify.
4. Log audit results to Metacognitive Log.

### 8.5 — Autonomous Self-Modification

After running 8.1–8.4, apply improvements autonomously ONLY if ALL conditions are met:
- Confidence = High (pattern in 3+ sessions, no counter-examples)
- The change is **additive only** (new rule, clarified condition, additional check) — no deletions
- No prior rollback exists for a similar change in the last 10 sessions

If all conditions met: apply via Phase 6.1–6.3 (pre-snapshot, apply, post-snapshot). Log: `[INFO] — Autonomous self-modification applied: [description]. Pre-snapshot: [path].`

For deletive or restructuring changes: generate a Pending Proposal and require user approval via Phase 6.

### 8.6 — Differentiation Report

Explicitly separate two trend lines — the watchdog improving vs. the skill improving:

```
═══════════════════════════════════════════════════
  METACOGNITIVE SELF-REPORT — [YYYY-MM-DD]
  Based on [N] sessions analyzed
═══════════════════════════════════════════════════

WATCHDOG SELF-HEALTH TREND
  False positive rate:     N% → N% → N%  [improving / worsening / stable]
  Missed issue rate:       N% → N% → N%  [improving / worsening / stable]
  Format compliance:       N% → N% → N%  [improving / worsening / stable]
  Registry write rate:     N% → N% → N%  [improving / worsening / stable]

SKILL HEALTH TREND (under watchdog observation)
  [skill-name]: [N/100] → [N/100] → [N/100]  [improving / worsening / stable]

SELF-MODIFICATIONS THIS CYCLE
  Autonomous: N applied  |  Proposal-based: N pending  |  Rollbacks: N

IDENTIFIED BLIND SPOTS
  [List from 8.2, or "None identified"]

PROPOSALS GENERATED THIS CYCLE
  N proposals — run /skill-watchdog evolve to review
  [Or: "None — insufficient signal or all signals below confidence threshold"]
═══════════════════════════════════════════════════
```

Append the full self-report to `METACOGNITIVE_LOG`. Increment `Metacognitive runs` in the Evolution Registry. Update `Watchdog Self-Health History` table.

---

## Phase 9 — Active Skill Correction

**Activation:** `/skill-watchdog correct [skill-name]` (manual) or auto-triggered when EVOLUTION_TRIGGER sessions have elapsed since last correction for a skill, or when a Category C pattern appears in 3+ sessions for the same skill.

Phase 9 reads a skill's session history and baseline, classifies root causes, and either auto-applies corrections or generates targeted proposals. It is additive-only by default — deletions always require Phase 6 approval.

### 9.1 — Root Cause Classification

For each open FLAG, unresolved issue, or Category C pattern in the skill's session logs:

Classify each into one of three root cause types:

| Type | Definition | Action path |
|---|---|---|
| `execution` | Claude deviated from a correctly written spec — the spec says the right thing but Claude didn't follow it | Log as behavioral pattern; no spec change needed; add a stronger instruction to that spec step |
| `spec_gap` | The skill spec was missing, ambiguous, or silent on the scenario — Claude had no instruction to follow | Generate spec correction — add or clarify the missing instruction |
| `environment` | External factor (Drive auth, MCP failure, file not found) — neither Claude nor spec is at fault | Log as environment issue; flag for manual review; no auto-correction |

### 9.2 — Confidence Gates for Auto-Apply

Auto-apply a spec correction without user approval ONLY if ALL conditions are met:
- Pattern appears in 3+ sessions for the same skill and issue type
- Correction is additive only (new instruction, clarification, example — no deletions)
- No prior rollback exists in SNAPSHOT_DIR for a similar correction to the same skill
- Stale-check passes: the target text still exists unchanged in the skill's SKILL.md (same as Phase 6.1 check)

If any gate fails: generate a Pending Proposal (Phase 5.5 format) and require Phase 6 approval.

### 9.3 — Correction Application

When all confidence gates pass:
1. Read the target skill's SKILL.md.
2. Store a pre-snapshot in `SNAPSHOT_DIR/pre-[YYYY-MM-DD]-correction-[skill-name].md`.
3. Apply the edit (Edit tool). Keep it surgical — touch only the minimum text needed.
4. Re-read the modified section to verify.
5. Log `[INFO] — Phase 9 auto-correction applied to [skill-name]: [description]. Pre-snapshot: [path].`
6. Write a row to the Evolution Registry Applied Improvements Log:
   ```
   | [YYYY-MM-DD] | Phase 9 auto-correct | [skill-name] | [description] |
   ```
7. Increment `WATCHDOG_VERSION` by 0.1 if this is the first Phase 9 application this cycle.

### 9.4 — Post-Correction Monitoring

On the next session for the corrected skill:
1. At Phase 3 checkpoints, verify the corrected step is now executing as specified.
2. If the same issue fires again after the correction: log `[FLAG] — Phase 9 correction for [issue] did not resolve the pattern. Escalating to Pending Proposal for user review.`
3. If the correction holds across 2 sessions: mark correction as `stable` in the Applied Improvements Log.

### 9.5 — Correction Report

After running Phase 9, display:
```
─────────────────────────────────────────────
[Watchdog Phase 9] Active Skill Correction — [skill-name]
Root causes analyzed:  N issues classified
  execution:    N  (behavioral — no spec change)
  spec_gap:     N  (spec corrections generated)
  environment:  N  (flagged for manual review)

Auto-applied corrections: N
Pending proposals generated: N
─────────────────────────────────────────────
```

---

## Phase 10 — Weekly Report and Feedback Loop

**Architecture:** Google Apps Script runs on a Friday 8:45am EST time-based trigger (cloud, no local machine required). It reads session logs from Drive, generates an HTML dashboard, and emails it. The local machine runs a separate cron job (`FEEDBACK_WATCH_INTERVAL`) to pick up approved feedback JSON files from Drive and apply them immediately.

### 10.1 — Weekly HTML Dashboard Generation (Apps Script — cloud)

The Apps Script at `all_skills/watchdog-evolution/weekly_report.gs` runs every Friday at 8:45am EST:

1. **Read session logs**: List all files in `DRIVE_SESSION_LOGS_FOLDER`. Filter to logs created since the previous Friday.
2. **Parse logs**: Extract per-skill: session count, confidence scores, issue counts by severity, rule fires.
3. **Read registry**: Download `evolution-registry.md` from Drive. Parse Per-Skill Confidence Trend and Pending Proposals sections.
4. **Generate HTML**: Produce a complete HTML dashboard (same structure as `skill-health-dashboard-MOCKUP.html`):
   - Night mountain photo background
   - One collapsible card per skill with trend sparkline, confidence score, top rules
   - Enhancement suggestions with approve/reject buttons (each writes a JSON file to `DRIVE_FEEDBACK_INBOX_FOLDER` on click)
   - Per-skill JSON download button
   - MCP availability tag on C11 suggestions
5. **Upload to Drive**: Save the HTML as `watchdog-report-YYYY-MM-DD.html` in `DRIVE_WEEKLY_REPORTS_FOLDER`.
6. **Email**: Send to `WEEKLY_REPORT_EMAIL` with:
   - Subject: `Watchdog Weekly — [YYYY-MM-DD] | [N skills] | [avg confidence]/100`
   - Body: inline HTML summary (skill table + top 3 enhancement suggestions)
   - One humor snippet about watchdog performance (rotate from a fixed set of 8)
   - Drive link to the full HTML report
   - Footer: "View full dashboard → [Drive link]"

### 10.2 — Approve/Reject Flow (HTML dashboard → Drive inbox)

When the user opens the HTML dashboard and clicks Approve or Reject on an enhancement suggestion:

The button's `onclick` handler writes a JSON file to `DRIVE_FEEDBACK_INBOX_FOLDER`:

```json
{
  "feedback_id": "[ISO timestamp]-[skill]-[rule-id]",
  "skill": "[skill-name]",
  "rule_id": "[C-ID or Rule ID]",
  "session_date": "[YYYY-MM-DD]",
  "decision": "approve" | "reject",
  "suggestion_text": "[full text of the enhancement suggestion]",
  "decided_at": "[ISO timestamp]"
}
```

Files are named `feedback-[feedback_id].json`.

### 10.3 — Feedback Inbox Processing (local cron — every FEEDBACK_WATCH_INTERVAL)

A local cron job invokes `/skill-watchdog apply-feedback` every `FEEDBACK_WATCH_INTERVAL` (default: 30 minutes) when the machine is running:

1. List all `feedback-*.json` files in `DRIVE_FEEDBACK_INBOX_FOLDER`.
2. For each unprocessed file:
   a. Parse the JSON. Verify required fields present.
   b. If `decision = reject`: mark the Pending Proposal as rejected in the Evolution Registry. No skill file changes. Archive the JSON.
   c. If `decision = approve`: run Phase 9.2 confidence gates against the approved suggestion.
      - If gates pass: apply via Phase 9.3 (auto-apply with pre-snapshot).
      - If gates fail (stale target, deletion required, etc.): surface as a Pending Proposal for Phase 6 manual review. Do not apply.
3. After processing each file: move it to `DRIVE_FEEDBACK_INBOX_FOLDER/processed/feedback-[feedback_id]-done.json`.
4. Log all actions to the local watchdog log for the current date: `YYYY-MM-DD_[HH:MM]_feedback-sync_watchdog.md`.
5. Display in chat (if a session is open): `[Watchdog] Feedback sync: N approved | N rejected | N deferred. [N corrections applied.]`

The local cron setup is a one-time step: add a crontab entry like:
```
*/30 * * * * cd /Users/carlaklaasen/claude_code && claude --print "/skill-watchdog apply-feedback" >> ~/.claude/feedback-cron.log 2>&1
```

---

## Phase 11 — Audit Comment Review Monitor

**Activation:** Auto-activated whenever `seo-geo-technical-audit` enters a column S/R comment review session (Rules C1–C7 in its CLAUDE.md). Also triggered by `/skill-watchdog review-comments`.

Phase 11 intercepts every comment processed during a "Comments for Claude" feedback session, verifies that the correct reference documents were loaded before the comment was acted upon, classifies each comment as a row fix or a skill-rule signal, and — for skill-rule signals — queues and applies Phase 9 corrections in the background while the main session continues.

### 11.1 — Auto-Activation Trigger

Phase 11 activates automatically when both conditions are true:
1. `seo-geo-technical-audit` is the active skill in this session.
2. The agent reads column S or R of an audit Google Sheet in response to a "comments added" confirmation from the user.

When activated, log `[INFO] — Phase 11 active: audit comment review monitor started.`

### 11.2 — Reference Doc Verification (per comment)

Before the audit agent acts on each non-empty comment cell, Phase 11 checks whether the correct reference file was loaded per the Rule C1 routing table in `seo-geo-technical-audit/CLAUDE.md`. Use the following signal words to classify the comment and determine the required reference:

| Comment signal words | Required reference file |
|---|---|
| canonical, redirect, HTTPS, robots.txt, Core Web Vitals, crawl error, 404, mobile speed, page speed, structured data error, tracking, GSC, GA4, configuration | `REFERENCE-1.md` |
| meta description, H1, title tag, image alt, internal linking, backlink, domain authority, AI overview, LLM citation, Bing GEO, word count, on-page | `REFERENCE-2.md` |
| JSON-LD, structured data, schema gap, Schema.org, FAQPage, Product schema | `REFERENCE-SCHEMA.md` |
| too long, redundant, rewrite, score explanation verbose, plain language, tighten, writing style | `CHECKS.md` |
| wrong column, priority colour, column order, Data Analyzed, How to Correct, formatting | `OUTPUTS-WORKBOOK.md`, `CHECKS.md` |
| title tag report, redirect plan, canonical tag issues, upload to Drive, mandatory export | `FORMS-EXPORTS-MANDATORY.md` |
| disavow, sitemap delta, robots.txt recommendation, schema CSV | `FORMS-EXPORTS-CONDITIONAL.md` |
| report card, HTML layout, phase heading, client report | `OUTPUTS-HTML.md` |

**Verification rule**: At the point the comment is being processed, check whether the mapped reference file appears in the current session's tool call history (via Read tool calls). If it does not appear: log `[FLAG] — Phase 11 reference gate: comment in row [N] requires [file] per Rule C1 but no Read of that file was found in this session. Instruct audit agent to Read [file] before proceeding with this comment.` Halt processing of that specific comment and surface the instruction to the agent.

If the reference file is confirmed loaded (Read tool was called for it in this session): log `[INFO] — Phase 11 reference gate PASS: [file] loaded before comment row [N].`

### 11.3 — Comment Classification

After reading all non-empty comment cells, classify each comment as one of:

| Class | Definition | Action |
|---|---|---|
| `row_fix` | Correction scoped entirely to one or more specific cells in that row — swap columns, rewrite a cell, fix a value, update a URL | Log as processed. No skill correction triggered. |
| `skill_rule` | The comment reveals that the skill has a systematic gap — the agent would have made the same error on any audit, not just this row | Log as `[FLAG] — Phase 11 skill signal: [description]`. Queue Phase 9 correction. |
| `both` | A row fix that also reveals a recurring skill rule | Apply the row fix via the audit agent. Queue Phase 9 correction in background. |

**Skill signal detection criteria** — classify as `skill_rule` or `both` if the comment:
- Describes something the skill should "always" or "never" do
- Corrects a pattern that has appeared in prior sessions (check Evolution Registry)
- Fixes a scoring methodology, weight, or data-source rule
- Indicates a reference doc was not consulted when it should have been
- Reveals a prohibited element (e.g. FAQPage schema, word count prescriptions, phase references in client cells)

Log a running tally in the session log:

```
Phase 11 Comment Classification
| Row | Comment summary | Class | Reference required | Reference loaded | Phase 9 queued |
|---|---|---|---|---|---|
```

### 11.4 — Background Skill Correction

For each comment classified as `skill_rule` or `both`:

1. **Identify target file**: Determine which skill file needs updating based on comment type (REFERENCE-1.md, REFERENCE-2.md, CLAUDE.md, CHECKS.md, etc.).
2. **Formulate correction**: Write a one-sentence description of the rule addition or clarification needed.
3. **Run Phase 9 gates**: Apply Phase 9.2 confidence checks:
   - If the same issue has appeared in 2+ prior sessions (check Evolution Registry): all gates pass → auto-apply.
   - If this is the first session where this signal appears: create a Pending Proposal entry (Phase 5.5 format) — do not apply yet.
4. **Apply in background**: If gates pass, apply the correction using Phase 9.3 (pre-snapshot → Edit → verify → log). This runs after the corresponding row fix is confirmed complete, so the main comment review session is not blocked.
5. **Mark correction complete**: Append to the Phase 11 correction queue:

```
Phase 11 Skill Corrections Applied
| Target file | Rule added / clarified | Applied | Pre-snapshot |
|---|---|---|---|
```

### 11.5 — Post-Review Report

After all column S/R comments have been processed (all row fixes applied, all corrections applied or queued), surface a consolidated report before clearing any column S/R cells:

```
─────────────────────────────────────────────
[Watchdog Phase 11] Audit Comment Review — [Client] — [Date]

Comments reviewed:       N
  Row fixes:             N  (applied to sheet only)
  Skill signals:         N  (skill files updated)
  Both:                  N  (row fix + skill file updated)

Reference gate checks:   N checked
  PASS:                  N  (reference loaded before acting)
  FLAG:                  N  (reference missing — loading instructed)

Skill file updates applied this session:
  [File name] — [one-line description of change]
  [File name] — [one-line description of change]

Pending proposals (require 2+ sessions before auto-apply):
  [Description] — queued for [target file]

Pre-snapshots stored: SNAPSHOT_DIR/pre-[date]-correction-[skill].md
─────────────────────────────────────────────
```

If no skill-rule signals were detected: `[Watchdog Phase 11] No skill-level patterns detected in this comment set. All comments were row-specific fixes.`

### 11.6 — Evolution Registry Update

After Phase 11 completes, write skill signal entries to the Evolution Registry Category C section using sub-type C1 (Repeated workaround) for any pattern identified. Include:
- The comment text (summarized)
- The target skill file
- Whether a correction was applied or a proposal was queued
- Session date

---

## Evolution Registry Format

Template used when the registry is created for the first time:

```markdown
# Watchdog Evolution Registry

**Current watchdog version:** 5.0
**Total sessions monitored:** 0
**Sessions since last proposal:** 0
**Registry created:** [YYYY-MM-DD]
**Metacognitive runs:** 0
**False positive rate (last 10 sessions):** —
**Missed issue rate (last 10 sessions):** —

---

## Version History

| Version | Date | Sessions range | Summary |
|---|---|---|---|
| 5.0 | [YYYY-MM-DD] | 0→ | Initial v5.0 — forced Phase 5 close, Drive sync, Phase 9 (Active Skill Correction), Phase 10 (Weekly Report + Feedback Loop), Category C enhancements (C1–C11), AUTONOMY_TIER_MAX=3, EVOLUTION_TRIGGER=3 |
| 5.1 | [YYYY-MM-DD] | — | Phase 5.9 Slack DM notification (end-of-session), Phase 7b HTML dashboard auto-regeneration, tightened forced-close natural-end trigger |

---

## Cumulative Issue Metrics

| Category | INFO | WARN | FLAG | CRITICAL | Total |
|---|---|---|---|---|---|
| Naming Consistency | 0 | 0 | 0 | 0 | 0 |
| Spec vs Execution | 0 | 0 | 0 | 0 | 0 |
| Pipeline Integrity | 0 | 0 | 0 | 0 | 0 |
| Silent Failures | 0 | 0 | 0 | 0 | 0 |
| Truncation Risks | 0 | 0 | 0 | 0 | 0 |
| Claude Behavior | 0 | 0 | 0 | 0 | 0 |
| Context Integrity | 0 | 0 | 0 | 0 | 0 |
| Watchdog Self | 0 | 0 | 0 | 0 | 0 |
| Output Quality | 0 | 0 | 0 | 0 | 0 |
| Recovery Verification | 0 | 0 | 0 | 0 | 0 |

---

## Rule Effectiveness

| Rule ID | Name | Total fires | Last fired | Sessions since fire | Trend | Status |
|---|---|---|---|---|---|---|
| NC-01 | Name drift | 0 | — | 0 | — | Active |
| NC-02 | Terminology inconsistency | 0 | — | 0 | — | Active |
| NC-03 | File naming deviation | 0 | — | 0 | — | Active |
| NC-04 | Column/field casing drift | 0 | — | 0 | — | Active |
| SE-01 | Declared count mismatch | 0 | — | 0 | — | Active |
| SE-02 | Format change mid-pipeline | 0 | — | 0 | — | Active |
| SE-03 | Declared file never written | 0 | — | 0 | — | Active |
| SE-04 | Declared step never started | 0 | — | 0 | — | Active |
| SE-05 | Undeclared output written | 0 | — | 0 | — | Active |
| PI-01 | Step B before Step A confirmed | 0 | — | 0 | — | Active |
| PI-02 | Orphaned output | 0 | — | 0 | — | Active |
| PI-03 | Transformation chain break | 0 | — | 0 | — | Active |
| PI-04 | Steps out of order | 0 | — | 0 | — | Active |
| PI-05 | Dependency chain mismatch | 0 | — | 0 | — | Active |
| SF-01 | Silent exception catch | 0 | — | 0 | — | Active |
| SF-02 | Empty tool result unchecked | 0 | — | 0 | — | Active |
| SF-03 | Write without confirmation | 0 | — | 0 | — | Active |
| SF-04 | Batch without count check | 0 | — | 0 | — | Active |
| SF-05 | Missing null check | 0 | — | 0 | — | Active |
| SF-06 | Bash non-zero exit unhandled | 0 | — | 0 | — | Active |
| TR-01 | Unbounded dataset operation | 0 | — | 0 | — | Active |
| TR-02 | Large write unverified | 0 | — | 0 | — | Active |
| TR-03 | Context overflow risk | 0 | — | 0 | — | Active |
| TR-04 | Unbounded content generation | 0 | — | 0 | — | Active |
| CB-01 | Assumption drift | 0 | — | 0 | — | Active |
| CB-02 | Scope creep | 0 | — | 0 | — | Active |
| CB-03 | Hallucinated reference | 0 | — | 0 | — | Active |
| CB-04 | Write without read | 0 | — | 0 | — | Active |
| CB-05 | Instruction compliance gap | 0 | — | 0 | — | Active |
| CB-06 | Repeated identical tool call | 0 | — | 0 | — | Active |
| CB-07 | Tool call ratio anomaly | 0 | — | 0 | — | Active |
| CI-01 | Context compaction loss | 0 | — | 0 | — | Active |
| CI-02 | High context load | 0 | — | 0 | — | Active |
| CI-03 | Unverifiable prior reference | 0 | — | 0 | — | Active |
| WD-01 | Missed issue (found later) | 0 | — | 0 | — | Active |
| WD-02 | False positive (user dismissed) | 0 | — | 0 | — | Active |
| WD-03 | Over-sensitive CRITICAL | 0 | — | 0 | — | Active |
| WD-04 | Phase 5 registry write incomplete | 0 | — | 0 | — | Active |
| WD-05 | Informal format in own log | 0 | — | 0 | — | Active |
| OQ-01 | Structurally wrong output | 0 | — | 0 | — | Active |
| OQ-02 | File references non-existent file | 0 | — | 0 | — | Active |
| OQ-03 | Output size regression | 0 | — | 0 | — | Active |
| OQ-04 | Silent overwrite (prior session) | 0 | — | 0 | — | Active |
| RV-01 | CRITICAL with no recovery logged | 0 | — | 0 | — | Active |
| RV-02 | Auto-resolve without verification | 0 | — | 0 | — | Active |
| RV-03 | Implicit CRITICAL bypass | 0 | — | 0 | — | Active |

---

## Per-Skill Confidence Trend

| Skill | Sessions | Avg confidence | Last 5 scores | Trend |
|---|---|---|---|---|
| — | — | — | — | — |

---

## Session History

| Date | Skill | Duration | CRITICAL | FLAG | WARN | INFO | Confidence | Feedback |
|---|---|---|---|---|---|---|---|---|
| — | — | — | — | — | — | — | — | — |

---

## Watchdog Self-Health History

| Date | FP rate | Missed rate | Format compliance | Registry write rate | Self-mods |
|---|---|---|---|---|---|
| — | — | — | — | — | — |

---

## Pending Proposals

[None yet — run 5 monitored sessions (or trigger a quality signal) to generate the first proposals]

---

## Applied Improvements Log

[None yet]
```

---

## Per-Skill Baseline File Format

Template for `BASELINE_DIR/[skill-name].md`:

```markdown
# Skill Baseline: [skill-name]
**Created:** YYYY-MM-DD
**Last updated:** YYYY-MM-DD
**Sessions on record:** 0

## Confidence History

| Date | Overall | Spec | Pipeline | Silent | Truncation | Behavior | Issues | Notes |
|---|---|---|---|---|---|---|---|---|

## Computed Baselines

| Metric | 3-session avg | 5-session avg | All-time avg | Trend |
|---|---|---|---|---|
| Overall confidence | — | — | — | — |
| Spec compliance | — | — | — | — |
| Pipeline integrity | — | — | — | — |
| Silent failure risk | — | — | — | — |
| Truncation risk | — | — | — | — |
| Claude behavior | — | — | — | — |
| Issues per session | — | — | — | — |

## Anomaly Thresholds (auto-computed)

| Metric | Normal range | Anomaly threshold |
|---|---|---|
| Overall confidence | — | — |
| Issues per session | — | — |

## Persistent Weak Dimensions

[Populated by Phase 5b — dimensions scoring below 15/20 for 3+ consecutive sessions]

## Improving Dimensions

[Populated by Phase 5b]

## Most Fired Rules (for this skill)

| Rule ID | Name | Total fires | Fire rate |
|---|---|---|---|
```

---

## Logging Behavior

- All entries are **appended** to the log file in real time — never overwritten
- Log files are never deleted by the watchdog
- If `LOG_DIR` does not exist, create it before writing
- Each session produces exactly one log file (or resumes an existing partial one)
- The end-of-session summary is always the last section of the log file
- The Evolution Registry is read at session start (Phase 0) and written at session end (Phase 5)
- The Evolution Registry is never overwritten in full — only specific sections are updated
- Per-skill baseline files are updated at session end (Phase 5.3c)
- The Metacognitive Log is append-only — never overwritten

---

## General Behavior Notes

- The watchdog is **passive by default** — it observes and logs, never modifies skill behavior except in CRITICAL hard-stops and Tier 1/2 autonomous responses
- It infers from tool calls and declared specs — it does not read output files to verify their contents (this is a declared Watchdog Blind Spot)
- It does not slow down skill execution — log writes are brief and targeted
- It applies to any skill, not just SEO audits
- When loaded at session start without a specific skill name, it monitors the entire session
- The `WATCHDOG_VERSION` in Configuration must match the version in the Evolution Registry; if they differ, update the registry
- **Autonomy is bounded**: the watchdog will not take autonomous actions beyond `AUTONOMY_TIER_MAX`. Default (3) means it auto-resolves deterministic issues, auto-mitigates with notification, and may apply Phase 9 spec corrections when all confidence gates pass — but always escalates ambiguous or destructive decisions to the user
- **Self-modification is conservative**: autonomous self-modifications apply only additive, high-confidence changes. Any deletion or restructuring requires user approval via Phase 6
