---
name: geo-trust
description: >
  Trust-site presence verification. Checks Wikipedia, Wikidata, G2,
  Capterra, Trustpilot, Software Advice, GetApp, TrustRadius, LinkedIn
  for brand listings and aggregate ratings. Special focus on the "G2 ≥4.0
  rule" — aggregate review score below 4.0 acts as a hard ChatGPT filter
  in competitive queries. Triggers on: G2, Capterra, Trustpilot, Wikipedia
  brand article, Wikidata, trust signals, review aggregator rating.
user-invokable: true
argument-hint: "<brand>"
license: MIT
metadata:
  author: Digital Vlad
  version: "1.0.0"
  category: geo
---

# Trust-Site Presence Verification

**Invocation:** `/geo trust <brand>`

## What this checks

```
python ${CLAUDE_PLUGIN_ROOT}/scripts/check_wikipedia.py <brand>
python ${CLAUDE_PLUGIN_ROOT}/scripts/check_trust_sites.py <brand>
```

### Wikipedia / Wikidata

- Wikipedia article: exists / draft / none.
- Wikidata Q-ID: exists / none.
- Wikidata `sameAs` count.
- Wikipedia article freshness (last edit).
- Wikipedia article quality flags (stub, NPOV warnings, deletion notices).

**Why it matters:** First ChatGPT citation in 28 days with Wikipedia vs 52
days without. Top-10 ChatGPT citations: 26-48% from Wikipedia.

### Review aggregators

For each of G2, Capterra, Trustpilot, Software Advice, GetApp, TrustRadius:

- Listed: yes / no.
- Aggregate rating (if listed).
- Review count.
- Response rate (vendor responds to reviews).
- Recency of latest review.

**The G2 4.0 Rule.** Aggregate score <4.0 on G2/Capterra/Trustpilot acts as
a **hard filter** for ChatGPT in competitive queries even when content is
excellent. This is the single highest-leverage off-site signal for ChatGPT
visibility.

### LinkedIn company page

- Followers count.
- Posting cadence (last 30 days).
- Employee count listed.

## Output

```
# Trust-Site Presence — {brand}

## Wikipedia / Wikidata
| Asset | Status | Notes |
|-------|--------|-------|
| Wikipedia article | Present / Draft / None | last edit: YYYY-MM-DD |
| Wikipedia quality | Good / Stub / Issues | flags: ... |
| Wikidata Q-ID | Q12345 / None | sameAs count: N |

## Review aggregators
| Platform | Listed | Rating | Reviews | Recency | Notes |
|----------|--------|--------|---------|---------|-------|
| G2 | yes | 4.3 | 87 | within 30d | ✓ above 4.0 floor |
| Capterra | yes | 3.7 | 12 | within 90d | ⚠ BELOW 4.0 — ChatGPT filter risk |
| Trustpilot | no | — | — | — | — |
| Software Advice | yes | 4.5 | 22 | within 30d | ✓ |
| GetApp | yes | 4.1 | 18 | within 60d | ✓ |
| TrustRadius | no | — | — | — | — |

## LinkedIn
- Followers: N
- Last post: YYYY-MM-DD
- Posting cadence: high / medium / low

## Pillar contribution
+ Wikipedia article: +20
+ Wikidata: +10
+ G2 ≥4.0: +15
- Capterra <4.0: -10 (Critical)
+ Trustpilot ≥4.0: +10
+ LinkedIn ≥1000 followers: +5

## Critical Findings
- Capterra aggregate rating 3.7 < 4.0 floor. ChatGPT competitive-query
  filter applies. Highest-priority remediation: review request campaign.

## Top Actions (Trust pillar)
1. Capterra: drive 10-15 verified reviews from satisfied customers to lift
   aggregate above 4.0. Estimated impact: removes ChatGPT filter; pillar
   delta +20.
2. Wikidata: create Q-item if missing. 30 minutes work, +10 pillar.
3. Trustpilot: claim and seed first 20 reviews. Pillar delta +10.
```

## Remediation playbooks

### G2 below 4.0
- Audit existing reviews for the dimensions dragging score (UX? support? pricing?).
- Address the substantive complaints first (not just request more reviews).
- Use G2's Review Generation Campaign.
- In-app NPS prompt for promoters → "leave us a review on G2".
- Set up vendor response on every existing review (correlates with score recovery).

### No Wikipedia article
- Check notability: 3+ tier-1 secondary sources (NYT, WSJ, TechCrunch, FT, Forbes).
- If notable: draft in user space → submit via AfC.
- If not yet notable: focus on PR first; build Wikidata in parallel (lower bar).

### No Wikidata
- 30 minutes. Create Q-item with: `instance of`, `industry`, `founded date`,
  `founder`, `website`, `LinkedIn ID`, `Crunchbase ID`, `GitHub ID`.

## Quality gates

- The G2 4.0 floor is the most important single rule in this skill — always
  surface as Critical when violated.
- Never recommend buying reviews — it's a TOS violation everywhere and is
  detectable.
- Always recommend responding to negative reviews substantively, not
  defensively.
