# Skill Creator Examples

Complete walkthroughs showing how to create new skills using the skill-creator.

## Example 1: Interactive Wizard - Creating a Custom Skill

**User**: "I want to create a skill that helps me write SQL queries"

**Claude** (using skill-creator):

Let me help you create a SQL query helper skill! I'll ask you a few questions to build it.

### Step 1: Skill Name

What should this skill be called? (Use kebab-case like `sql-helper`)

**User**: `sql-query-builder`

### Step 2: Purpose

What does this skill do in one sentence?

**User**: "It helps me write SQL queries by understanding my schema and suggesting query patterns"

### Step 3: Trigger Phrases

When should Claude use this skill? List 3-5 phrases:

**User**:
- "write a SQL query"
- "query the database"
- "SQL select statement"
- "get data from table"

### Step 4: Tool Permissions

Which tools does this skill need?

**User**: "Just Read to see schema files, maybe Bash to run queries"

### Step 5: Skill Type

What kind of skill is this?

**User**: "With Reference - I want to document SQL patterns"

### Step 6: Target Location

Where should I create this skill?

**User**: "Personal - just for me in ~/.claude/skills/"

### Generated Files

I'll create the skill now:

```yaml
---
name: sql-query-builder
description: Write SQL queries by understanding database schema. Use when user asks to write SQL queries, query database, select from table, or mentions SQL, database query, or data retrieval.
allowed-tools: Read, Bash
---
```

Files created:
- `~/.claude/skills/sql-query-builder/SKILL.md`
- `~/.claude/skills/sql-query-builder/.claude-plugin/plugin.json`
- `~/.claude/skills/sql-query-builder/README.md`
- `~/.claude/skills/sql-query-builder/reference.md`

**Verification**: Test with "Write a SQL query to get all users who signed up this week"

---

## Example 2: Template-Based Generation

**User**: "Create a skill from the pr-reviewer template for my team"

**Claude** (using skill-creator):

I'll create a PR reviewer skill from the template. Let me customize it for your team.

### Template: pr-reviewer

I'll use the PR reviewer template as a foundation. A few questions to customize it:

1. **What programming language does your team use?**
   **User**: "TypeScript"

2. **What's your team's style guide?**
   **User**: "We use Airbnb TypeScript guide"

3. **Any specific rules to check?**
   **User**: "No any types, maximum 2 function parameters, always use async/await"

4. **Where should this skill live?**
   **User**: "Project - in .claude/skills/ so the team can use it"

### Generated Skill

Created with custom rules:

```markdown
## Team Standards

- Language: TypeScript
- Style guide: [Airbnb TypeScript Style Guide](https://github.com/airbnb/typescript)
- No `any` types allowed
- Maximum 2 function parameters (use objects for more)
- Always use async/await, never .then() chains
- Test coverage requirement: 80%
```

Files created:
- `.claude/skills/pr-reviewer/SKILL.md`
- `.claude/skills/pr-reviewer/.claude-plugin/plugin.json`
- `.claude/skills/pr-reviewer/README.md`
- `.claude/skills/pr-reviewer/examples.md`

---

## Example 3: Hybrid - Template + Customization

**User**: "I want an API caller skill but customized for GitHub API"

**Claude** (using skill-creator):

I'll start with the api-caller template and customize it for GitHub.

### Base Template: api-caller

Customizing for GitHub API integration:

1. **GitHub-specific authentication**: Personal Access Token
2. **Key endpoints**: Issues, Pull Requests, Repositories
3. **Rate limiting**: GitHub's 5000/hour limit
4. **Error handling**: GitHub-specific error responses

### Generated Skill

The template is adapted:

```python
class GitHubAPI:
    def __init__(self, token: str):
        self.token = token
        self.base_url = "https://api.github.com"
        self.session.headers.update({
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        })

    def get_issues(self, repo: str, state: str = "open"):
        """Get issues for a repository."""
        return self._request(
            "GET",
            f"repos/{repo}/issues",
            params={"state": state}
        )

    def create_issue(self, repo: str, title: str, body: str):
        """Create a new issue."""
        return self._request(
            "POST",
            f"repos/{repo}/issues",
            json={"title": title, "body": body}
        )
```

Files created:
- `~/.claude/skills/github-api/SKILL.md`
- `~/.claude/skills/github-api/.claude-plugin/plugin.json`
- `~/.claude/skills/github-api/README.md`
- `~/.claude/skills/github-api/scripts/github_client.py`

---

## Example 4: Standalone Plugin Structure

**User**: "Create a skill I can share as a plugin"

**Claude** (using skill-creator):

I'll create a portable plugin structure for distribution.

### Skill: Commit Message Generator

Creating a full plugin with marketplace-ready structure:

```
commit-helper/
├── SKILL.md
├── .claude-plugin/
│   └── plugin.json
├── README.md
├── examples.md
└── skills/
    └── commit-helper/
        └── (same structure for nested skill)
```

This structure can be:
1. Committed to a GitHub repository
2. Published as a standalone plugin
3. Added to a marketplace bundle

Files created:
- `skills/commit-helper/SKILL.md`
- `skills/commit-helper/.claude-plugin/plugin.json`
- `skills/commit-helper/README.md`
- `skills/commit-helper/examples.md`
- `skills/commit-helper/skills/commit-helper/` (nested copy)

---

## Example 5: Complex Skill with Scripts

**User**: "Create a skill for processing logs and finding errors"

**Claude** (using skill-creator):

I'll create a complex skill with helper scripts.

### Skill: Log Analyzer

Creating with automation scripts:

**SKILL.md** - Instructions for Claude
**scripts/parse_log.py** - Python script to parse log files
**scripts/extract_errors.py** - Extract error messages
**scripts/summarize.py** - Generate summary statistics

### Script: parse_log.py

```python
#!/usr/bin/env python3
import re
from pathlib import Path

def parse_log_file(log_path: Path):
    """Parse log file and return structured data."""
    error_pattern = re.compile(r'ERROR: (.+)')
    warning_pattern = re.compile(r'WARNING: (.+)')

    errors = []
    warnings = []

    with open(log_path) as f:
        for line in f:
            if match := error_pattern.search(line):
                errors.append(match.group(1))
            if match := warning_pattern.search(line):
                warnings.append(match.group(1))

    return {
        "errors": errors,
        "warnings": warnings,
        "error_count": len(errors),
        "warning_count": len(warnings),
    }
```

Files created:
- `~/.claude/skills/log-analyzer/SKILL.md`
- `~/.claude/skills/log-analyzer/.claude-plugin/plugin.json`
- `~/.claude/skills/log-analyzer/README.md`
- `~/.claude/skills/log-analyzer/scripts/parse_log.py`
- `~/.claude/skills/log-analyzer/scripts/extract_errors.py`
- `~/.claude/skills/log-analyzer/scripts/summarize.py`

---

## Testing Generated Skills

After creating any skill, test it:

1. **Verify discovery**:
   ```
   What Skills are available?
   ```

2. **Test activation** with a query matching your description:
   ```
   [Query that should trigger the skill]
   ```

3. **Verify functionality**:
   - Does Claude ask to use the skill?
   - Does the skill produce expected results?
   - Are all files correctly formatted?

4. **Iterate**: Edit SKILL.md to refine behavior based on testing.
