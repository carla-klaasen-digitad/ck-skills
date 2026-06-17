---
name: commit-helper
description: Generate clear commit messages from git diffs. Use when writing commit messages, reviewing staged changes, or when user mentions commit, commit message, or git commit.
allowed-tools: Read, Bash
---

# Commit Helper

Generates clear, conventional commit messages by analyzing staged changes.

## When This Skill Activates

- User asks to "write a commit message", "generate commit message", "help with commit"
- User mentions "commit message", "git commit", "staged changes"
- User wants to commit changes but isn't sure what to write

## Commit Workflow

### Step 1: Analyze Staged Changes

```bash
# Get the diff of staged changes
git diff --staged

# See which files changed
git diff --staged --name-only

# See the diff stats
git diff --staged --stat
```

### Step 2: Generate Commit Message

Based on the changes, generate a commit message following this format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

#### Type Options
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks
- `perf`: Performance improvements

#### Subject (summary line)
- Use present tense ("add" not "added")
- Use imperative mood ("add" not "adds")
- Don't capitalize first letter
- No period at end
- Max 50 characters

#### Body (detailed explanation)
- Explain what and why, not how
- Wrap at 72 characters
- Use present tense
- Each line on its own bullet

#### Footer
- Reference issues: `Closes #123`
- Breaking changes: `BREAKING CHANGE: <description>`

### Step 3: Present Options

Show the user 2-3 commit message options:

```markdown
## Commit Message Options

### Option 1 (Concise)
```
feat(auth): add OAuth2 login support

Implements login via Google and GitHub OAuth2 providers.
```

### Option 2 (Detailed)
```
feat(auth): add OAuth2 login support

Implements login via Google and GitHub OAuth2 providers:

- Add OAuth2 callback endpoint
- Store OAuth tokens securely
- Update user model to support OAuth

Closes #45
```

Which option would you like to use, or should I refine further?
```

## Best Practices

### DO
- Focus on what changed and why
- Keep summary under 50 characters
- Use conventional commit format
- Reference related issues

### DON'T
- Include implementation details in body
- Use past tense
- Start with capital letter
- End summary with period

## Examples

See [examples.md](examples.md) for more commit message examples.

## Troubleshooting

### No staged changes
- Run `git status` to see if files are staged
- Run `git add` to stage files first
- Check that you're on the correct branch

### Summary too long
- Focus on the main change
- Move details to body
- Remove filler words

### Not sure about type
- `feat` for user-facing changes
- `fix` for bug fixes
- `refactor` for internal restructuring
