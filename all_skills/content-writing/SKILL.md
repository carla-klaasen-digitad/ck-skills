---
name: content-writing
description: Generate high-quality on-page content, create NeuronWriter briefs, write multi-format website content, and produce SEO-optimized copy with brand consistency.
model: sonnet
priority_intent_keywords: write content|create brief|generate copy|content creation|seo content|brand content|page content|on-page|neuronwriter
---

# Skill Overview

This skill automates content generation across multiple formats and channels:
- **On-Page Content**: SEO-optimized website copy for homepage, product pages, category pages
- **NeuronWriter Briefs**: Content outlines with keyword research, competitor analysis, and structure recommendations
- **Multi-Brand Support**: Maintains brand voice consistency across multiple properties (Danone, DTC, etc.)
- **Bulk Generation**: Process content from Google Sheets, generate in batch, auto-upload to Google Docs/Drive or creation of neuronwriter briefs. 
- **Content Iteration**: Refine content based on performance metrics and brand feedback
- **Compliance & Guidelines**: Adheres to brand-specific and general legal guidelines for content creation, ensuring all claims are supported and language is appropriate for the target audience.
---

# Phase 0: Requirements & Validation

## API & Authentication Setup

### Required Credentials (load from `.env`)
- **Google Sheets API**: OAuth credentials stored as `content-automation-key.json`
- **Google Drive API**: Same OAuth flow, enabled in Google Cloud project
- **Google Docs API**: Required for document creation/updates
- **Anthropic API**: Claude API key for content generation
- **NeuronWriter API** (optional): For brief generation and keyword research
- **SE Ranking API** (optional): For SERP analysis and competitive insights

### Token Management
- Google OAuth tokens stored in `token.json` — auto-refreshed if expired
- Keep `.env` file secure; never commit credentials to git
- Verify all services are authorized before running batch jobs

### Brand Guidelines — Auto-Load

Brand guidelines are stored in `all_skills/content-writing/guidelines/`. When a brand name is mentioned, the brand-context skill loads the appropriate file automatically. Do not proceed with writing before the brand file is loaded.

- Brand files: `all_skills/content-writing/guidelines/{brand}.md`
- Legal overlay: `all_skills/content-writing/guidelines/general_legal.md` (load for off-site / guest post content)
- Full registry and rules: `.claude/commands/brand-context/SKILL.md`

---

# 