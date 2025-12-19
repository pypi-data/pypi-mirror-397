"""
Report generation for accessibility scan results.

Supports JSON, HTML, and CSV output formats for different use cases:
- JSON: Machine-readable, for integration with other tools
- HTML: Human-readable, styled report for stakeholders
- CSV: Spreadsheet-compatible for tracking and analysis
"""

import csv
import io
import json
from enum import Enum
from typing import Any

from jinja2 import Template

from .scanner import ScanResult


def flatten_target(target: list) -> str:
    """
    Flatten possibly nested axe-core target to a string selector.

    axe-core returns nested arrays for shadow DOM and iframe contexts.
    Each nested array represents a different document context.

    Examples:
        ["button"] -> "button"
        [["#host", "button"]] -> "#host > button"
        [["iframe"], ["#host", "button"]] -> "iframe >> #host > button"
    """
    parts = []
    for item in target:
        if isinstance(item, list):
            parts.append(" > ".join(item))
        else:
            parts.append(item)
    return " >> ".join(parts) if len(parts) > 1 else (parts[0] if parts else "")


class ReportFormat(str, Enum):
    """Supported report output formats."""

    JSON = "json"
    HTML = "html"
    CSV = "csv"


# HTML template for accessibility reports
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Accessibility Report - {{ url }}</title>
    <style>
        * { box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
            color: #333;
            line-height: 1.6;
        }
        h1 { color: #1a1a1a; border-bottom: 3px solid #0066cc; padding-bottom: 10px; }
        h2 { color: #333; margin-top: 30px; }
        h3 { margin: 0 0 10px 0; }

        .summary {
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .summary-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }
        .summary-item {
            text-align: center;
            padding: 15px;
            border-radius: 6px;
            background: #f8f9fa;
        }
        .summary-item .count {
            font-size: 2em;
            font-weight: bold;
            display: block;
        }
        .summary-item.critical .count { color: #dc3545; }
        .summary-item.serious .count { color: #fd7e14; }
        .summary-item.moderate .count { color: #ffc107; }
        .summary-item.minor .count { color: #17a2b8; }
        .summary-item.passes .count { color: #28a745; }

        .violation {
            background: white;
            border: 1px solid #ddd;
            margin: 15px 0;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        .violation.critical { border-left: 5px solid #dc3545; }
        .violation.serious { border-left: 5px solid #fd7e14; }
        .violation.moderate { border-left: 5px solid #ffc107; }
        .violation.minor { border-left: 5px solid #17a2b8; }

        .impact-badge {
            display: inline-block;
            padding: 3px 10px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: bold;
            text-transform: uppercase;
            margin-left: 10px;
        }
        .impact-badge.critical { background: #dc3545; color: white; }
        .impact-badge.serious { background: #fd7e14; color: white; }
        .impact-badge.moderate { background: #ffc107; color: #333; }
        .impact-badge.minor { background: #17a2b8; color: white; }

        .code {
            background: #f8f9fa;
            padding: 12px;
            font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
            font-size: 13px;
            overflow-x: auto;
            border-radius: 4px;
            border: 1px solid #e9ecef;
            margin: 10px 0;
            white-space: pre-wrap;
            word-break: break-all;
        }

        .tags {
            display: flex;
            gap: 5px;
            flex-wrap: wrap;
            margin: 10px 0;
        }
        .tag {
            background: #e9ecef;
            padding: 2px 8px;
            border-radius: 3px;
            font-size: 11px;
            color: #666;
        }
        .tag.wcag { background: #cce5ff; color: #004085; }

        .help-link {
            color: #0066cc;
            text-decoration: none;
        }
        .help-link:hover { text-decoration: underline; }

        .element-list { margin-top: 15px; }
        .element-item {
            background: #fafafa;
            padding: 10px;
            margin: 8px 0;
            border-radius: 4px;
            border: 1px solid #eee;
        }
        .element-item small { color: #666; }

        .no-violations {
            background: #d4edda;
            color: #155724;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }

        footer {
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            color: #666;
            font-size: 12px;
            text-align: center;
        }
    </style>
</head>
<body>
    <h1>Accessibility Report</h1>

    <div class="summary">
        <p><strong>URL:</strong> <a href="{{ url }}" target="_blank">{{ url }}</a></p>
        <p><strong>Scanned:</strong> {{ timestamp }}</p>

        <div class="summary-grid">
            <div class="summary-item critical">
                <span class="count">{{ severity_counts.critical }}</span>
                <span>Critical</span>
            </div>
            <div class="summary-item serious">
                <span class="count">{{ severity_counts.serious }}</span>
                <span>Serious</span>
            </div>
            <div class="summary-item moderate">
                <span class="count">{{ severity_counts.moderate }}</span>
                <span>Moderate</span>
            </div>
            <div class="summary-item minor">
                <span class="count">{{ severity_counts.minor }}</span>
                <span>Minor</span>
            </div>
            <div class="summary-item passes">
                <span class="count">{{ passes_count }}</span>
                <span>Passed</span>
            </div>
        </div>
    </div>

    <h2>Violations ({{ violations|length }})</h2>

    {% if violations %}
        {% for v in violations %}
        <div class="violation {{ v.impact }}">
            <h3>
                {{ v.help }}
                <span class="impact-badge {{ v.impact }}">{{ v.impact }}</span>
            </h3>
            <p>{{ v.description }}</p>

            <div class="tags">
                {% for tag in v.tags %}
                <span class="tag {% if tag.startswith('wcag') %}wcag{% endif %}">{{ tag }}</span>
                {% endfor %}
            </div>

            <p><a href="{{ v.help_url }}" target="_blank" class="help-link">Learn how to fix this issue</a></p>

            <div class="element-list">
                <strong>Affected Elements ({{ v.nodes|length }}):</strong>
                {% for node in v.nodes[:10] %}
                <div class="element-item">
                    <div class="code">{{ node.html }}</div>
                    <small>Selector: {{ node.target|flatten_target }}</small>
                    {% if node.failure_summary %}
                    <p><small>{{ node.failure_summary }}</small></p>
                    {% endif %}
                </div>
                {% endfor %}
                {% if v.nodes|length > 10 %}
                <p><em>... and {{ v.nodes|length - 10 }} more elements</em></p>
                {% endif %}
            </div>
        </div>
        {% endfor %}
    {% else %}
        <div class="no-violations">
            <h3>No accessibility violations found!</h3>
            <p>This page passed all automated accessibility checks.</p>
        </div>
    {% endif %}

    {% if incomplete %}
    <h2>Needs Review ({{ incomplete|length }})</h2>
    <p>These items require manual review to determine if they are violations.</p>
    <ul>
        {% for item in incomplete[:20] %}
        <li><strong>{{ item.id }}</strong>: {{ item.description }}</li>
        {% endfor %}
    </ul>
    {% endif %}

    <footer>
        <p>Generated by a11y-mcp using axe-core</p>
        <p>Note: Automated testing finds ~30-50% of issues. Manual testing recommended.</p>
    </footer>
</body>
</html>"""


class ReportGenerator:
    """Generate accessibility reports in various formats."""

    @staticmethod
    def generate(result: ScanResult, format: ReportFormat) -> str:
        """
        Generate report in specified format.

        Args:
            result: Scan result to format
            format: Output format (json, html, csv)

        Returns:
            Formatted report as string

        Raises:
            ValueError: If format is not supported
        """
        if format == ReportFormat.JSON:
            return ReportGenerator._to_json(result)
        elif format == ReportFormat.HTML:
            return ReportGenerator._to_html(result)
        elif format == ReportFormat.CSV:
            return ReportGenerator._to_csv(result)
        else:
            raise ValueError(f"Unsupported format: {format}")

    @staticmethod
    def _to_json(result: ScanResult) -> str:
        """Convert to JSON format."""
        data: dict[str, Any] = {
            "url": result.url,
            "timestamp": result.timestamp,
            "summary": {
                "total_violations": result.violation_count,
                "by_severity": result.severity_counts(),
                "passes": len(result.passes),
                "incomplete": len(result.incomplete),
                "inapplicable": len(result.inapplicable),
            },
            "violations": [
                {
                    "id": v.id,
                    "impact": v.impact,
                    "description": v.description,
                    "help": v.help,
                    "helpUrl": v.help_url,
                    "tags": v.tags,
                    "wcagTags": v.wcag_tags,
                    "nodes": [
                        {
                            "html": n.html,
                            "target": n.target,
                            "failureSummary": n.failure_summary,
                        }
                        for n in v.nodes
                    ],
                }
                for v in result.violations
            ],
            "passes": [
                {"id": p["id"], "description": p.get("description", "")}
                for p in result.passes
            ],
            "incomplete": [
                {"id": i["id"], "description": i.get("description", "")}
                for i in result.incomplete
            ],
        }
        return json.dumps(data, indent=2, ensure_ascii=False)

    @staticmethod
    def _to_html(result: ScanResult) -> str:
        """Convert to HTML format."""
        template = Template(HTML_TEMPLATE)
        template.globals["flatten_target"] = flatten_target
        return template.render(
            url=result.url,
            timestamp=result.timestamp,
            violations=result.violations,
            passes_count=len(result.passes),
            incomplete=result.incomplete,
            severity_counts=result.severity_counts(),
        )

    @staticmethod
    def _to_csv(result: ScanResult) -> str:
        """Convert violations to CSV format."""
        output = io.StringIO()
        writer = csv.writer(output)

        # Header row
        writer.writerow(
            [
                "Rule ID",
                "Impact",
                "Description",
                "Help",
                "Help URL",
                "WCAG Tags",
                "Element HTML",
                "Target Selector",
                "Failure Summary",
            ]
        )

        # Violation rows - one row per affected element
        for v in result.violations:
            for node in v.nodes:
                writer.writerow(
                    [
                        v.id,
                        v.impact,
                        v.description,
                        v.help,
                        v.help_url,
                        ", ".join(v.wcag_tags),
                        node.html,
                        flatten_target(node.target),
                        node.failure_summary,
                    ]
                )

        return output.getvalue()
