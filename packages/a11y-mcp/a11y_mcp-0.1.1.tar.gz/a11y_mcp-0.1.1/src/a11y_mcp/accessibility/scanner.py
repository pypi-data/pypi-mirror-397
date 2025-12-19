"""
axe-core injection and accessibility scanning.

This module handles injecting the axe-core library into pages and
executing accessibility scans with configurable WCAG levels and rules.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Optional

from playwright.async_api import Page


class WCAGLevel(str, Enum):
    """WCAG conformance levels."""

    A = "wcag2a"
    AA = "wcag2aa"
    AAA = "wcag2aaa"
    WCAG21_A = "wcag21a"
    WCAG21_AA = "wcag21aa"
    WCAG22_AA = "wcag22aa"


@dataclass
class ScanOptions:
    """Configuration for accessibility scan."""

    wcag_level: WCAGLevel = WCAGLevel.AA
    rules: dict[str, bool] = field(default_factory=dict)  # Rule overrides
    include_selectors: list[str] = field(default_factory=list)
    exclude_selectors: list[str] = field(default_factory=list)


@dataclass
class ViolationNode:
    """Individual element that triggered a violation."""

    html: str
    target: list[str | list[str]]  # Can be nested for shadow DOM/iframes
    impact: str
    failure_summary: str


@dataclass
class Violation:
    """Accessibility violation result."""

    id: str
    impact: str  # minor, moderate, serious, critical
    description: str
    help: str
    help_url: str
    tags: list[str]
    nodes: list[ViolationNode]

    @property
    def wcag_tags(self) -> list[str]:
        """Get only WCAG-related tags."""
        return [t for t in self.tags if t.startswith("wcag")]

    @property
    def affected_count(self) -> int:
        """Number of affected elements."""
        return len(self.nodes)


@dataclass
class ScanResult:
    """Complete accessibility scan result."""

    url: str
    timestamp: str
    violations: list[Violation]
    passes: list[dict[str, Any]]
    incomplete: list[dict[str, Any]]
    inapplicable: list[dict[str, Any]]

    @property
    def violation_count(self) -> int:
        """Total number of violations."""
        return len(self.violations)

    @property
    def has_critical(self) -> bool:
        """Check if there are critical violations."""
        return any(v.impact == "critical" for v in self.violations)

    @property
    def has_serious(self) -> bool:
        """Check if there are serious violations."""
        return any(v.impact == "serious" for v in self.violations)

    def violations_by_impact(self) -> dict[str, list[Violation]]:
        """Group violations by impact level."""
        result: dict[str, list[Violation]] = {
            "critical": [],
            "serious": [],
            "moderate": [],
            "minor": [],
        }
        for v in self.violations:
            if v.impact in result:
                result[v.impact].append(v)
        return result

    def severity_counts(self) -> dict[str, int]:
        """Count violations by severity."""
        counts = {"critical": 0, "serious": 0, "moderate": 0, "minor": 0}
        for v in self.violations:
            if v.impact in counts:
                counts[v.impact] += 1
        return counts


class AccessibilityScanner:
    """
    Injects and runs axe-core for accessibility testing.

    axe-core is bundled locally to avoid CDN dependencies and
    ensure consistent results across scans.
    """

    AXE_SCRIPT_PATH = Path(__file__).parent.parent / "assets" / "axe.min.js"

    def __init__(self) -> None:
        self._axe_script: Optional[str] = None
        self._current_result: Optional[ScanResult] = None
        self._options = ScanOptions()

    async def _load_axe_script(self) -> str:
        """Load bundled axe-core script."""
        if self._axe_script is None:
            if not self.AXE_SCRIPT_PATH.exists():
                raise FileNotFoundError(
                    f"axe-core script not found at {self.AXE_SCRIPT_PATH}. "
                    "Run 'python scripts/download_axe.py' to download it."
                )
            self._axe_script = self.AXE_SCRIPT_PATH.read_text(encoding="utf-8")
        return self._axe_script

    async def inject_axe(self, page: Page) -> None:
        """
        Inject axe-core into the page.

        Must be called after page navigation and before scanning.
        """
        script = await self._load_axe_script()
        await page.evaluate(script)

        # Verify injection
        is_loaded = await page.evaluate("typeof window.axe !== 'undefined'")
        if not is_loaded:
            raise RuntimeError("Failed to inject axe-core into page")

    def configure(self, options: ScanOptions) -> None:
        """Configure scan options."""
        self._options = options

    def set_wcag_level(self, level: WCAGLevel) -> None:
        """Set WCAG conformance level."""
        self._options.wcag_level = level

    def configure_rules(self, rules: dict[str, bool]) -> None:
        """
        Enable or disable specific rules.

        Args:
            rules: Dict mapping rule IDs to enabled status
                   e.g., {"color-contrast": False, "valid-lang": True}
        """
        self._options.rules.update(rules)

    def reset_rules(self) -> None:
        """Reset rule configuration to defaults."""
        self._options.rules = {}

    def _get_wcag_tags(self) -> list[str]:
        """Get WCAG tags based on conformance level."""
        level = self._options.wcag_level

        # WCAG levels are cumulative
        tag_map = {
            WCAGLevel.A: ["wcag2a", "wcag21a", "wcag22a", "best-practice"],
            WCAGLevel.AA: ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22a", "wcag22aa", "best-practice"],
            WCAGLevel.AAA: ["wcag2a", "wcag2aa", "wcag2aaa", "wcag21a", "wcag21aa", "wcag21aaa", "best-practice"],
            WCAGLevel.WCAG21_A: ["wcag2a", "wcag21a", "best-practice"],
            WCAGLevel.WCAG21_AA: ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "best-practice"],
            WCAGLevel.WCAG22_AA: ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22a", "wcag22aa", "best-practice"],
        }

        return tag_map.get(level, ["wcag2a", "wcag2aa", "best-practice"])

    def _build_axe_options(self) -> dict[str, Any]:
        """Build axe.run() options from current configuration."""
        options: dict[str, Any] = {}

        # WCAG level tags
        wcag_tags = self._get_wcag_tags()
        if wcag_tags:
            options["runOnly"] = {"type": "tag", "values": wcag_tags}

        # Rule overrides
        if self._options.rules:
            options["rules"] = {
                rule_id: {"enabled": enabled}
                for rule_id, enabled in self._options.rules.items()
            }

        return options

    async def scan_page(self, page: Page) -> ScanResult:
        """
        Run full page accessibility scan.

        Injects axe-core and executes axe.run() with configured options.

        Args:
            page: Playwright page to scan

        Returns:
            ScanResult with violations, passes, and other findings
        """
        await self.inject_axe(page)

        # Build axe.run() options
        axe_options = self._build_axe_options()

        # Execute scan
        raw_result = await page.evaluate(
            """async (options) => {
                return await axe.run(document, options);
            }""",
            axe_options,
        )

        # Parse and store result
        self._current_result = self._parse_result(page.url, raw_result)
        return self._current_result

    async def scan_element(self, page: Page, selector: str) -> ScanResult:
        """
        Scan specific element by CSS selector.

        Args:
            page: Playwright page containing the element
            selector: CSS selector for the element to scan

        Returns:
            ScanResult with findings for the specified element
        """
        await self.inject_axe(page)

        axe_options = self._build_axe_options()

        raw_result = await page.evaluate(
            """async ([selector, options]) => {
                const element = document.querySelector(selector);
                if (!element) {
                    throw new Error(`Element not found: ${selector}`);
                }
                return await axe.run(element, options);
            }""",
            [selector, axe_options],
        )

        self._current_result = self._parse_result(page.url, raw_result)
        return self._current_result

    def _parse_result(self, url: str, raw: dict[str, Any]) -> ScanResult:
        """Parse raw axe result into structured ScanResult."""
        violations = [
            Violation(
                id=v["id"],
                impact=v.get("impact", "unknown"),
                description=v["description"],
                help=v["help"],
                help_url=v["helpUrl"],
                tags=v["tags"],
                nodes=[
                    ViolationNode(
                        html=n["html"],
                        target=n["target"],
                        impact=n.get("impact", "unknown"),
                        failure_summary=n.get("failureSummary", ""),
                    )
                    for n in v["nodes"]
                ],
            )
            for v in raw.get("violations", [])
        ]

        return ScanResult(
            url=url,
            timestamp=datetime.now(timezone.utc).isoformat(),
            violations=violations,
            passes=raw.get("passes", []),
            incomplete=raw.get("incomplete", []),
            inapplicable=raw.get("inapplicable", []),
        )

    def get_violations(self) -> list[Violation]:
        """Get violations from last scan."""
        if not self._current_result:
            return []
        return self._current_result.violations

    def get_full_report(self) -> Optional[ScanResult]:
        """Get complete scan result."""
        return self._current_result

    def clear_results(self) -> None:
        """Clear stored scan results."""
        self._current_result = None
