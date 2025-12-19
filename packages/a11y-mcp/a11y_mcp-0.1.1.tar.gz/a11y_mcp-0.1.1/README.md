# a11y-mcp

[![PyPI](https://img.shields.io/pypi/v/a11y-mcp)](https://pypi.org/project/a11y-mcp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

MCP server for running [axe-core](https://github.com/dequelabs/axe-core) accessibility audits. Uses [Camoufox](https://github.com/daijro/camoufox) to bypass Cloudflare and other bot protection.

## Install

```bash
# Claude Code
claude mcp add a11y -- uvx a11y-mcp

# Or with pip
pip install a11y-mcp
```

## Configuration

For Claude Desktop, add to your config (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "a11y": {
      "command": "uvx",
      "args": ["a11y-mcp"]
    }
  }
}
```

<details>
<summary>Other editors (Cursor, VS Code, Zed, etc.)</summary>

Most editors use the same format. Add to your MCP config:

```json
{
  "mcpServers": {
    "a11y": {
      "command": "uvx",
      "args": ["a11y-mcp"]
    }
  }
}
```

Config locations:
- **Cursor**: `~/.cursor/mcp.json`
- **VS Code (Continue)**: `.continue/config.json` under `experimental.modelContextProtocolServers`
- **VS Code (Cline)**: Cline MCP settings
- **Zed**: `~/.config/zed/settings.json` under `context_servers`

</details>

## Tools

| Tool | Description |
|------|-------------|
| `scan_page` | Scan a URL for WCAG violations |
| `scan_element` | Scan a specific CSS selector |
| `get_violations` | Get detailed violation info from last scan |
| `get_full_report` | Full axe results (violations, passes, incomplete) |
| `export_report` | Export as JSON, HTML, or CSV |
| `set_wcag_level` | Set WCAG level (A, AA, AAA, 21A, 21AA, 22AA) |
| `configure_rules` | Enable/disable specific axe rules |

## Usage

```
> Scan https://example.com for accessibility issues

> Export an HTML report for the last scan

> Check WCAG 2.2 AA compliance for https://adobe.com
```

## WCAG Levels

| Level | Standard |
|-------|----------|
| `A`, `AA`, `AAA` | WCAG 2.0 |
| `21A`, `21AA` | WCAG 2.1 |
| `22AA` | WCAG 2.2 |

Default is `AA`.

## Cloudflare Bypass

This uses Camoufox, an anti-detect browser with fingerprint spoofing at the C++ level. It handles JavaScript challenges, Turnstile, and most bot detection automatically.

On first run, Camoufox downloads a browser binary (~300MB).

## Requirements

- Python 3.10+
- macOS, Linux, or Windows

## Troubleshooting

**Browser won't launch**: Run `python -c "import camoufox; camoufox.install()"`

**Cloudflare still blocking**: Some sites have aggressive detection. The first visit may require manual verification.

**axe-core won't inject**: Likely a strict CSP. Try a different page on the same domain.

## Development

```bash
git clone https://github.com/anthropics/a11y-mcp && cd a11y-mcp
uv venv && source .venv/bin/activate
uv pip install -e ".[dev]"
python -m camoufox fetch
pytest
```

Debug with the MCP inspector:
```bash
npx @modelcontextprotocol/inspector uvx a11y-mcp
```

## License

MIT License - see [LICENSE](LICENSE) for details.

## Credits

- [axe-core](https://github.com/dequelabs/axe-core) - Accessibility testing engine by Deque
- [Camoufox](https://github.com/daijro/camoufox) - Anti-detect browser
- [MCP](https://modelcontextprotocol.io/) - Model Context Protocol by Anthropic

## Related Projects

- [mcp-server-fetch](https://github.com/modelcontextprotocol/servers/tree/main/src/fetch) - Web content fetching
- [mcp-server-puppeteer](https://github.com/modelcontextprotocol/servers/tree/main/src/puppeteer) - Browser automation
- [mcp-server-playwright](https://github.com/microsoft/playwright-mcp) - Playwright browser control
