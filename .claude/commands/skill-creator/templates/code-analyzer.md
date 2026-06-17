---
name: code-analyzer
description: Analyze code quality, detect patterns, and suggest improvements. Use when reviewing code, checking quality, or when user mentions code analysis, quality check, or code review.
allowed-tools: Read, Grep, Glob
---

# Code Analyzer

Analyzes code quality, detects patterns and anti-patterns, and provides actionable improvement suggestions.

## When This Skill Activates

- User asks to "analyze this code", "check code quality", "review codebase"
- User mentions "code analysis", "quality check", "code smells", "anti-patterns"
- User wants to understand code health or find issues

## Analysis Workflow

### Step 1: Identify Analysis Scope

Ask the user:
- **Target**: Single file, directory, or entire codebase?
- **Focus**: Security, performance, maintainability, or all?
- **Language**: What language(s) should be analyzed?

### Step 2: Scan Code Structure

```bash
# Find all source files
find . -name "*.py" -o -name "*.js" -o -name "*.ts"

# Get file statistics
find . -name "*.py" | xargs wc -l | sort -n

# Find large files (potential code smell)
find . -name "*.py" -size +100k
```

### Step 3: Analyze Code Quality

Check for these common issues:

#### Code Smells
- [ ] **Long functions**: Functions > 50 lines
- [ ] **Large files**: Files > 500 lines
- [ ] **Deep nesting**: Nesting > 4 levels
- [ ] **High complexity**: Cyclomatic complexity > 10
- [ ] **Duplicate code**: Similar logic in multiple places

#### Maintainability Issues
- [ ] **Magic numbers**: Unexplained numeric literals
- [ ] **Poor naming**: Single-letter variables, unclear names
- [ ] **Long parameter lists**: > 4 parameters
- [ ] **God objects**: Classes doing too much
- [ ] **Feature envy**: Methods using other classes more than their own

#### Security Concerns
- [ ] **Hardcoded secrets**: API keys, passwords
- [ ] **SQL injection**: Unsanitized input in queries
- [ ] **Command injection**: Unsanitized input in system calls
- [ ] **XSS vulnerabilities**: Unescaped output
- [ ] **Insecure dependencies**: Outdated packages

#### Performance Issues
- [ ] **N+1 queries**: Database calls in loops
- [ ] **Inefficient algorithms**: O(n²) where O(n) possible
- [ ] **Memory leaks**: Unclosed resources, circular references
- [ ] **Unnecessary IO**: Redundant file/network operations

### Step 4: Generate Analysis Report

Format findings as:

```markdown
## Code Analysis Report

### Summary
- Total files analyzed: [count]
- Total lines of code: [count]
- Languages: [list]
- Overall health: [Good / Fair / Poor]

### Critical Issues
[Potential bugs, security vulnerabilities]

### Warnings
[Code smells, maintainability concerns]

### Suggestions
[Improvements, refactoring opportunities]

### Metrics
| File | LOC | Complexity | Issues |
|------|-----|------------|--------|
| file1.py | 250 | 8 | 3 |
| file2.py | 450 | 15 | 7 |
```

### Step 5: Provide Actionable Recommendations

For each issue found, provide:

1. **Problem**: What's wrong and why it matters
2. **Location**: File and line number
3. **Fix**: Specific code change or refactor suggestion
4. **Priority**: Critical / High / Medium / Low

Example:

```markdown
### Issue: Hardcoded API Secret

**Priority**: Critical
**Location**: `src/api.py:23`

**Problem**: API key is hardcoded in source code. If this code is shared or committed, the secret will be exposed.

**Fix**:
```python
# Before
API_KEY = "sk_live_1234567890"

# After
import os
API_KEY = os.getenv("API_KEY")
if not API_KEY:
    raise ValueError("API_KEY environment variable required")
```

Add to `.env`:
```
API_KEY=sk_live_1234567890
```
```

## Analysis Patterns

### Language-Specific Checks

#### Python
- Check for `__pycache__` in version control
- Verify `requirements.txt` or `pyproject.toml` exists
- Look for missing type hints
- Check for improper exception handling (bare `except:`)

#### JavaScript/TypeScript
- Check for `var` usage (prefer `const`/`let`)
- Look for missing error handling in async functions
- Verify `package.json` scripts are complete
- Check for missing `await` keywords

#### General
- Inconsistent indentation
- Missing error handling
- Unused imports/variables
- TODO/FIXME comments that need attention

## Examples

See [examples.md](examples.md) for sample analysis reports.

## Troubleshooting

### Too Many Results
- Focus on high-priority issues first
- Filter by file or directory
- Exclude vendor/node_modules directories

### False Positives
- Adjust analysis rules for your codebase
- Add exclusions for specific patterns
- Context matters - some "smells" are intentional

### Can't Identify Issues
- Check if file is excluded from analysis
- Verify file is a supported language
- Ensure file is not minified or compiled
