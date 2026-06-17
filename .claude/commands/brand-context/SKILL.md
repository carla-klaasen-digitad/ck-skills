---
name: brand-context
description: Automatically loads brand-specific writing guidelines whenever a brand name is mentioned in a content task. Reads the brand's .md file from all_skills/content-writing/guidelines/ and optionally loads general_legal.md for off-site or legal-sensitive content. Read for on-site content writing, off-site content writing, keyword research, general brand questions. Brand include but are not limited to: Oikos, Activia, Happy Family, International Delight (ID), Too Good, Evian, Stok, Silk, Danone North America, Light and Fit, Danimals, Remix, Dunkin creamers. Also load this skill if relevant file names are brought up. 

allowed-tools: Read, Bash
---

# Brand Context Skill

## Purpose

Load the correct brand guidelines file the moment a brand name appears in conversation — before writing any content, briefs, or copy.

---

## Brand Registry

Match any of these names (case-insensitive) to their file:

| Brand mention(s) | File |
|-----------------|------|
| Activia | `activia.md` |
| Danimals | `danimals.md` |
| Dannon | `dannon.md` |
| Danone Away From Home, Danone AFH, DAFH | `danoneawayfromhome.md` |
| Danone North America, DNA, Danone NA | `danonenorthamerica.md` |
| Dunkin Creamers, Dunkin' Creamers, Dunkin | `dunkincreamers.md` |
| Evian | `evian.md` |
| Follow Your Heart, FollowYourHeart, FYH | `followyourheart.md` |
| Happy Family, HappyFamily, Happy Family Organics | `happyfamily.md` |
| International Delight, Int'l Delight, ID Creamers | `internationaldelight.md` |
| Light & Fit, Light and Fit | `lightandfit.md` |
| Mitacs | `mitacs.md` |
| Oikos | `oikos.md` |
| Silk | `silk.md` |
| So Delicious, SoDelicious, So Delicious Dairy Free | `sodelicious.md` |
| SToK, Stok | `stok.md` |
| Too Good, TooGood, Two Good | `toogood.md` |
| YoCrunch, Yo Crunch | `yocrunch.md` |
| Remix Yogurt, Remix, RemixYogurt | `remixyogurt.md` |

**Base path:** `/Users/carlaklaasen/claude_code/all_skills/content-writing/guidelines/`

---

## Auto-Load Rules

### Step 1 — Detect brand
Scan the user's message for any brand name from the registry above. Match is case-insensitive and partial (e.g. "writing for Oikos" matches Oikos).

### Step 2 — Read brand file
Immediately read the matched brand `.md` file using the Read tool. Do this silently — no announcement, no "Loading Oikos guidelines…" message.

### Step 3 — Load `general_legal.md` when needed
Also read `general_legal.md` only when **one of these two conditions** is true:
- The message mentions a guest post (e.g. "guest post", "guest article")
- The user explicitly asks for legal review help (e.g. "legal review", "check legal", "review for legal")

### Step 4 — Apply silently
Use the brand guidelines and legal rules as active constraints throughout the rest of the task. Do not summarize or quote the files back unless the user asks. Just follow them.

---

## When This Skill Activates

- Any content task (writing, briefing, editing) that names a brand from the registry
- User says "write for [brand]", "create content for [brand]", "brief for [brand]"
- User pastes an article or copy and mentions a brand name for review
- User mentions checking brand guidelines

## When to Invoke Manually (`/brand-context`)

Use the slash command when you want to explicitly reload or verify brand context:
- "Load Oikos guidelines" — reads and confirms the brand file is loaded
- `/brand-context Silk` — forces a fresh read of the Silk brand file
- `/brand-context` with no args — lists all available brands

---

## Multiple Brands in One Session

If a second brand is mentioned mid-session, load its file as well. Keep both active. Note any conflicts between brand rules (e.g., one brand prohibits claims the other allows) and flag them to the user.

---

## Missing Brand File

If a brand name is mentioned but no file exists in the guidelines directory:
1. Do not guess or improvise brand rules
2. Tell the user: "I don't have a guidelines file for [Brand]. Want me to create one or proceed without brand-specific rules?"

---

## File Does Not Load

If the Read tool returns an error, immediately tell the user which file failed to load and ask if they'd like to supply the guidelines manually.

---

## Brand Onboarding — When a Brand Is Approved

When the user says a brand is being approved, added, or moved from pending to active, run the onboarding interview below. Ask the questions grouped by section. Wait for answers before proceeding to the next section. Once all answers are collected, compile them into a brand guidelines `.md` file at `all_skills/content-writing/guidelines/[brandname].md` following the structure of existing brand files (activia.md, oikos.md, etc. as reference).

### Onboarding Interview

**Section 1 — Logistics** *(fills the top block of the guidelines file)*
1. What is the brand's website URL?
2. Is there a Google Drive folder for on-site content deliverables? Share the URL (or say n/a).
3. What is the Google Sheets production plan ID and the tab name for this brand?
4. Is there a content brief template Google Doc? Share the URL (or say n/a).
5. What is the Neuronwriter project URL for this brand?

**Section 2 — Brand Identity**
6. Who is the parent company?
7. What is the industry sector and what are the core products or product lines?
8. What is the primary market — US only, Canada only, or both? (US = US English; Canada may be bilingual FR/EN)
9. Who is the primary target audience? (demographics + psychographics — e.g., "coffee drinkers 18+, budget-conscious, flavor explorers")
10. What are the top 3–5 brand differentiators vs. competitors?

**Section 3 — Tone & Vocabulary**
11. Describe the editorial tone in 5–10 words. (e.g., "empowering, flavor-forward, transparent, not preachy")
12. What tones or voices should be avoided? (e.g., overly promotional, clinical, moralizing)
13. Are there specific words or phrases that must always appear in copy?
14. Are there specific words or phrases that must never appear? (regulatory exclusions, banned claims, etc.)

**Section 4 — Content Types & Structure**
15. What content types are in scope? (product pages, category pages, recipe pages, learning center articles, etc.)
16. For each content type: does the page include a FAQ section? If yes, how many questions?
17. For product pages: what is the standard content structure? (benefit bullets, Q&A throughout, or other)
18. For recipe pages: does the brief include a "Client Information" block for social media captions?

**Section 5 — SEO & Quality Check**
19. What are the primary keyword clusters or content pillars the brand wants to own?
20. Which competitor brands should never be mentioned, linked, or compared?
21. What QC tools are required? Standard is: NW score before/after, AI detection (gptradar.com), plagiarism <10% (duplichecker.com). Any additional tools?
22. Is any content bilingual? If yes: are EN and FR in the same document, or separate files per language?

**Section 6 — Claims, Compliance & Certifications**
23. Are there product claims that must always appear on relevant pages? (e.g., "0g added sugar", "USDA Organic", "Prepared in the US")
24. Are there health claim restrictions or mandatory legal disclaimers?
25. Are there certifications that should always be referenced? (e.g., Clean Label Project, B Corp, Non-GMO Project)

**Section 7 — Additional Context**
26. Are there any discontinued products, programs, or lines that must never be promoted?
27. Are there seasonal content rules or campaign priorities to note?
28. Anything else a writer needs to know to produce excellent on-brand content?

### After the Interview

Once all answers are collected:
1. Create `all_skills/content-writing/guidelines/[brandname].md` with the standard structure (Logistical Information block → AI Content Profile sections matching existing brand files)
2. Create a Section 15 "Content Brief Standards" with placeholders — fill it in once actual briefs from Drive have been reviewed
3. Add the brand to the CLAUDE.md Brand Context registry
4. Tell the user: "Brand guidelines file created. I'd recommend reviewing an actual content brief from Drive to fill in the Section 15 patterns before the first brief is written."
