---
name: geo-report
description: >
  Generate a GEO audit report from collected sub-agent + verifier-script
  outputs. Produces three artifacts: (1) Markdown audit document, (2) HTML
  presentation deck (executive-friendly, slide-style, ideal for sharing
  with leadership/clients), (3) HTML technical guide (detailed scrollable
  reference). Saves into the working directory with date-stamped filenames.
  Triggers on: GEO report, generate report, audit report, presentation,
  technical guide, share with team, report for leadership.
user-invokable: true
argument-hint: "<type> <url|brand>"
license: MIT
metadata:
  author: Digital Vlad
  version: "1.0.0"
  category: geo
---

# GEO Report Generator

**Invocation:** `/geo report <type> <url|brand>`

Types:
- `md` — Markdown audit document only.
- `html-deck` — HTML presentation (slide deck, keyboard-navigable).
- `html-guide` — HTML scrollable technical guide.
- `all` — All three.

## Inputs

The report generator reads from one of:

1. **Just-completed audit context.** If `/geo audit` was the most recent call
   in the conversation, use its in-memory findings.
2. **Workspace file.** If `GEO-Audit-{brand}-{YYYY-MM-DD}.md` exists in the
   working directory within the last 14 days, parse it.
3. **Fresh audit.** If neither, prompt the user — would they like to run
   `/geo audit <url>` first?

## File naming convention

Output files are saved to the working directory:

- `GEO-Audit-{slug}-{YYYY-MM-DD}.md`
- `GEO-Presentation-{slug}-{YYYY-MM-DD}.html`
- `GEO-Guide-{slug}-{YYYY-MM-DD}.html`

Where `{slug}` is the brand name lowercased with non-alphanumerics replaced
by `-`.

## Workflow

```
python ${CLAUDE_PLUGIN_ROOT}/scripts/generate_report.py \
  --input <audit-data.json> \
  --format <md|html-deck|html-guide|all> \
  --output-dir <cwd> \
  --brand "{Brand Name}" \
  --url "{URL}"
```

The script reads structured audit data (as JSON), applies templates from
`templates/`, and writes the requested artifacts.

## Templates

- `templates/report-audit.md` — Markdown template.
- `templates/report-presentation.html` — HTML deck template (Apple-Keynote
  style, dark background, slide-by-slide navigation).
- `templates/report-guide.html` — HTML guide template (sidebar nav,
  scroll-spy, dark theme).

All HTML templates load Chart.js from CDN for visualizations
(score-by-pillar bar chart, citation distribution donut, etc.).

## Author footer

Both HTML templates have a fixed author-credit block at the very bottom of
the document, linking to:
- vdigital.app
- https://t.me/vladi9ital
- https://www.youtube.com/@vladi9ital

The Markdown template ends with the standard author footer (`../geo/references/author.md`).

## Output

The report generator emits a short message to the chat:

```
Reports generated:
- {cwd}/GEO-Audit-{slug}-{date}.md
- {cwd}/GEO-Presentation-{slug}-{date}.html
- {cwd}/GEO-Guide-{slug}-{date}.html

Open each via the file links above.
```

In the Cowork environment, the agent additionally surfaces clickable
`computer://` links to each artifact for the user.

## Quality gates

- Never fabricate scores in the report. If a pillar was not audited, mark
  it as "Not audited" in the score table.
- Always include the verification-source column (which script / what data
  source produced each finding).
- All three formats present the same data — no version drift between MD
  and HTML.
- Footer with author credit is mandatory on all three.
