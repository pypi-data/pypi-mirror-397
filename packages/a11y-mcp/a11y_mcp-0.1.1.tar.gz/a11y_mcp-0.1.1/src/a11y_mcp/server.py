"""
MCP Server for accessibility testing with Cloudflare bypass.

This server exposes tools for AI agents to perform accessibility audits
on websites, including those protected by Cloudflare. It uses Camoufox
(an anti-detect browser) for navigation and axe-core for accessibility testing.

Tools:
    - scan_page: Navigate to URL and run accessibility scan
    - scan_element: Scan specific element on current page
    - get_violations: Get detailed violations from last scan
    - get_full_report: Get complete accessibility report
    - configure_rules: Enable/disable specific accessibility rules
    - set_wcag_level: Set WCAG conformance level
    - export_report: Export report as JSON, HTML, or CSV
"""

import asyncio
from typing import Any, Optional

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

from .accessibility.report import ReportFormat, ReportGenerator
from .accessibility.scanner import AccessibilityScanner, ScanResult, WCAGLevel
from .browser.manager import BrowserConfig, BrowserManager

# Initialize MCP server
mcp = FastMCP(name="a11y-agent")

# Global state for browser and scanner singletons
_browser_manager: Optional[BrowserManager] = None
_scanner: Optional[AccessibilityScanner] = None
_lock = asyncio.Lock()


async def get_browser() -> BrowserManager:
    """Get or create browser manager singleton."""
    global _browser_manager
    async with _lock:
        if _browser_manager is None:
            config = BrowserConfig(
                headless=True,
                user_data_dir=None,  # Disable persistent context for now
                humanize=True,
                timeout=60000,
            )
            _browser_manager = BrowserManager(config)
            await _browser_manager.initialize()
        return _browser_manager


async def get_scanner() -> AccessibilityScanner:
    """Get or create scanner singleton."""
    global _scanner
    if _scanner is None:
        _scanner = AccessibilityScanner()
    return _scanner


# =============================================================================
# Pydantic Models for Tool Parameters
# =============================================================================


class ScanPageInput(BaseModel):
    """Input parameters for scan_page tool."""

    url: str = Field(description="The URL to scan for accessibility issues")
    wcag_level: str = Field(
        default="AA",
        description="WCAG conformance level: A, AA, AAA, 21A, 21AA, or 22AA",
    )
    wait_for_cloudflare: bool = Field(
        default=True,
        description="Wait for Cloudflare challenges to complete before scanning",
    )


class ScanElementInput(BaseModel):
    """Input parameters for scan_element tool."""

    selector: str = Field(
        description="CSS selector for the element to scan (e.g., '#main-content', '.nav-menu')"
    )


class ConfigureRulesInput(BaseModel):
    """Input parameters for configure_rules tool."""

    rules: dict[str, bool] = Field(
        description="Map of rule IDs to enabled status. Example: {'color-contrast': false, 'image-alt': true}"
    )


class SetWcagLevelInput(BaseModel):
    """Input parameters for set_wcag_level tool."""

    level: str = Field(
        description="WCAG level code: A, AA, AAA, 21A, 21AA, or 22AA"
    )


class ExportReportInput(BaseModel):
    """Input parameters for export_report tool."""

    format: str = Field(
        description="Output format: 'json', 'html', or 'csv'"
    )


# =============================================================================
# Helper Functions
# =============================================================================


def _get_wcag_level(level_str: str) -> Optional[WCAGLevel]:
    """Convert string to WCAGLevel enum."""
    level_map = {
        "A": WCAGLevel.A,
        "AA": WCAGLevel.AA,
        "AAA": WCAGLevel.AAA,
        "21A": WCAGLevel.WCAG21_A,
        "21AA": WCAGLevel.WCAG21_AA,
        "22AA": WCAGLevel.WCAG22_AA,
    }
    return level_map.get(level_str.upper())


def _format_selector(target: list) -> str:
    """Format axe-core target selector for display.

    Target can be a list of strings or a list of lists (for shadow DOM, iframes).
    """
    if not target:
        return ""

    parts = []
    for item in target:
        if isinstance(item, list):
            parts.append(" > ".join(str(x) for x in item))
        else:
            parts.append(str(item))

    return " > ".join(parts)


def _format_scan_summary(result: ScanResult, wcag_level: str) -> dict[str, Any]:
    """Format scan result as summary dict."""
    severity_counts = result.severity_counts()

    return {
        "success": True,
        "url": result.url,
        "timestamp": result.timestamp,
        "wcag_level": wcag_level,
        "summary": {
            "total_violations": result.violation_count,
            "by_severity": severity_counts,
            "passes": len(result.passes),
            "incomplete": len(result.incomplete),
        },
        "has_critical_issues": result.has_critical,
        "has_serious_issues": result.has_serious,
    }


# =============================================================================
# MCP Tool Definitions
# =============================================================================


@mcp.tool()
async def scan_page(url: str, wcag_level: str = "AA", wait_for_cloudflare: bool = True) -> dict[str, Any]:
    """
    Navigate to a URL, bypass Cloudflare if present, and run an accessibility scan.

    This tool uses an anti-detect browser (Camoufox) that can bypass Cloudflare
    protection, then injects axe-core and runs a full accessibility audit.

    Args:
        url: The URL to scan for accessibility issues
        wcag_level: WCAG conformance level (A, AA, AAA, 21A, 21AA, 22AA). Default: AA
        wait_for_cloudflare: Wait for Cloudflare challenges to complete. Default: True

    Returns:
        Summary of accessibility scan including violation counts by severity
    """
    browser = await get_browser()
    scanner = await get_scanner()

    # Set WCAG level
    level = _get_wcag_level(wcag_level)
    if level:
        scanner.set_wcag_level(level)

    # Navigate with Cloudflare bypass
    try:
        await browser.navigate(url, wait_for_cloudflare=wait_for_cloudflare)
    except TimeoutError as e:
        return {
            "success": False,
            "error": str(e),
            "url": url,
            "suggestion": "Try increasing timeout or check if the site is accessible",
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Navigation failed: {str(e)}",
            "url": url,
        }

    # Run scan
    try:
        result = await scanner.scan_page(browser.page)
        return _format_scan_summary(result, wcag_level)
    except Exception as e:
        return {
            "success": False,
            "error": f"Scan failed: {str(e)}",
            "url": url,
        }


@mcp.tool()
async def scan_element(selector: str) -> dict[str, Any]:
    """
    Scan a specific element on the current page for accessibility issues.

    Must be called after scan_page() has loaded a page. Runs axe-core
    on just the specified element and its descendants.

    Args:
        selector: CSS selector for the element to scan (e.g., '#main-nav', '.form-container')

    Returns:
        Accessibility scan results for the specified element
    """
    browser = await get_browser()
    scanner = await get_scanner()

    if not browser.is_initialized:
        return {
            "success": False,
            "error": "No page loaded. Call scan_page() first to navigate to a URL.",
        }

    try:
        result = await scanner.scan_element(browser.page, selector)
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "selector": selector,
        }

    return {
        "success": True,
        "selector": selector,
        "total_violations": result.violation_count,
        "violations": [
            {
                "id": v.id,
                "impact": v.impact,
                "help": v.help,
                "affected_elements": v.affected_count,
            }
            for v in result.violations
        ],
    }


@mcp.tool()
async def get_violations() -> dict[str, Any]:
    """
    Get detailed list of violations from the most recent scan.

    Returns full violation details including affected elements,
    WCAG references, and remediation guidance.

    Returns:
        List of violations with complete details including affected HTML elements
    """
    scanner = await get_scanner()
    violations = scanner.get_violations()

    if not violations:
        return {
            "success": True,
            "count": 0,
            "violations": [],
            "message": "No violations found or no scan performed yet.",
        }

    return {
        "success": True,
        "count": len(violations),
        "violations": [
            {
                "id": v.id,
                "impact": v.impact,
                "description": v.description,
                "help": v.help,
                "help_url": v.help_url,
                "wcag_tags": v.wcag_tags,
                "affected_elements": [
                    {
                        "html": n.html[:500] if len(n.html) > 500 else n.html,  # Truncate long HTML
                        "selector": _format_selector(n.target),
                        "issue": n.failure_summary,
                    }
                    for n in v.nodes[:10]  # Limit to first 10 nodes
                ],
                "total_affected": len(v.nodes),
            }
            for v in violations
        ],
    }


@mcp.tool()
async def get_full_report() -> dict[str, Any]:
    """
    Get complete accessibility report from the last scan.

    Includes violations, passes, incomplete checks, and inapplicable rules.
    Use this for comprehensive analysis of accessibility compliance.

    Returns:
        Complete scan results including all categories (violations, passes, incomplete, inapplicable)
    """
    scanner = await get_scanner()
    result = scanner.get_full_report()

    if not result:
        return {
            "success": False,
            "error": "No scan results available. Run scan_page() first.",
        }

    return {
        "success": True,
        "url": result.url,
        "timestamp": result.timestamp,
        "violations": {
            "count": len(result.violations),
            "by_severity": result.severity_counts(),
            "items": [
                {"id": v.id, "impact": v.impact, "help": v.help, "affected": v.affected_count}
                for v in result.violations
            ],
        },
        "passes": {
            "count": len(result.passes),
            "items": [
                {"id": p["id"], "description": p.get("description", "")}
                for p in result.passes[:20]  # First 20 passes
            ],
        },
        "incomplete": {
            "count": len(result.incomplete),
            "items": [
                {"id": i["id"], "description": i.get("description", "")}
                for i in result.incomplete
            ],
        },
        "inapplicable_count": len(result.inapplicable),
    }


@mcp.tool()
async def configure_rules(rules: dict[str, bool]) -> dict[str, Any]:
    """
    Enable or disable specific accessibility rules.

    Use this to customize which rules are checked during scans.
    Changes apply to all subsequent scans until reconfigured.

    Common rules to disable:
    - color-contrast: Color contrast checks
    - image-alt: Image alt text requirements
    - link-name: Link text requirements
    - region: Landmark region requirements

    Args:
        rules: Map of rule IDs to enabled status. Example: {'color-contrast': false}

    Returns:
        Confirmation of applied configuration
    """
    scanner = await get_scanner()
    scanner.configure_rules(rules)

    enabled = [k for k, v in rules.items() if v]
    disabled = [k for k, v in rules.items() if not v]

    return {
        "success": True,
        "message": f"Configured {len(rules)} rule(s)",
        "enabled": enabled,
        "disabled": disabled,
    }


@mcp.tool()
async def set_wcag_level(level: str) -> dict[str, Any]:
    """
    Set WCAG conformance level for accessibility testing.

    Available levels:
    - A: WCAG 2.0 Level A (minimum accessibility)
    - AA: WCAG 2.0 Level AA (standard compliance target, recommended)
    - AAA: WCAG 2.0 Level AAA (enhanced accessibility)
    - 21A: WCAG 2.1 Level A
    - 21AA: WCAG 2.1 Level AA
    - 22AA: WCAG 2.2 Level AA (latest standard)

    Args:
        level: WCAG level code (A, AA, AAA, 21A, 21AA, 22AA)

    Returns:
        Confirmation of WCAG level setting with tags that will be used
    """
    valid_levels = ["A", "AA", "AAA", "21A", "21AA", "22AA"]

    wcag_level = _get_wcag_level(level)
    if not wcag_level:
        return {
            "success": False,
            "error": f"Invalid WCAG level: {level}",
            "valid_options": valid_levels,
        }

    scanner = await get_scanner()
    scanner.set_wcag_level(wcag_level)

    # Get the tags that will be used
    tags = scanner._get_wcag_tags()

    return {
        "success": True,
        "level": level.upper(),
        "description": f"WCAG {level.upper()} conformance level set",
        "tags_enabled": tags,
    }


@mcp.tool()
async def export_report(format: str) -> dict[str, Any]:
    """
    Export accessibility report in the specified format.

    Generates a formatted report from the last scan results.

    Formats:
    - json: Machine-readable JSON with full details
    - html: Styled HTML report for stakeholders
    - csv: Spreadsheet-compatible format for tracking

    Args:
        format: Output format - 'json', 'html', or 'csv'

    Returns:
        Formatted report content as a string
    """
    format_lower = format.lower()
    format_map = {
        "json": ReportFormat.JSON,
        "html": ReportFormat.HTML,
        "csv": ReportFormat.CSV,
    }

    report_format = format_map.get(format_lower)
    if not report_format:
        return {
            "success": False,
            "error": f"Invalid format: {format}",
            "valid_options": ["json", "html", "csv"],
        }

    scanner = await get_scanner()
    result = scanner.get_full_report()

    if not result:
        return {
            "success": False,
            "error": "No scan results available. Run scan_page() first.",
        }

    try:
        report = ReportGenerator.generate(result, report_format)
    except Exception as e:
        return {
            "success": False,
            "error": f"Report generation failed: {str(e)}",
        }

    return {
        "success": True,
        "format": format_lower,
        "url": result.url,
        "content": report,
    }


# =============================================================================
# Server Entry Point
# =============================================================================


async def cleanup() -> None:
    """Cleanup browser on shutdown."""
    global _browser_manager
    if _browser_manager:
        await _browser_manager.close()
        _browser_manager = None


def main() -> None:
    """Run the MCP server."""
    import atexit
    import signal

    # Register cleanup handlers
    def sync_cleanup() -> None:
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.create_task(cleanup())
            else:
                loop.run_until_complete(cleanup())
        except Exception:
            pass

    atexit.register(sync_cleanup)

    # Handle SIGTERM gracefully
    def sigterm_handler(signum: int, frame: Any) -> None:
        sync_cleanup()
        raise SystemExit(0)

    signal.signal(signal.SIGTERM, sigterm_handler)

    # Run the MCP server
    mcp.run()


if __name__ == "__main__":
    main()
