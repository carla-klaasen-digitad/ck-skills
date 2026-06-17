# crawl-vm-screaming-frog

Runs Screaming Frog SEO Spider crawls on the DigitAd remote VM (10.209.181.239) via SSH. Handles the full workflow: pre-flight checks, crawl launch, progress monitoring, 429 error recovery, Slack notifications, and CSV retrieval.

## Requirements

- **ZeroTier** active on your machine (VM is on the ZeroTier network)
- **`expect`** installed locally (`brew install expect`)
- **Slack MCP** connected in Claude Code (`/mcp` → connect Slack)

## Quick Start

```
/crawl-vm-screaming-frog https://www.example.com/
```

## Examples

```
# Full crawl (all tabs)
/crawl-vm-screaming-frog https://www.oikos.com/

# Quick crawl (core tabs only)
/crawl-vm-screaming-frog https://www.oikos.com/ --quick

# Custom tabs
/crawl-vm-screaming-frog https://www.oikos.com/ --tabs-only "Internal:All,H1:All"

# Crawl from sitemap
/crawl-vm-screaming-frog https://www.oikos.com/ --sitemap https://www.oikos.com/sitemap.xml

# Skip Slack (testing)
/crawl-vm-screaming-frog https://www.oikos.com/ --no-slack
```

## Output

CSV exports are saved to `screaming-frog/output/<domain>/` in the current project directory.

## Slack Notifications

Posts start/end messages to **#screamingfrog-vm** (channel ID: `C0AND2KTNKW`).

## VM Details

| Setting | Value |
|---------|-------|
| IP | 10.209.181.239 |
| User | digitad |
| SF Path | `/Applications/Screaming Frog SEO Spider.app/Contents/MacOS/ScreamingFrogSEOSpiderLauncher` |
