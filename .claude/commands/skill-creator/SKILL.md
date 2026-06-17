---
name: skill-creator
description: Create new Agent Skills interactively or from templates. Use when user wants to create, generate, scaffold, or build a new skill, or mentions creating skills, writing skills, skill templates, skill development.
allowed-tools: Read, Write, Edit
---

# Skill Creator

Creates new Agent Skills through interactive wizard or template-based generation. A meta-skill for bootstrapping Claude Code capabilities.

## When This Skill Activates

- User asks to "create a skill", "make a skill", "generate a skill", "scaffold a skill"
- User mentions "skill template", "new skill", "custom skill", "skill development"
- User wants to extend Claude with custom capabilities or workflows
- User asks about building, authoring, or writing skills

## Workflow

### Step 1: Choose Mode

Ask the user which mode they prefer:

1. **Interactive Wizard**: Guided Q&A to build a skill from scratch
2. **Template-Based**: Start from a pre-built template and customize
3. **Hybrid**: Template foundation + interactive customization

### Step 2: Gather Requirements (Interactive Mode)

Ask these questions in order:

1. **Skill Name**: What should the skill be called? (kebab-case, max 64 chars)
2. **Purpose**: What does this skill do? (one sentence)
3. **Trigger Phrases**: When should Claude use this skill? (list 3-5 specific phrases users might say)
4. **Tool Permissions**: Which tools does the skill need? (Read, Write, Edit, Bash, Grep, Glob - request minimal)
5. **Skill Type**:
   - Simple: Single SKILL.md only
   - With Scripts: SKILL.md + Python/bash helper scripts
   - With Reference: SKILL.md + reference.md for technical docs
   - With Examples: SKILL.md + examples.md for use cases
   - Complex: All of the above
6. **Target Location**:
   - Personal: `~/.claude/skills/` (just for you)
   - Project: `.claude/skills/` (shared with team)
   - Standalone: Portable plugin structure (for distribution)

### Step 3: Select Template (Template Mode)

Available templates in `templates/`:

| Template | Purpose | Best For |
|----------|---------|----------|
| `pr-reviewer` | Review pull requests against standards | Teams with code review workflows |
| `commit-helper` | Generate commit messages from diffs | Projects with commit conventions |
| `api-caller` | Call external APIs with auth | Integrations with external services |
| `code-analyzer` | Analyze code quality and patterns | Codebases needing quality checks |
| `data-processor` | Process CSV/JSON data files | Data transformation workflows |

### Step 4: Generate Core Files

Always generate:

1. **SKILL.md** - Complete with:
   - YAML frontmatter (name, description, allowed-tools)
   - When This Skill Activates section
   - Main workflow/instructions
   - Examples section
   - Troubleshooting section

2. **.claude-plugin/plugin.json** - With:
   - Skill name and version
   - Description matching SKILL.md
   - Author info (prompt for name/email)
   - License (default: MIT)

3. **README.md** - With:
   - Skill overview
   - Installation instructions
   - Quick start example
   - Requirements

4. **examples.md** (if skill type includes it) - With:
   - 2-3 complete usage examples
   - Input/output samples
   - Common scenarios

Conditionally generate:

- **scripts/** directory for automation skills
- **reference.md** for technical/API skills
- **templates/** for generator skills

### Step 5: Validate Before Writing

Before creating files, validate:

- [ ] Name is kebab-case (lowercase letters, numbers, hyphens only)
- [ ] Name is <= 64 characters
- [ ] Description is <= 1024 characters
- [ ] Description includes specific trigger phrases
- [ ] Tool permissions are minimal (don't request tools the skill won't use)
- [ ] YAML frontmatter is valid (proper `---` delimiters)
- [ ] File paths use forward slashes

### Step 6: Create Files

Use Write tool to create files in the selected location.

For target location = "standalone", create full plugin structure:
```
skill-name/
├── SKILL.md
├── .claude-plugin/
│   └── plugin.json
├── README.md
└── examples.md
```

### Step 7: Verification

After creating files, tell the user:

1. Where files were created
2. How to verify the skill works:
   - `What Skills are available?` should list the new skill
   - Test with a query matching the description
3. Next steps (edit SKILL.md to customize, test with example queries)

## Template Details

### pr-reviewer.md
Reviews pull requests against team standards. Checks for common issues, provides structured feedback format, integrates with git workflow.

### commit-helper.md
Generates conventional commit messages from git diffs. Supports custom commit conventions, formats summaries and body, handles commit types.

### api-caller.md
Integrates with external APIs. Handles authentication (API keys, OAuth), rate limiting, error responses, request/response parsing.

### code-analyzer.md
Analyzes code quality. Detects anti-patterns, suggests improvements, generates quality reports, supports multiple languages.

### data-processor.md
Processes data files (CSV, JSON, YAML). Validates schemas, transforms data, handles large files, generates outputs.

## Best Practices for Generated Skills

### Description Writing
- Start with "Use when..." for clarity
- Include 3-5 specific trigger scenarios
- Mention what makes this skill unique
- Keep under 1024 characters

### Tool Permissions
- Request only necessary tools
- Use specific constraints (e.g., `Bash(python:*)`)
- Explain why each tool is needed

### Progressive Disclosure
- Keep SKILL.md focused (under 500 lines)
- Reference supporting files for deep details
- Don't duplicate content across files

## Common Patterns

### Skill with Scripts
When a skill needs helper scripts:

```markdown
## Utility Scripts

This skill includes helper scripts for complex operations:

```bash
# Validate input
python scripts/validate.py input.txt

# Transform data
python scripts/transform.py input.csv output.json
```
```

### Skill with Reference
For technical/API skills, reference detailed docs:

```markdown
## Technical Reference

For complete API details, see [reference.md](reference.md).
```

### Skill with Environment Variables
If the skill needs environment setup:

```markdown
## Requirements

Set these environment variables:
- `API_KEY`: Your service API key
- `ENDPOINT`: API endpoint URL

Install dependencies:
```bash
pip install requests pydantic
```
```

## Troubleshooting

### Skill Not Appearing
- Verify SKILL.md path is correct
- Check YAML frontmatter is valid
- Run `claude --debug` to see loading errors

### Description Not Triggering
- Add more specific trigger phrases
- Include keywords users would naturally say
- Test with different query phrasings

### Validation Errors
- Check name is kebab-case only
- Verify description length < 1024 chars
- Ensure YAML has proper `---` delimiters

## Examples

See [examples.md](examples.md) for complete walkthroughs of creating skills in each mode.
