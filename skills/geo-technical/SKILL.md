---
name: geo-technical
description: >
  Technical GEO audit. Checks robots.txt for AI crawler accessibility
  (OpenAI three-bot family, Anthropic three-bot framework, Perplexity bots,
  Google-Extended, Apple/Meta/Mistral/Amazon), llms.txt presence and
  validity, server-side rendering vs JS-only rendering, sitemap fetchability,
  and Cloudflare Pay-Per-Crawl configuration. Triggers on: robots.txt,
  llms.txt, AI crawlers, GPTBot, ClaudeBot, PerplexityBot, SSR, JavaScript
  rendering, AI bot access.
user-invokable: true
argument-hint: "<url>"
license: MIT
metadata:
  author: Digital Vlad
  version: "1.0.0"
  category: geo
---

# Technical GEO Audit

**Invocation:** `/geo technical <url>`

## What this checks

### 1. robots.txt — AI crawler access

Fetch `<root>/robots.txt`. Verify each of the following bots has an explicit
`Allow:` or fallback `User-agent: *` allow:

**OpenAI (three bots, deliberately separated):**
- `GPTBot` — model training crawler.
- `OAI-SearchBot` — search index crawler (more crawl events than GPTBot as of 2026).
- `ChatGPT-User` — user-initiated fetches.

**Anthropic (three-bot framework, formalized 2026):**
- `ClaudeBot` — training. Supports `Crawl-delay`.
- `Claude-User` — user-initiated fetches.
- `Claude-SearchBot` — search index.

**Retired — do NOT add:** `anthropic-ai`, `claude-web` (retired July 2024).

**Perplexity:**
- `PerplexityBot` — main crawler.
- `Perplexity-User` — user-initiated fetches.

**Google:**
- `Google-Extended` — controls Gemini/AIO/AI Mode training use of content.
- `Googlebot` — standard.

**Microsoft:**
- `bingbot`.

**Optional but recommended:**
- `Applebot`, `Meta-ExternalAgent`, `MistralAI-User`, `Amazonbot`, `CCBot`.

**Anti-pattern:** Blocking all AI bots while allowing search engines —
competitors will fill the slot.

**Selective strategy:** If the user wants to opt out of training but stay in
search, allow only the `*SearchBot` / `*-User` family and block training bots
(GPTBot, ClaudeBot). Models continue to cite via RAG retrieval.

### 2. Cloudflare Pay-Per-Crawl

If the site sits behind Cloudflare:

- Cloudflare introduced **Pay-Per-Crawl** (closed beta) — site owners can
  Allow / Charge (HTTP 402) / Block each AI crawler from the dashboard.
- **Content Independence Day (1 July 2025)**: new Cloudflare-registered sites
  by default **block AI bots**. If the domain was registered after this date,
  the user must explicitly check the `AI Crawl Control` panel.

**Action item:** Warn the user to verify their Cloudflare AI Crawl Control
configuration if `cf-ray` header is present.

### 3. llms.txt

Fetch `<root>/llms.txt`. Validate against the standard:

```
# Site Title

> Brief description (1-2 sentences)

[Detailed description: what it does, for whom, key differentiators]

## Docs
- [Title](https://example.com/path.md): one-line description

## Guides
- [Title](https://example.com/path.md): one-line description
```

**Reality check:** Only 10.13% adoption (SE Ranking 300K-domain survey, 2026).
Google publicly does NOT use llms.txt. ChatGPT/Claude/Perplexity have NOT
confirmed use. **BUT**: IDE agents (Cursor, Continue, Cline, Aider) and MCP
servers actively consume llms.txt.

**Verdict:**
- Developer-tool products: implement (improves agent workflows).
- Non-developer products: low priority.
- If present but malformed: report exactly which section fails.

### 4. Server-side rendering check

Fetch raw HTML (no JS execution). Compare:

- `<body>` text length (raw).
- `<body>` text length (post-JS, via headless if available).

If raw < 20% of rendered: **HARD-FLAG as Critical**. AI crawlers do not
execute JavaScript. Suggest:
- Next.js SSR / Static Generation.
- Astro / Nuxt SSR.
- Cloudflare Snippets or Workers for prerender.
- React Snap / Prerender.io.

### 5. Sitemap fetchability

Check `<root>/sitemap.xml`. If present, verify:
- Valid XML.
- Listed in robots.txt as `Sitemap: <url>`.
- No 404s in first 20 URLs sampled.

## Verifier scripts to run

```
python ${CLAUDE_PLUGIN_ROOT}/scripts/check_robots_txt.py <url>
python ${CLAUDE_PLUGIN_ROOT}/scripts/check_llms_txt.py <url>
python ${CLAUDE_PLUGIN_ROOT}/scripts/fetch_page.py <url> --check-ssr
```

## Output

```
# Technical GEO — {url}

## Pillar Score: XX/100

## Findings

### robots.txt
- GPTBot: ALLOWED / BLOCKED / IMPLICIT
- OAI-SearchBot: ...
[full table per crawler]

### llms.txt
- Status: present / missing / malformed
- Recommendation: ...

### SSR
- Raw HTML body: X chars
- Rendered body: Y chars (if available)
- Verdict: SSR / Hybrid / JS-only

### Sitemap
- Status: present / missing
- Issues: ...

### Cloudflare Pay-Per-Crawl
- cf-ray header: present / absent
- Recommendation: ...

## Top Actions (Technical pillar)
1. ...
```

## Quality gates

- Never recommend `anthropic-ai` or `claude-web` (retired).
- Never block all AI bots without explaining the cost.
- Flag JS-only as Critical, not Suggestion.
