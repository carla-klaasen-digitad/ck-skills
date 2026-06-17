---
name: pr-reviewer
description: Review pull requests against team standards. Use when reviewing code, checking PR quality, validating changes, or when user mentions pull request, PR review, code review, or merge request.
allowed-tools: Read, Bash
---

# PR Reviewer

Reviews pull requests against team coding standards, checks for common issues, and provides structured feedback.

## When This Skill Activates

- User asks to "review this PR", "check the pull request", "review these changes"
- User mentions "PR review", "code review", "merge request", "validate changes"
- User wants feedback on a pull request or merge request

## Review Workflow

### Step 1: Get PR Context

Run these commands to understand the PR:

```bash
# Get PR diff
git diff main...HEAD

# Get commit messages
git log main..HEAD --oneline

# Get changed files
git diff main...HEAD --name-only
```

### Step 2: Review Checklist

Check each of these areas:

#### Code Quality
- [ ] Code follows team style guide
- [ ] No obvious bugs or logic errors
- [ ] Error handling is appropriate
- [ ] Edge cases are handled

#### Testing
- [ ] New code has tests
- [ ] Tests cover edge cases
- [ ] Tests are readable and maintainable

#### Documentation
- [ ] Complex functions have comments
- [ ] README/API docs updated if needed
- [ ] Changes are self-documenting with clear names

#### Security
- [ ] No hardcoded secrets or credentials
- [ ] Input validation on user data
- [ ] No SQL injection/XSS vulnerabilities
- [ ] Proper authentication/authorization checks

#### Performance
- [ ] No obvious performance regressions
- [ ] Database queries are optimized
- [ ] No unnecessary loops or expensive operations

### Step 3: Provide Structured Feedback

Format feedback as:

```markdown
## PR Review: [PR Title]

### Summary
[Brief summary of changes]

### ✅ Strengths
- [What's done well]

### 🔴 Issues
[Critical issues that should block merge]

### ⚠️ Suggestions
[Improvements that are optional but recommended]

### 💡 Nitpicks
[Minor style or preference items]

### Overall Assessment
[Ready to merge / Needs changes / Major concerns]
```

### Step 4: Run Automated Checks

If your project has automated tools, run them:

```bash
# Linting
npm run lint  # or your project's equivalent

# Tests
npm test      # or your project's equivalent

# Type checking
npm run type-check  # or your project's equivalent
```

## Team Standards

Customize this section with your team's specific standards:

- Language: [Your primary language]
- Style guide: [Link to your style guide]
- Test coverage requirement: [e.g., 80%]
- Approval policy: [e.g., 1 reviewer required]

## Examples

See [examples.md](examples.md) for sample PR reviews.

## Troubleshooting

### Can't see PR changes
- Ensure you're on the correct branch
- Check that `main...HEAD` is the correct diff target
- Use `git branch --show-current` to verify

### Review feels incomplete
- Request more context from the PR author
- Ask for the related issue/ticket
- Request a walkthrough of complex changes
