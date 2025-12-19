# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.1] - 2025-12-18

### Fixed

- CSV export now handles shadow DOM and iframe elements correctly
- HTML report selector display for nested element contexts

### Changed

- Renamed internal module from `a11y_agent` to `a11y_mcp` for consistency

## [0.1.0] - 2025-12-17

### Added

- Initial release of a11y-mcp
- Cloudflare bypass using Camoufox anti-detect browser
- axe-core integration for accessibility testing (v4.10.2)
- Support for WCAG 2.0, 2.1, and 2.2 at levels A, AA, and AAA
- MCP tools:
  - `scan_page` - Navigate and scan URL for accessibility issues
  - `scan_element` - Scan specific element on page
  - `get_violations` - Get detailed violation list
  - `get_full_report` - Get complete accessibility report
  - `configure_rules` - Enable/disable specific rules
  - `set_wcag_level` - Set WCAG conformance level
  - `export_report` - Export as JSON, HTML, or CSV
- Report generation in JSON, HTML, and CSV formats
- Compatible with Claude Desktop, Claude Code, VS Code, and other MCP clients
