# ck-skills

Claude Code skills for Digitad's SEO, content, and technical audit work — built and maintained by Carla Klaasen.

## Setup

Launch Claude Code from the repository root. Skills are loaded from `.claude/commands/` and resolve all internal paths relative to that root, so this repo works from any clone location — no machine-specific paths to edit.

Credentials (Google OAuth, API keys) go in a `.env` file at the repo root. Never commit `.env` — it's already gitignored.

## Structure

```
ck-skills/
├── .claude/commands/        ← active skills — this is what Claude Code actually loads
│   └── {skill-name}/
│       ├── SKILL.md         ← required — the skill definition
│       ├── README.md        ← optional — human-readable overview
│       └── scripts/         ← optional — helper scripts the skill shells out to
├── shared/
│   └── brand-guidelines/    ← one .md file per brand, shared across every skill
│                              that writes or reviews brand content
└── all_skills/
    ├── _archive/            ← retired/superseded skill copies, kept for history only
    └── session-skill-logs/  ← skill-watchdog runtime logs (gitignored)
```

**`.claude/commands/` is the only canonical source for skill definitions.** If you're looking for how a skill behaves, that's the one place to check — nothing else should duplicate it.

## Brand Guidelines

Brand voice, tone, vocabulary, and compliance rules live in `shared/brand-guidelines/`, one file per brand (e.g. `oikos.md`, `silk.md`), plus `general_legal.md` for off-site/guest-post legal rules.

Any skill that produces or reviews brand content reads from this directory — the `brand-context` skill is what auto-loads the right file the moment a brand name is mentioned in conversation. See `.claude/commands/brand-context/SKILL.md` for the full brand registry and matching rules.

To onboard a new brand, invoke `brand-context`'s onboarding interview rather than hand-writing a guidelines file — it keeps new files structurally consistent with the existing ones.

## Active Skills

| Skill | Purpose |
|---|---|
| `brand-context` | Auto-loads the right brand guidelines file whenever a brand is mentioned in a content task |
| `content-writing` | Generates on-page content, NeuronWriter briefs, and SEO-optimized copy with brand consistency |
| `digitad-tech-recommendations` | Produces client-facing technical recommendations Google Docs from SEO audit spreadsheets |
| `global-seo-skill` | Senior SEO/GEO knowledge base — keyword research, on-page rules, Core Web Vitals, schema mapping, GEO factors |
| `monthly-content-planner` | Runs the monthly on-site content brief workflow across all approved brands |
| `nw-enrich` | Enriches a Google Doc with NeuronWriter keyword/entity recommendations |
| `on-page-strategy` | Builds a prioritized on-page content production plan from keyword research |
| `redirection-plan-skill` | Builds a redirection plan for 404s, redirect chains, and canonical issues |
| `seo-geo-technical-audit` | Full technical + GEO/AI-visibility SEO audit workflow (123 scored elements across 6 phases) |
| `skill-creator` | Scaffolds new Agent Skills from templates |
| `skill-watchdog` | Passive background monitor for every other skill — spec compliance, naming consistency, silent failures |
| `translate-and-push-page` | Translates a source page to English and/or pushes structured content into a Google Doc template |

## Contributing / Editing Skills

- **No absolute paths.** Every path in a `SKILL.md` or script must be relative to the repo root (or use `~` for the user's home directory when a global, non-project path is genuinely intended, as in `skill-watchdog`'s global-shadow check). A hardcoded `/Users/yourname/...` path only works on your machine.
- **Don't duplicate a skill directory.** If a skill needs updating, edit it in place under `.claude/commands/`. Copies elsewhere in the repo will drift and it becomes unclear which one is authoritative.
- **Session-generated files don't belong in git.** Files a skill writes fresh each run (like `seo-geo-technical-audit`'s `audit-session-config.json`) should be gitignored, not committed — see the `.gitignore` for the pattern to follow.
