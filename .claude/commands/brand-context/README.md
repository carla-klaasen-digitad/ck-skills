# brand-context

Automatically loads the correct brand writing guidelines whenever a brand name appears in a content task. Runs silently — no announcement, no setup required.

## How It Works

The moment you mention a brand name in any content, briefing, or copy task, this skill reads that brand's `.md` guidelines file and applies it as an active constraint for the rest of the task.

## Supported Brands

| Brand | Key |
|-------|-----|
| Activia | activia |
| Danimals | danimals |
| Dannon | dannon |
| Danone Away From Home | danoneawayfromhome |
| Danone North America | danonenorthamerica |
| Dunkin Creamers | dunkincreamers |
| Evian | evian |
| Follow Your Heart | followyourheart |
| Happy Family | happyfamily |
| International Delight | internationaldelight |
| Light & Fit | lightandfit |
| Oikos | oikos |
| Remix Yogurt | remixyogurt |
| Silk | silk |
| So Delicious | sodelicious |
| SToK | stok |
| Too Good | toogood |
| YoCrunch | yocrunch |

Brand guidelines live in `all_skills/content-writing/guidelines/`.

## Auto-Trigger (no slash command needed)

Just mention a brand name in any content task:

```
Write a product page for Oikos Triple Zero Vanilla
```

```
Review this copy for Silk Oat Milk — does it match brand voice?
```

## Manual Trigger

Force-load a specific brand's guidelines:

```
/brand-context Silk
```

List all available brands:

```
/brand-context
```

## Legal Guidelines

`general_legal.md` is loaded automatically when:
- A **guest post** is mentioned
- The user asks for **legal review** help

## Adding a New Brand

Tell Claude the brand is being approved — it will run an onboarding interview (website URL, Drive folder, production plan tab, template doc, tone, content types, claims/restrictions) and generate the guidelines file automatically.
