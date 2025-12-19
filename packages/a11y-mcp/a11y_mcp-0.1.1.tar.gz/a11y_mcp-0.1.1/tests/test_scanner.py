"""Tests for the accessibility scanner module."""

import pytest
from pathlib import Path


class TestAccessibilityScanner:
    """Test suite for AccessibilityScanner."""

    def test_axe_script_exists(self) -> None:
        """Verify axe-core script is bundled."""
        axe_path = (
            Path(__file__).parent.parent
            / "src"
            / "a11y_mcp"
            / "assets"
            / "axe.min.js"
        )
        assert axe_path.exists(), "axe.min.js should be bundled"
        assert axe_path.stat().st_size > 100_000, "axe.min.js should be > 100KB"

    def test_wcag_level_enum(self) -> None:
        """Test WCAG level enum values."""
        from a11y_mcp.accessibility.scanner import WCAGLevel

        assert WCAGLevel.A.value == "wcag2a"
        assert WCAGLevel.AA.value == "wcag2aa"
        assert WCAGLevel.AAA.value == "wcag2aaa"
        assert WCAGLevel.WCAG21_AA.value == "wcag21aa"
        assert WCAGLevel.WCAG22_AA.value == "wcag22aa"

    def test_report_format_enum(self) -> None:
        """Test report format enum values."""
        from a11y_mcp.accessibility.report import ReportFormat

        assert ReportFormat.JSON.value == "json"
        assert ReportFormat.HTML.value == "html"
        assert ReportFormat.CSV.value == "csv"


class TestBrowserConfig:
    """Test suite for BrowserConfig."""

    def test_default_config(self) -> None:
        """Test default browser configuration."""
        from a11y_mcp.browser.manager import BrowserConfig

        config = BrowserConfig()
        assert config.headless is True
        assert config.humanize is True
        assert config.timeout == 60000
        assert config.window_width == 1920
        assert config.window_height == 1080
