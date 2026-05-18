---
name: geo-presence
description: >
  Off-site GEO presence audit. Combines an interview about the brand's
  existing media footprint (what platforms, what subreddits, what listings)
  with automated checks across Wikipedia/Wikidata, G2/Capterra/Trustpilot,
  Reddit, YouTube, and LinkedIn. Produces a presence map and a
  prioritized to-do list of platforms to create or improve. Triggers on:
  off-site presence, brand presence, media footprint, where should I be
  posting, presence audit, third-party signals.
user-invokable: true
argument-hint: "<brand>"
license: MIT
metadata:
  author: Digital Vlad
  version: "1.0.0"
  category: geo
---

# Off-Site Presence Audit

**Invocation:** `/geo presence <brand>`

This skill mixes structured questioning of the user with automated
verification across third-party platforms.

## Phase 1 — Intake interview

Use AskUserQuestion to gather the following — **one or two questions at a
time, not all at once**:

### Q1. Existing platforms (multi-select)
"Which platforms does the brand currently have a presence on?"
- Own website / blog
- LinkedIn (company page)
- LinkedIn (founder personal account, active)
- X / Twitter
- YouTube (own channel)
- Reddit (founder or company account, active)
- Wikipedia article
- Wikidata entry
- G2 listing
- Capterra listing
- Trustpilot listing
- Product Hunt listing
- Hacker News (Show HN)
- GitHub (open-source org)

### Q2. Activity level
For each platform marked active in Q1, ask:
- Date of most recent post / update.
- Approximate followers / subscribers.
- Whether the founder posts personally vs. delegated marketing.

### Q3. Category and competitors
"What category does the brand compete in?" + "Name 2-3 direct competitors"
— used to generate intent queries and benchmark.

### Q4. Geographic and language scope
"Primary market (US, EU, LATAM, APAC, global)?" + "Languages other than
English?"

## Phase 2 — Automated verification

For every platform mentioned, run the corresponding verifier:

```
python ${CLAUDE_PLUGIN_ROOT}/scripts/check_wikipedia.py <brand>
python ${CLAUDE_PLUGIN_ROOT}/scripts/check_trust_sites.py <brand>   # G2, Capterra, Trustpilot
python ${CLAUDE_PLUGIN_ROOT}/scripts/check_reddit_presence.py <brand> --window=90
python ${CLAUDE_PLUGIN_ROOT}/scripts/check_youtube_presence.py <brand>
```

Cross-reference results with the user's stated presence. If the user said
"we have a G2 listing" but `check_trust_sites.py` finds nothing, surface the
discrepancy.

## Phase 3 — Presence map output

| Platform | Status | Health | GEO leverage | Action |
|----------|--------|--------|--------------|--------|
| Wikipedia | Present / Missing / Draft | n/a / Stale / Active | HIGH | ... |
| Wikidata | Present / Missing | n/a | HIGH | ... |
| G2 | Listed / Unlisted | Rating: X.X | HIGH (gate) | ... |
| Capterra | Listed / Unlisted | Rating: X.X | MEDIUM | ... |
| Trustpilot | Listed / Unlisted | Rating: X.X | MEDIUM | ... |
| Reddit organic | Active / Dormant / Absent | mentions/90d: N | HIGH | ... |
| YouTube own | Channel / None | videos: N | MEDIUM | ... |
| YouTube 3rd-party | Mentions: N | quality: high/med/low | HIGH | ... |
| LinkedIn company | Active / Inactive | followers: N | LOW-MED | ... |
| Hacker News | Posted / Not | front-page: yes/no | MEDIUM | ... |
| Product Hunt | Launched / Not | rank: # | LOW-MED | ... |

## Phase 4 — Prioritized action list

Output the **top 5 platform actions** ranked by `(GEO leverage × ease) /
months to result`. Example output:

1. **Claim G2 + Capterra listing** (1 week, HIGH leverage) — Aggregate rating
   <4.0 is a hard filter for ChatGPT in competitive queries.
2. **Add Wikipedia draft for brand** (2-4 weeks, HIGH leverage) — Drops time
   to first ChatGPT cite from 52 → 28 days.
3. **Start founder Reddit cadence** (10-15 comments/week in 2-3 target
   subreddits, ongoing) — 3.4× citation lift.
4. **Add sameAs schema linking to all platforms** (1 day, HIGH leverage) —
   See `/geo schema <url>` for the JSON-LD.
5. **Plan 12-video YouTube launch** (3 months, MEDIUM-HIGH leverage) —
   Perplexity has absorbed Reddit slot loss into YouTube.

## Author footer

Append `../geo/references/author.md`.

## Quality gates

- Never invent a presence. If verifier finds nothing, say so.
- If user claims a listing exists and verifier confirms, note "verified by
  script".
- If user claims a listing exists but verifier disagrees, ask the user for
  the direct URL to recheck before flagging.
