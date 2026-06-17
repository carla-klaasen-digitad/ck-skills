---
name: crawl-vm-screaming-frog
description: Use when user wants to crawl a website with Screaming Frog, run a Screaming Frog crawl on the remote VM, audit a site with SF Spider, or mentions screaming frog, SF crawl, remote crawl, or VM crawl. Handles full workflow: SSH connection, crawl execution, monitoring, Slack notifications, result retrieval, and 429 error handling.
allowed-tools: Bash, Read, Write
---

# Crawl VM — Screaming Frog Remote Crawl

Manages Screaming Frog SEO Spider crawls on a remote VM via SSH. Handles connection, crawl execution, monitoring, Slack notifications, result retrieval, and error recovery.

## Arguments

`$ARGUMENTS` — The URL(s) to crawl (e.g., `https://www.example.com/`). Optional flags described below.

## VM Connection

- **IP**: `10.209.181.239`
- **User**: `digitad`
- **Password**: `Digitad`
- **Screaming Frog path**: `/Applications/Screaming Frog SEO Spider.app/Contents/MacOS/ScreamingFrogSEOSpiderLauncher`

Use `expect` to pass the password automatically for all SSH/SCP commands:

```bash
expect -c '
set timeout 300
spawn ssh -o StrictHostKeyChecking=no digitad@10.209.181.239 {COMMAND_HERE}
expect -re "assword:"
send "Digitad\r"
expect eof
'
```

**Important quoting rule**: Always wrap the remote command in `{}` braces inside expect to preserve spaces and special characters correctly.

## Pre-flight Checks

Run these checks in order before any crawl.

### 1. ZeroTier / VM Connectivity

Test SSH connectivity with a short timeout:

```bash
expect -c '
set timeout 10
spawn ssh -o StrictHostKeyChecking=no digitad@10.209.181.239 {echo OK}
expect {
  -re "assword:" { send "Digitad\r"; expect eof }
  timeout { puts "TIMEOUT"; exit 1 }
}
'
```

If connection fails, inform the user:
> La connexion SSH vers la VM (10.209.181.239) a échoué. Vérifie que ZeroTier est actif sur ta machine (`zerotier-cli status` ou ouvre l'app ZeroTier One).

### 2. Slack MCP Connectivity (BLOCKING)

Before any crawl, verify Slack MCP tools are available. If no Slack tools are found:

1. **STOP — do not launch the crawl.**
2. Inform the user:
   > Le MCP Slack n'est pas connecté. Le crawl ne peut pas être lancé sans Slack. Pour l'activer : tape `/mcp` dans Claude Code, puis connecte le serveur Slack via OAuth. Relance ensuite la commande.
3. Do NOT proceed unless the user explicitly says to skip Slack (e.g., "lance sans Slack", "skip Slack", `--no-slack`).

## Crawl Execution

### Output directory

- **VM**: `/tmp/sf-output/<domain>/` (extract domain from URL, strip `www.`)
- **Local**: `screaming-frog/output/<domain>/` (relative to project working directory)

### Default export tabs (complete set)

Unless the user specifies `--tabs-only` or `--quick`, always export ALL tabs:

```
Internal:All,Response Codes:All,Page Titles:All,Meta Description:All,H1:All,H2:All,Images:All,Canonicals:All,Structured Data:All,Links:All,Security:All,Hreflang:All,AMP:All,Sitemaps:All,Analytics:All,Search Console:All,Content:All,Custom Search:All,Custom Extraction:All
```

### Quick mode

If the user says `--quick` or "crawl rapide", export only:

```
Internal:All,Response Codes:All,Page Titles:All,Meta Description:All,H1:All
```

### Launch command

```bash
expect -c '
set timeout 300
spawn ssh -o StrictHostKeyChecking=no digitad@10.209.181.239 {mkdir -p /tmp/sf-output/<domain> && nohup "/Applications/Screaming Frog SEO Spider.app/Contents/MacOS/ScreamingFrogSEOSpiderLauncher" --headless --crawl "<URL>" --output-folder "/tmp/sf-output/<domain>" --export-tabs "<TABS>" > /tmp/sf-output/<domain>/crawl.log 2>&1 &}
expect -re "assword:"
send "Digitad\r"
expect eof
'
```

Always use `--headless` (required for CLI mode) and `nohup` to run in background.

## Slack Notifications

Channel: **#screamingfrog-vm** — ID: `C0AND2KTNKW`

### On crawl launch

Post to `C0AND2KTNKW` via `mcp__claude_ai_Slack__slack_send_message`:

```
Crawl de "<URL>" lancé. Heure de lancement: HH:MM
```

Use current time in `HH:MM` 24h format (from `date +%H:%M`).

### On crawl completion

Post to `C0AND2KTNKW` via `mcp__claude_ai_Slack__slack_send_message`:

```
Crawl de "<URL>" terminé. Heure de fin: HH:MM
```

### Slack tool usage

Use `mcp__claude_ai_Slack__slack_send_message` with `channel_id: "C0AND2KTNKW"` directly. Do NOT search for the channel — use the hardcoded ID.

## Monitoring & 429 Error Handling

After launching the crawl:

1. Wait 15 seconds, then check if the process is still running:
   ```bash
   expect -c '...' # ps aux | grep -i screaming on the VM
   ```
2. Periodically tail the crawl log:
   ```bash
   expect -c '...' # tail -30 /tmp/sf-output/<domain>/crawl.log
   ```
3. **If 429 errors appear in the log**:
   - Kill the crawl process on the VM
   - Relaunch with `--max-threads 1 --max-urls-per-second 1`
   - Inform the user that rate limiting was applied
4. Crawl is complete when log shows "Application Exited" or process is gone

## Result Retrieval

Once crawl is complete:

1. List exported files on VM: `ls -la /tmp/sf-output/<domain>/`
2. Create local directory: `mkdir -p screaming-frog/output/<domain>/`
3. SCP all CSVs to local:

```bash
expect -c '
set timeout 120
spawn scp -o StrictHostKeyChecking=no digitad@10.209.181.239:/tmp/sf-output/<domain>/*.csv screaming-frog/output/<domain>/
expect -re "assword:"
send "Digitad\r"
expect eof
'
```

4. Verify files arrived: `ls screaming-frog/output/<domain>/`
5. Present a summary table of exported files and sizes

## Final Output

After a successful crawl, report:

- **VM path**: `/tmp/sf-output/<domain>/`
- **Local path**: `screaming-frog/output/<domain>/`
- **Files table**: each CSV with its size
- **Crawl duration** (if discernible from logs)

## Optional Flags

| Flag | Effect |
|------|--------|
| `--quick` | Export only core tabs (Internal, Response Codes, Titles, Meta Desc, H1) |
| `--tabs-only "Tab1,Tab2"` | Export only specified tabs |
| `--config path/to/config` | Use a custom Screaming Frog config file |
| `--sitemap <url>` | Crawl from a sitemap URL instead |
| `--list <file>` | Crawl from a URL list file |
| `--reports "Report1,Report2"` | Generate additional reports |
| `--bulk-export "Export1"` | Run bulk exports |
| `--no-slack` | Skip Slack notifications (bypass the Slack pre-flight block) |
