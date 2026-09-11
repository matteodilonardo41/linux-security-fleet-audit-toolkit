#!/usr/bin/env python3

import argparse
import json
from datetime import datetime, timezone
from html import escape
from pathlib import Path
from typing import Any


SEVERITIES = ("CRITICAL", "HIGH", "WARNING", "INFO", "OK")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate an HTML security report from fleet analysis JSON."
    )

    parser.add_argument(
        "--input",
        type=Path,
        required=True,
        help="Fleet analysis JSON file.",
    )

    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Destination HTML report.",
    )

    return parser.parse_args()


def load_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def severity_badge(severity: str) -> str:
    safe = escape(severity)
    css_class = severity.lower()

    return f'<span class="badge {css_class}">{safe}</span>'


def build_summary_cards(report: dict[str, Any]) -> str:
    summary = report.get("finding_summary", {})

    cards = []

    for severity in SEVERITIES:
        count = summary.get(severity, 0)

        cards.append(
            f"""
            <div class="summary-card {severity.lower()}">
                <div class="summary-value">{count}</div>
                <div class="summary-label">{severity}</div>
            </div>
            """
        )

    return "\n".join(cards)


def build_fleet_table(report: dict[str, Any]) -> str:
    rows = []

    for host in report.get("hosts", []):
        system = host.get("system", {})
        findings = host.get("findings", [])

        non_ok = sum(
            1
            for finding in findings
            if finding.get("severity") != "OK"
        )

        rows.append(
            f"""
            <tr>
                <td>{escape(str(host.get("host", "unknown")))}</td>
                <td>{escape(str(host.get("role", "generic")))}</td>
                <td>
                    {escape(str(system.get("distribution", "unknown")))}
                    {escape(str(system.get("distribution_version", "")))}
                </td>
                <td>{escape(str(system.get("kernel", "unknown")))}</td>
                <td>{severity_badge(str(host.get("status", "OK")))}</td>
                <td>{non_ok}</td>
            </tr>
            """
        )

    return "\n".join(rows)


def build_findings(report: dict[str, Any]) -> str:
    sections = []

    for host in report.get("hosts", []):
        host_findings = []

        for finding in host.get("findings", []):
            severity = str(finding.get("severity", "INFO"))
            title = escape(str(finding.get("title", "Unnamed finding")))
            control_id = escape(str(finding.get("control_id", "N/A")))
            recommendation = escape(
                str(finding.get("recommendation", ""))
            )

            evidence_items = []

            for item in finding.get("evidence", []):
                evidence_items.append(
                    f"<li><code>{escape(str(item))}</code></li>"
                )

            if evidence_items:
                evidence_html = (
                    "<div class=\"evidence-title\">Evidence</div>"
                    "<ul class=\"evidence-list\">"
                    + "".join(evidence_items)
                    + "</ul>"
                )
            else:
                evidence_html = ""

            if recommendation:
                recommendation_html = (
                    "<div class=\"recommendation\">"
                    "<strong>Recommendation:</strong> "
                    f"{recommendation}"
                    "</div>"
                )
            else:
                recommendation_html = ""

            host_findings.append(
                f"""
                <article class="finding {severity.lower()}">
                    <div class="finding-header">
                        {severity_badge(severity)}
                        <span class="control-id">{control_id}</span>
                    </div>

                    <h3>{title}</h3>

                    {evidence_html}
                    {recommendation_html}
                </article>
                """
            )

        sections.append(
            f"""
            <section class="host-detail">
                <div class="host-title">
                    <h2>{escape(str(host.get("host", "unknown")))}</h2>
                    {severity_badge(str(host.get("status", "OK")))}
                </div>

                <div class="host-meta">
                    Role: {escape(str(host.get("role", "generic")))}
                </div>

                {''.join(host_findings)}
            </section>
            """
        )

    return "\n".join(sections)


def build_html(report: dict[str, Any]) -> str:
    generated_at = datetime.now(timezone.utc).strftime(
        "%Y-%m-%d %H:%M:%S UTC"
    )

    host_count = report.get("host_count", 0)
    overall_status = "OK"
    host_status_summary = report.get("host_status_summary", {})

    for severity in SEVERITIES:
        if host_status_summary.get(severity, 0) > 0:
            overall_status = severity
            break
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">

<title>Linux Security Fleet Audit</title>

<style>
    :root {{
        --background: #0b1020;
        --panel: #151b2d;
        --panel-light: #1c2438;
        --text: #e7eaf0;
        --muted: #9aa5b5;
        --border: #2c354a;
        --critical: #d7263d;
        --high: #ef476f;
        --warning: #f4a261;
        --info: #4ea8de;
        --ok: #2a9d8f;
    }}

    * {{
        box-sizing: border-box;
    }}

    body {{
        margin: 0;
        font-family:
            Inter,
            -apple-system,
            BlinkMacSystemFont,
            "Segoe UI",
            sans-serif;
        background: var(--background);
        color: var(--text);
        line-height: 1.5;
    }}

    .container {{
        max-width: 1180px;
        margin: 0 auto;
        padding: 40px 24px 80px;
    }}

    .hero {{
        padding: 36px;
        border: 1px solid var(--border);
        border-radius: 18px;
        background:
            linear-gradient(
                135deg,
                #151b2d 0%,
                #101729 100%
            );
        margin-bottom: 28px;
    }}

    h1 {{
        margin: 0 0 8px;
        font-size: 34px;
    }}

    .subtitle {{
        color: var(--muted);
        margin-bottom: 22px;
    }}

    .metadata {{
        display: flex;
        gap: 24px;
        flex-wrap: wrap;
        color: var(--muted);
        font-size: 14px;
    }}

    .summary-grid {{
        display: grid;
        grid-template-columns:
            repeat(auto-fit, minmax(150px, 1fr));
        gap: 16px;
        margin: 28px 0;
    }}

    .summary-card {{
        border-radius: 14px;
        padding: 20px;
        background: var(--panel);
        border: 1px solid var(--border);
    }}

    .summary-value {{
        font-size: 32px;
        font-weight: 700;
    }}

    .summary-label {{
        margin-top: 3px;
        font-size: 13px;
        letter-spacing: 0.08em;
        color: var(--muted);
    }}

    .summary-card.critical {{
        border-top: 4px solid var(--critical);
    }}

    .summary-card.high {{
        border-top: 4px solid var(--high);
    }}

    .summary-card.warning {{
        border-top: 4px solid var(--warning);
    }}

    .summary-card.info {{
        border-top: 4px solid var(--info);
    }}

    .summary-card.ok {{
        border-top: 4px solid var(--ok);
    }}

    .panel {{
        background: var(--panel);
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 24px;
        margin-top: 28px;
        overflow-x: auto;
    }}

    table {{
        width: 100%;
        border-collapse: collapse;
    }}

    th,
    td {{
        padding: 13px 12px;
        border-bottom: 1px solid var(--border);
        text-align: left;
        white-space: nowrap;
    }}

    th {{
        color: var(--muted);
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }}

    .badge {{
        display: inline-block;
        padding: 5px 9px;
        border-radius: 999px;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.05em;
    }}

    .badge.critical {{
        background: var(--critical);
    }}

    .badge.high {{
        background: var(--high);
    }}

    .badge.warning {{
        background: var(--warning);
        color: #151515;
    }}

    .badge.info {{
        background: var(--info);
    }}

    .badge.ok {{
        background: var(--ok);
    }}

    .host-detail {{
        margin-top: 38px;
    }}

    .host-title {{
        display: flex;
        align-items: center;
        gap: 12px;
    }}

    .host-title h2 {{
        margin: 0;
    }}

    .host-meta {{
        color: var(--muted);
        margin: 4px 0 16px;
    }}

    .finding {{
        background: var(--panel);
        border: 1px solid var(--border);
        border-left-width: 5px;
        border-radius: 12px;
        padding: 20px;
        margin: 14px 0;
    }}

    .finding.critical {{
        border-left-color: var(--critical);
    }}

    .finding.high {{
        border-left-color: var(--high);
    }}

    .finding.warning {{
        border-left-color: var(--warning);
    }}

    .finding.info {{
        border-left-color: var(--info);
    }}

    .finding.ok {{
        border-left-color: var(--ok);
    }}

    .finding-header {{
        display: flex;
        gap: 10px;
        align-items: center;
    }}

    .finding h3 {{
        margin: 12px 0;
    }}

    .control-id {{
        color: var(--muted);
        font-family: monospace;
        font-size: 12px;
    }}

    .evidence-title {{
        font-weight: 600;
        margin-top: 14px;
    }}

    .evidence-list {{
        margin-top: 8px;
    }}

    code {{
        color: #d6e3ff;
        overflow-wrap: anywhere;
    }}

    .recommendation {{
        margin-top: 16px;
        padding: 12px 14px;
        border-radius: 8px;
        background: var(--panel-light);
    }}

    footer {{
        color: var(--muted);
        margin-top: 50px;
        font-size: 13px;
        text-align: center;
    }}

    @media print {{
        body {{
            background: white;
            color: #151515;
        }}

        .hero,
        .panel,
        .finding,
        .summary-card {{
            background: white;
            color: #151515;
            break-inside: avoid;
        }}

        code {{
            color: #151515;
        }}

        .host-detail {{
            break-before: auto;
        }}
    }}
</style>
</head>

<body>

<div class="container">

    <header class="hero">
        <h1>Linux Security Fleet Audit</h1>

        <div class="subtitle">
            Automated non-destructive Linux security assessment
        </div>

        <div class="metadata">
            <span>Generated: {escape(generated_at)}</span>
            <span>Hosts analyzed: {escape(str(host_count))}</span>
            <span>Public Edition</span>
            <span>Fictitious demo data</span>
            <span>Overall status: {severity_badge(overall_status)}</span>
        </div>
    </header>

    <section>
        <h2>Security Findings</h2>

        <div class="summary-grid">
            {build_summary_cards(report)}
        </div>
    </section>

    <section class="panel">
        <h2>Fleet Status</h2>

        <table>
            <thead>
                <tr>
                    <th>Host</th>
                    <th>Role</th>
                    <th>Operating System</th>
                    <th>Kernel</th>
                    <th>Status</th>
                    <th>Non-OK Findings</th>
                </tr>
            </thead>

            <tbody>
                {build_fleet_table(report)}
            </tbody>
        </table>
    </section>

    <section>
        <h2>Technical Details</h2>

        {build_findings(report)}
    </section>

    <footer>
        Linux Security Fleet Audit Toolkit · Public Edition
    </footer>

</div>

</body>
</html>
"""


def main() -> int:
    args = parse_args()

    if not args.input.exists():
        raise SystemExit(
            f"Input report does not exist: {args.input}"
        )

    report = load_report(args.input)

    args.output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    html = build_html(report)

    args.output.write_text(
        html,
        encoding="utf-8",
    )

    print(
        f"HTML report written to {args.output}"
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
