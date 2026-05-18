---
name: geo-reddit
description: >
  Reddit presence audit and organic posting strategy. Counts brand
  mentions across target subreddits over the last 90 days, evaluates
  sentiment, identifies subreddit-wiki entries, and produces a 6-step
  organic playbook (subreddit selection, account setup, cadence,
  extraction pipeline, late-stage targeting, tool-wiki entries).
  Triggers on: Reddit strategy, Reddit presence, subreddit, Reddit posting,
  Reddit cadence, Reddit citations.
user-invokable: true
argument-hint: "<brand> [--subreddits=r/a,r/b,r/c]"
license: MIT
metadata:
  author: Digital Vlad
  version: "1.0.0"
  category: geo
---

# Reddit Presence + Strategy

**Invocation:** `/geo reddit <brand>` (optional `--subreddits=...`)

## Phase 1 — Subreddit targeting

If `--subreddits` not provided, ask the user via AskUserQuestion:

> "Name 3-5 subreddits where your buyers actually hang out (e.g. r/SaaS,
> r/webdev, r/marketing). If you don't know, list your category and we'll
> suggest."

If the user lists a category instead of subreddits, suggest 5-8 candidates
matching that category. Common starting points:

| Category | Subreddits |
|----------|-----------|
| Dev tools | r/programming, r/webdev, r/devops, r/javascript, r/Python |
| SaaS / B2B | r/SaaS, r/Entrepreneur, r/startups, r/sales, r/CustomerSuccess |
| Marketing | r/marketing, r/SEO, r/PPC, r/socialmedia, r/contentmarketing |
| Design | r/Design, r/UI_Design, r/UXDesign, r/web_design |
| Data | r/datascience, r/analytics, r/dataengineering, r/MachineLearning |
| Productivity | r/productivity, r/Notion, r/GetMotivated |

## Phase 2 — Verification

```
python ${CLAUDE_PLUGIN_ROOT}/scripts/check_reddit_presence.py <brand> --subreddits=r/a,r/b,r/c --window=90
```

The script counts:
- Total mentions of brand string in the last 90 days.
- Mentions per subreddit.
- Average upvotes on threads that mention the brand.
- Sentiment per mention (positive / neutral / negative).
- Whether the brand appears in any subreddit sidebar / wiki.
- Whether the founder account (if known) has activity in those subreddits.

## Phase 3 — Score

Mention count thresholds (per `scoring-rubric.md`):
- ≥ 10 organic mentions in 90 days (non-spam): +15 points.
- Brand in subreddit sidebar / wiki: +10 points.

## Phase 4 — Strategy output

If the user wants a **plan** (not just an audit), generate the 6-step
playbook from `../geo/references/reddit-strategy.md`:

### Step 1 — Final subreddit list
Confirm 3-5 target subreddits with reasoning (active, allows tool discussion,
buyers present, competitors mentioned).

### Step 2 — Account setup
- Founder account: real name + LinkedIn link.
- Bio: explicit company mention.
- Account-age warm-up: 4-6 weeks of comments only before any link.

### Step 3 — Cadence
- 10-15 quality comments/week.
- 70% pure help / 20% natural product mention / 10% deep-content link.
- No top-level disguised ads.

### Step 4 — Extraction pipeline
Weekly: extract 10-20 recurring questions / objections / competitor
mentions → convert to FAQ and blog content on the owned domain.

### Step 5 — Late-stage intent targeting
Highest-conversion threads: "has anyone tried X?", "looking for X
recommendations?", "migrating from X to Y", "eval-stage X vs Y vs Z".

### Step 6 — Tool-wiki entries
After 2-3 months of contribution: DM moderators with the case for inclusion.

## Output

```
# Reddit Presence — {brand}

## Mentions (last 90 days)
| Subreddit | Mentions | Avg upvotes | Sentiment | Sidebar/wiki |
|-----------|----------|-------------|-----------|--------------|
| r/SaaS | 12 | 47 | positive | no |
...

## Pillar contribution
+15 / +10 depending on volume and wiki presence.

## 6-Step Strategy (if plan mode)
[detailed plan as above]

## Risks called out
- Reddit citation volatility (lawsuits, parameter shifts) — diversify
  with YouTube + Wikipedia simultaneously.
- Astroturfing risk: never use fake accounts.
- Karma transfer: r/funny karma does not equal r/SaaS credibility.
```

## Quality gates

- Never recommend buying upvotes / karma.
- Never recommend mass-DMing moderators.
- Always recommend founder account, not generic marketing account.
- Caveat that Reddit citation share dropped 60% → 10% in ChatGPT during Q4
  2025 — Reddit is necessary but not sufficient.
