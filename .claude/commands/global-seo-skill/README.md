# global-seo-skill

Senior SEO/GEO advisor for Digitad. Handles any SEO or GEO question, strategy task, or analysis that doesn't match a more specialized skill. Fully bilingual (Canadian English / Canadian French) — responds in whichever language you write in.

## When to Use

- SEO questions, strategy, recommendations
- GEO / AI citation optimization (Google AI Overviews, Bing Copilot, LLM visibility)
- Keyword research and intent classification
- Competitive analysis
- Technical SEO explanations
- Any task where no specialized skill exists

## Quick Start

```
/global-seo-skill
```

Then ask your question naturally:

```
What's the best internal linking strategy for a yogurt brand with 200 product pages?
```

```
Comment optimiser une page pour les aperçus IA de Google?
```

## Skill Dispatch

Before answering directly, this skill checks whether a more specialized skill exists for your request and hands off to it automatically. Common dispatches:

| Request type | Dispatched to |
|---|---|
| Site/technical audit | `/seo-geo-technical-audit` |
| Monthly content briefs | `/monthly-content-planner` |
| Content production plan | `/on-page-strategy` |
| Remote SF crawl | `/crawl-vm-screaming-frog` |

## Behavior

- Proactively makes recommendations — doesn't just answer what was asked
- Asks clarifying questions when information is missing
- Will respectfully push back if it disagrees with an SEO approach (with reasoning)
- Cites evidence and suggests alternatives when challenging assumptions
