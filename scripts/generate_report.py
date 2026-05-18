#!/usr/bin/env python3
"""
generate_report.py — Render GEO audit reports from a structured data file.

Usage:
    python generate_report.py
        --input audit-data.json
        --format md|html-deck|html-guide|all
        --output-dir <dir>
        --brand "Acme"
        --url "https://acme.com"

Expects scored audit data (output of score_geo.py).

Templates loaded from <plugin>/templates/:
  - report-audit.md
  - report-presentation.html
  - report-guide.html

Each artifact carries Digital Vlad's author footer (vdigital.app, t.me/vladi9ital,
youtube.com/@vladi9ital).
"""
import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path


AUTHOR_FOOTER_FALLBACK = """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
GEO audit by Digital Vlad — claude-geo skill v1.0
🌐 Website  → https://vdigital.app/
📨 Telegram → https://t.me/vladi9ital
▶️ YouTube  → https://www.youtube.com/@vladi9ital
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""


def load_author_footer(plugin_dir: Path) -> str:
    """Load the canonical author footer from references/author.md.

    The reference file wraps the footer in a triple-backtick block — extract
    that block. Falls back to AUTHOR_FOOTER_FALLBACK if the file is missing
    or malformed.
    """
    ref_path = plugin_dir / "skills" / "geo" / "references" / "author.md"
    try:
        text = ref_path.read_text()
    except (FileNotFoundError, OSError):
        return AUTHOR_FOOTER_FALLBACK.strip()
    m = re.search(r"```\s*\n(.*?)\n```", text, re.DOTALL)
    if m:
        return m.group(1).strip()
    return AUTHOR_FOOTER_FALLBACK.strip()


def slugify(s: str) -> str:
    s = (s or "report").strip().lower()
    s = re.sub(r"[^a-z0-9-]+", "-", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return s or "report"


def load_templates(plugin_dir: Path) -> dict:
    return {
        "md": (plugin_dir / "templates" / "report-audit.md").read_text(),
        "html-deck": (plugin_dir / "templates" / "report-presentation.html").read_text(),
        "html-guide": (plugin_dir / "templates" / "report-guide.html").read_text(),
    }


def render_data_json(data: dict) -> str:
    """Render the audit data as embedded JSON for HTML templates.

    Escapes `</script>` sequences so a maliciously named brand can't break
    out of the script tag.
    """
    raw = json.dumps(data, indent=2)
    return raw.replace("</", "<\\/")


def render_md(template: str, data: dict, author_footer: str = None) -> str:
    """Simple {{key}} substitution for markdown template."""
    out = template
    out = out.replace("{{BRAND}}", str(data.get("brand", "")))
    out = out.replace("{{URL}}", str(data.get("url", "")))
    out = out.replace("{{DATE}}", datetime.now().strftime("%Y-%m-%d"))
    out = out.replace("{{TOTAL_SCORE}}", str(data.get("total_score", 0)))
    out = out.replace("{{GRADE}}", str(data.get("grade", "?")))
    out = out.replace("{{GRADE_MEANING}}", str(data.get("grade_meaning", "")))

    # Pillars table
    pillars_md = ""
    for name, info in (data.get("pillars") or {}).items():
        weight_pct = int(info.get("weight", 0) * 100)
        pillars_md += f"| {name.title():<13} | {info.get('score', 0):>5.1f}/100 | {weight_pct}% | {info.get('weighted_contribution', 0):>5.2f} |\n"
    out = out.replace("{{PILLARS_TABLE}}", pillars_md.rstrip())

    # Critical failures
    crit_md = ""
    for c in (data.get("critical_failures") or []):
        crit_md += f"- {c}\n"
    if not crit_md:
        crit_md = "_None identified in this audit._"
    out = out.replace("{{CRITICAL_FAILURES}}", crit_md)

    # Top 5 actions
    actions_md = ""
    for i, a in enumerate(data.get("top_5_actions") or [], start=1):
        actions_md += (f"{i}. **{a.get('action','')}** — pillar: `{a.get('pillar','')}`, "
                       f"expected score delta +{a.get('score_delta','?')}, "
                       f"effort: {a.get('effort_hours','?')}h, "
                       f"leverage: {a.get('leverage','?')}\n")
    if not actions_md:
        actions_md = "_No actions specified._"
    out = out.replace("{{TOP_5_ACTIONS}}", actions_md)

    # Per-pillar findings
    pillar_findings_md = ""
    for name, info in (data.get("pillars") or {}).items():
        pillar_findings_md += f"\n### {name.title()} ({info.get('score','?')}/100)\n\n"
        findings = info.get("findings", [])
        if findings:
            for f in findings:
                pillar_findings_md += f"- {f}\n"
        else:
            pillar_findings_md += "_No detailed findings recorded for this pillar._\n"
    out = out.replace("{{PILLAR_FINDINGS}}", pillar_findings_md)

    out = out.replace("{{AUTHOR_FOOTER}}", (author_footer or AUTHOR_FOOTER_FALLBACK).strip())
    return out


def render_html(template: str, data: dict) -> str:
    """For HTML templates, embed the audit data as JSON in a <script> tag."""
    payload_json = render_data_json(data)
    out = template
    out = out.replace("{{BRAND}}", str(data.get("brand", "")))
    out = out.replace("{{URL}}", str(data.get("url", "")))
    out = out.replace("{{DATE}}", datetime.now().strftime("%Y-%m-%d"))
    out = out.replace("{{TOTAL_SCORE}}", str(data.get("total_score", 0)))
    out = out.replace("{{GRADE}}", str(data.get("grade", "?")))
    out = out.replace("{{GRADE_MEANING}}", str(data.get("grade_meaning", "")))
    out = out.replace("{{AUDIT_DATA_JSON}}", payload_json)
    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--format", default="all", choices=["md", "html-deck", "html-guide", "all"])
    parser.add_argument("--output-dir", default=".")
    parser.add_argument("--brand", default="")
    parser.add_argument("--url", default="")
    parser.add_argument("--plugin-dir", default=None,
                        help="Path to claude-geo plugin (auto-detect if omitted)")
    args = parser.parse_args()

    with open(args.input, "r") as f:
        data = json.load(f)

    if args.brand:
        data["brand"] = args.brand
    if args.url:
        data["url"] = args.url

    plugin_dir = Path(args.plugin_dir) if args.plugin_dir else Path(__file__).resolve().parent.parent
    templates = load_templates(plugin_dir)
    author_footer = load_author_footer(plugin_dir)

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    slug = slugify(data.get("brand") or "report")
    date = datetime.now().strftime("%Y-%m-%d")

    generated = []

    if args.format in {"md", "all"}:
        md = render_md(templates["md"], data, author_footer)
        path = out_dir / f"GEO-Audit-{slug}-{date}.md"
        path.write_text(md)
        generated.append(str(path))
    if args.format in {"html-deck", "all"}:
        html = render_html(templates["html-deck"], data)
        path = out_dir / f"GEO-Presentation-{slug}-{date}.html"
        path.write_text(html)
        generated.append(str(path))
    if args.format in {"html-guide", "all"}:
        html = render_html(templates["html-guide"], data)
        path = out_dir / f"GEO-Guide-{slug}-{date}.html"
        path.write_text(html)
        generated.append(str(path))

    print(json.dumps({"generated": generated}, indent=2))


if __name__ == "__main__":
    main()
