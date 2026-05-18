# Compatibility with claude-seo

This skill is designed to be installed alongside `claude-seo` (AgriciDaniel) and
**never override or break its behavior**.

## Namespace separation

| Aspect | claude-seo | claude-geo |
|--------|------------|------------|
| Command prefix | `/seo ...` | `/geo ...` |
| Plugin name | `claude-seo` | `claude-geo` |
| Skill folder | `skills/seo/`, `skills/seo-*/` | `skills/geo/`, `skills/geo-*/` |
| Agent prefix | `seo-*` in `agents/` | `geo-*` in `agents/` |
| Script prefix | varies | `check_*.py`, `score_geo.py`, `generate_report.py` |
| Output file convention | `SEO-*.md`, GSC PDFs | `GEO-Audit-*.md`, `GEO-Presentation-*.html`, `GEO-Guide-*.html` |

There is no skill name collision, no agent name collision, no script name
collision. Both plugins coexist.

## Functional overlap

`claude-seo` ships a `/seo geo` command. It performs a basic single-page GEO
check inside a larger SEO audit. `claude-geo` is the deep specialist. Both can
be useful in the same workflow.

| Scenario | Recommended tool |
|----------|------------------|
| Full SEO audit with one-shot GEO pass | `/seo audit <url>` (claude-seo) |
| Quick GEO read on a single page during SEO work | `/seo geo <url>` (claude-seo) |
| Deep GEO audit with real LLM-mention verification | `/geo audit <url>` (claude-geo) |
| GEO scoring rubric + dual-HTML report | `/geo audit <url>` then `/geo report all <url>` |
| Off-site presence audit (Reddit / Wikipedia / G2 / Capterra) | `/geo presence <brand>` |
| Verify a single technique was applied | `/geo verify <technique> <url>` |
| Strategic 90-day GEO roadmap (technical + creative) | `/geo plan <brand>` |

## Recommended workflow

```
1. /seo audit https://example.com        # Core SEO foundations
2. /seo geo https://example.com           # Quick GEO read inside SEO context
3. /geo audit https://example.com         # Deep GEO audit (separate report)
4. /geo plan https://example.com          # Strategic 90-day roadmap
5. /geo verify <technique> https://example.com   # After implementing changes
```

## What this skill explicitly does NOT do

To avoid stepping on `claude-seo`:

- Core Web Vitals analysis (LCP, INP, CLS) — defer to `/seo technical` or `/seo google`.
- Backlink analysis — defer to `/seo backlinks`.
- Local SEO (Google Business Profile, citations) — defer to `/seo local` and `/seo maps`.
- Hreflang / i18n SEO — defer to `/seo hreflang`.
- Sitemap generation — defer to `/seo sitemap`.
- E-E-A-T content quality scoring — defer to `/seo content`.
- Programmatic SEO at scale — defer to `/seo programmatic`.

If the user asks about any of the above, recommend the matching `/seo` command
without trying to replicate that work inside GEO.
