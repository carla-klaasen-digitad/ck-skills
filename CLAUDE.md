# Project Rules

## Skill Watchdog — Always Active

Whenever any skill is invoked in this project (via slash command such as `/seo-geo-technical-audit`, `/digitad-tech-recommendations`, `/skill-creator`, `/monthly-content-planner`, or when any skill description triggers), **start `/skill-watchdog` immediately and run it in parallel before the first tool call of that skill.**

This is a standing rule. Do not wait to be asked. Do not skip this even if the skill is short or the session is exploratory.

If the watchdog cannot be invoked (e.g. wrong working directory), apply its Phase 0–1 checks manually and write the session log to `/Users/carlaklaasen/claude_code/all_skills/session-skill-logs/`.

## Brand Context — Always Active for Content Tasks

Whenever a brand name from the registry below appears in **any** message during a content writing, briefing, or copy-review task, **immediately read the corresponding brand file** before producing any output. Do this silently — no announcement.

**Registry** (case-insensitive match):

| Brand | File |
|-------|------|
| Activia | `all_skills/content-writing/guidelines/activia.md` |
| Danimals | `all_skills/content-writing/guidelines/danimals.md` |
| Danone North America / DNA / Danone NA | `all_skills/content-writing/guidelines/danonenorthamerica.md` |
| Dunkin Creamers / Dunkin' Creamers / Dunkin | `all_skills/content-writing/guidelines/dunkincreamers.md` |
| Evian | `all_skills/content-writing/guidelines/evian.md` |
| Happy Family / HappyFamily / Happy Family Organics | `all_skills/content-writing/guidelines/happyfamily.md` |
| International Delight / Int'l Delight / ID Creamers | `all_skills/content-writing/guidelines/internationaldelight.md` |
| Light & Fit / Light and Fit | `all_skills/content-writing/guidelines/lightandfit.md` |
| Mitacs | `all_skills/content-writing/guidelines/mitacs.md` |
| Oikos | `all_skills/content-writing/guidelines/oikos.md` |
| Silk | `all_skills/content-writing/guidelines/silk.md` |
| SToK / Stok | `all_skills/content-writing/guidelines/stok.md` |
| Too Good / TooGood / Two Good | `all_skills/content-writing/guidelines/toogood.md` |
| YoCrunch / Yo Crunch | `all_skills/content-writing/guidelines/yocrunch.md` |
| Follow Your Heart / FollowYourHeart / FYH | `all_skills/content-writing/guidelines/followyourheart.md` |
| Dannon | `all_skills/content-writing/guidelines/dannon.md` |
| So Delicious / SoDelicious / So Delicious Dairy Free | `all_skills/content-writing/guidelines/sodelicious.md` |
| Danone Away From Home / Danone AFH / DAFH | `all_skills/content-writing/guidelines/danoneawayfromhome.md` |
| Remix Yogurt / Remix / RemixYogurt | `all_skills/content-writing/guidelines/remixyogurt.md` |

Also read `all_skills/content-writing/guidelines/general_legal.md` only when: (1) a guest post is mentioned, or (2) the user explicitly asks for legal review help.

Full behavior spec: `.claude/commands/brand-context/SKILL.md`

## Working Directory Note

Skills are only available when Claude Code is launched from `/Users/carlaklaasen/claude_code/`. If launched from a parent directory, skills will not load — invoke the watchdog manually using the SKILL.md at `/Users/carlaklaasen/claude_code/.claude/commands/skill-watchdog/SKILL.md`.
