# RTLViz - AI-Powered RTL Diagram Generator

> ⚠️ **Development Notice**: This project is under active development. It can make mistakes. Please verify generated diagrams against your design.

An MCP (Model Context Protocol) server that enables AI assistants to generate publication-quality RTL block diagrams from Verilog/SystemVerilog code.

## Installation

```bash
pip install rtlviz
rtlviz-setup
```

That's it! The setup command auto-configures your AI IDE (Claude Desktop or VS Code).

### Manual Setup (Alternative)

If auto-setup doesn't work, you can configure manually:

**Claude Desktop** (`claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "rtlviz": {
      "command": "rtlviz-server"
    }
  }
}
```

**VS Code** (`.vscode/mcp.json`):
```json
{
  "servers": {
    "rtlviz": {
      "command": "rtlviz-server"
    }
  }
}
```

## Usage

Just ask your AI: **"Generate an RTL diagram for CPU.v"**

> 💡 **Recommended**: Works best with latest AI models like **Claude Opus 4.5** or **Claude Sonnet 4.5** for accurate RTL analysis.

## How It Works

1. **You install** the package (`pip install rtlviz`)
2. **Your IDE** spawns the server locally when you open a session
3. **The AI** reads the `rtlviz://prompt` resource to learn how to analyze RTL
4. **The AI** generates Graphviz DOT code based on your Verilog
5. **The AI** calls the `render_diagram` tool to create an interactive HTML viewer

**No server hosting required. No API keys. Runs 100% locally.**

## Enterprise & Privacy

- **Safe for Work**: All RTL analysis happens locally or via your enterprise-approved LLM provider.
- **Telemetry**: We collect minimal, anonymous usage data (version, session ID) to improve the tool.
  - **No IP addresses** or personal data.
  - **No file contents** or code.
- **Opt-Out**: Set the environment variable `RTLVIZ_TELEMETRY=0` to disable all network calls.
  - **Firewall Friendly**: If blocked, the tool fails silently and continues working.

## Developing & Releasing

### Analytics Setup
To enable your own analytics dashboard:
1. Deploy `analytics/google_apps_script.js` as a Google Web App (Execute as Me, Access: Anyone).
2. Set `RTLVIZ_TELEMETRY_URL` in `src/rtlviz/telemetry.py` to your Web App URL.

### Publishing to PyPI
1. **Bump Version**: Update `pyproject.toml` and `src/rtlviz/telemetry.py`.
2. **Build**: `python -m build`
3. **Upload**: `twine upload dist/*`

## Developers

- **Naveen Venkat** - [naveenvenkat1711@gmail.com](mailto:naveenvenkat1711@gmail.com)
- **Hariharan** - [hari.ayyaps@gmail.com](mailto:hari.ayyaps@gmail.com)

## License

MIT
