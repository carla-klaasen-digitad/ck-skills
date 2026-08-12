# Project Rules

## Brand Context — Always Active for Content Tasks

Whenever a brand name from the registry below appears in **any** message during a content writing, briefing, or copy-review task, **immediately read the corresponding brand file** before producing any output. Do this silently — no announcement.

**Registry** (case-insensitive match). Load the USA file by default; also load the Canada file (where one exists) whenever the message indicates a Canada context (`.ca` domain, "Canada," "Canadian," "Quebec," French-language content, or an explicit Canada mention):

| Brand | USA File | Canada File |
|-------|------|------|
| Activia | `shared/brand-guidelines/activia.md` | `shared/brand-guidelines/activia_canada.md` |
| Danimals | `shared/brand-guidelines/danimals.md` | — |
| Danone North America / DNA / Danone NA | `shared/brand-guidelines/danonenorthamerica.md` | — |
| Danone Yogurt / Danino / Danone Creamy | — | `shared/brand-guidelines/danoneyogurt_canada.md` |
| Dunkin Creamers / Dunkin' Creamers / Dunkin | `shared/brand-guidelines/dunkincreamers.md` | — |
| Evian | `shared/brand-guidelines/evian.md` | — |
| Happy Family / HappyFamily / Happy Family Organics | `shared/brand-guidelines/happyfamily.md` | — |
| International Delight / Int'l Delight / ID Creamers | `shared/brand-guidelines/internationaldelight.md` | `shared/brand-guidelines/internationaldelight_canada.md` |
| Light & Fit / Light and Fit | `shared/brand-guidelines/lightandfit.md` | — |
| Mitacs | `shared/brand-guidelines/mitacs.md` | — |
| Oikos | `shared/brand-guidelines/oikos.md` | `shared/brand-guidelines/oikos_canada.md` |
| Silk | `shared/brand-guidelines/silk.md` | `shared/brand-guidelines/silk_canada.md` |
| SToK / Stok | `shared/brand-guidelines/stok.md` | — |
| Too Good / TooGood | `shared/brand-guidelines/toogood.md` | — (see note below — do not use for "Two Good") |
| YoCrunch / Yo Crunch | `shared/brand-guidelines/yocrunch.md` | — |
| Follow Your Heart / FollowYourHeart / FYH | `shared/brand-guidelines/followyourheart.md` | — |
| Dannon | `shared/brand-guidelines/dannon.md` | — |
| So Delicious / SoDelicious / So Delicious Dairy Free | `shared/brand-guidelines/sodelicious.md` | `shared/brand-guidelines/sodelicious_canada.md` |
| Danone Away From Home / Danone AFH / DAFH | `shared/brand-guidelines/danoneawayfromhome.md` | — |
| Remix Yogurt / Remix / RemixYogurt | `shared/brand-guidelines/remixyogurt.md` | — |

**Two Good vs. Too Good — do not conflate.** Canada source material describes a "Two Good Yogurt" (80% less sugar Greek yogurt) that is materially different from the USA "Too Good & Co." profile (60% less sugar, cultured ultra-filtered milk, pouches/creamers/yogurts). These may be two distinct real Danone brands incorrectly aliased together in this registry historically. If "Two Good" comes up for Canada, do not use `toogood.md` or assume it's the same brand — flag to the user and ask before proceeding.

Also read the market-appropriate legal file for every content task: `shared/brand-guidelines/general_legal.md` (USA on-site) or `shared/brand-guidelines/general_legal_canada.md` (Canada on-site) always; for guest-post/off-site tasks read `shared/brand-guidelines/off-site/general_danoneusa.md` or `off-site/general_danonecanada.md` instead.

Full behavior spec: `.claude/commands/brand-context/SKILL.md`

## Working Directory Note

Skills are only available when Claude Code is launched from the repository root (this file's directory). If launched from a parent directory, skills will not load — invoke the watchdog manually using the SKILL.md at `.claude/commands/skill-watchdog/SKILL.md` (relative to the repo root).
