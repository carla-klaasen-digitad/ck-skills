# Project Rules

## Brand Context — Always Active for Content Tasks

Whenever a brand name from the registry below appears in **any** message during a content writing, briefing, or copy-review task, **immediately read the corresponding brand file** before producing any output. Do this silently — no announcement.

**Registry** (case-insensitive match):

| Brand | File |
|-------|------|
| Activia | `shared/brand-guidelines/activia.md` |
| Danimals | `shared/brand-guidelines/danimals.md` |
| Danone North America / DNA / Danone NA | `shared/brand-guidelines/danonenorthamerica.md` |
| Dunkin Creamers / Dunkin' Creamers / Dunkin | `shared/brand-guidelines/dunkincreamers.md` |
| Evian | `shared/brand-guidelines/evian.md` |
| Happy Family / HappyFamily / Happy Family Organics | `shared/brand-guidelines/happyfamily.md` |
| International Delight / Int'l Delight / ID Creamers | `shared/brand-guidelines/internationaldelight.md` |
| Light & Fit / Light and Fit | `shared/brand-guidelines/lightandfit.md` |
| Mitacs | `shared/brand-guidelines/mitacs.md` |
| Oikos | `shared/brand-guidelines/oikos.md` |
| Silk | `shared/brand-guidelines/silk.md` |
| SToK / Stok | `shared/brand-guidelines/stok.md` |
| Too Good / TooGood / Two Good | `shared/brand-guidelines/toogood.md` |
| YoCrunch / Yo Crunch | `shared/brand-guidelines/yocrunch.md` |
| Follow Your Heart / FollowYourHeart / FYH | `shared/brand-guidelines/followyourheart.md` |
| Dannon | `shared/brand-guidelines/dannon.md` |
| So Delicious / SoDelicious / So Delicious Dairy Free | `shared/brand-guidelines/sodelicious.md` |
| Danone Away From Home / Danone AFH / DAFH | `shared/brand-guidelines/danoneawayfromhome.md` |
| Remix Yogurt / Remix / RemixYogurt | `shared/brand-guidelines/remixyogurt.md` |

Also read `shared/brand-guidelines/general_legal.md` only when: (1) a guest post is mentioned, or (2) the user explicitly asks for legal review help.

Full behavior spec: `.claude/commands/brand-context/SKILL.md`

## Working Directory Note

Skills are only available when Claude Code is launched from the repository root (this file's directory). If launched from a parent directory, skills will not load — invoke the watchdog manually using the SKILL.md at `.claude/commands/skill-watchdog/SKILL.md` (relative to the repo root).
