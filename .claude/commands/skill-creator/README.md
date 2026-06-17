# Skill Creator

A meta-skill for creating new Agent Skills in Claude Code. Generate skills through an interactive wizard or start from pre-built templates.

## Quick Start

1. **Install** this plugin:
   ```
   /plugin install nibzard/skills-marketplace
   ```

2. **Create a skill**:
   ```
   Create a skill for reviewing pull requests
   ```

3. **Answer questions** about your skill:
   - Name (kebab-case)
   - What it does
   - When to use it
   - Tool permissions needed

4. **Skill is created** in your chosen location with all necessary files

## Features

### Three Creation Modes

1. **Interactive Wizard**: Build from scratch through guided Q&A
2. **Template-Based**: Start from pre-built templates (PR reviewer, API caller, etc.)
3. **Hybrid**: Template foundation + customization

### Five Skill Templates

| Template | Purpose |
|----------|---------|
| `pr-reviewer` | Review pull requests against team standards |
| `commit-helper` | Generate commit messages from diffs |
| `api-caller` | Integrate with external APIs |
| `code-analyzer` | Analyze code quality and patterns |
| `data-processor` | Process CSV/JSON/YAML data files |

### Flexible Deployment

- **Personal**: `~/.claude/skills/` - Just for you
- **Project**: `.claude/skills/` - Shared with your team
- **Standalone**: Portable plugin structure - For distribution

## Usage Examples

### Interactive Mode

```
Create a skill that helps me write better documentation
```

Skill creator will ask:
1. Skill name: `doc-writer`
2. Purpose: Help write clear, concise documentation
3. Triggers: "write docs", "document this", "help with documentation"
4. Tools: Read, Write, Edit
5. Type: With Examples
6. Location: Personal

Result: A complete skill with SKILL.md, plugin.json, README.md, and examples.md

### Template Mode

```
Create a skill from the api-caller template for the Stripe API
```

Result: An API caller skill pre-configured for Stripe with authentication, endpoints, and error handling.

### Hybrid Mode

```
Create a PR reviewer skill but customized for Python code
```

Result: The pr-reviewer template adapted with Python-specific checks (PEP 8, type hints, etc.).

## Generated Skill Structure

Every generated skill includes:

```
your-skill/
├── SKILL.md                    # Main skill file with frontmatter
├── .claude-plugin/
│   └── plugin.json             # Skill metadata
├── README.md                   # Documentation
└── examples.md                 # Usage examples
```

Optional additions based on skill type:
- `scripts/` - Helper Python/bash scripts
- `reference.md` - Technical documentation
- `templates/` - Reusable templates

## Best Practices

### Write Good Descriptions

The `description` field in SKILL.md frontmatter is critical - it's how Claude knows when to use your skill.

**Good**:
```yaml
description: Review pull requests against team coding standards. Use when reviewing code, checking PR quality, or when user mentions pull request, PR review, or code review.
```

**Bad**:
```yaml
description: Helps with code reviews
```

### Request Minimal Tools

Only request tools your skill actually needs:

```yaml
# Good - specific, minimal
allowed-tools: Read, Grep, Glob

# Bad - overly broad
allowed-tools: Read, Write, Edit, Bash, Grep, Glob
```

### Use Progressive Disclosure

Keep SKILL.md focused. Put detailed reference material in supporting files:

```
SKILL.md          # Core workflow, when to use
├── reference.md  # Detailed API docs
└── examples.md   # Complete walkthroughs
```

## Templates Reference

### pr-reviewer.md

Reviews pull requests with structured feedback. Checks:
- Code quality and style
- Test coverage
- Documentation completeness
- Security issues
- Performance concerns

### commit-helper.md

Generates conventional commit messages. Supports:
- Feat, fix, docs, style, refactor, test, chore types
- Summary and body format
- Issue references
- Breaking change notices

### api-caller.md

Integrates with external APIs. Handles:
- Multiple auth methods (API key, OAuth, bearer token)
- Rate limiting with backoff
- Error handling and retries
- Response parsing

### code-analyzer.md

Analyzes code quality. Detects:
- Code smells (long functions, deep nesting)
- Maintainability issues
- Security vulnerabilities
- Performance problems

### data-processor.md

Processes structured data. Supports:
- CSV, JSON, YAML input/output
- Schema validation
- Data transformation
- Large file handling (streaming)

## Requirements

- Claude Code with plugin support
- No external dependencies

## Contributing

This skill is part of the [skills-marketplace](https://github.com/nibzard/skills-marketplace) collection. Contributions welcome!

## License

MIT

## Author

nibzard - [GitHub](https://github.com/nibzard)

## See Also

- [Agent Skills Documentation](https://code.claude.com/docs/en/agents-and-tools/agent-skills)
- [Skills Best Practices](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/best-practices)
- [skills-marketplace](https://github.com/nibzard/skills-marketplace)
