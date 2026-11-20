# ankimcp

A Claude Code plugin that connects to the MCP server run by the [AnkiMCP](https://ankimcp.ai) Anki add-on, so the server can be enabled from `settings.json` instead of a per-machine `claude mcp add`.

Unofficial; not affiliated with AnkiMCP or Anki.

## Requirements

- Anki 25.07 or newer, with the AnkiMCP add-on installed (AnkiWeb code `124672614`).
- Anki must be running: the add-on serves MCP at `http://127.0.0.1:3141/` only while Anki is open.

## Install

```
/plugin marketplace add ledhed2222/claude-plugins
/plugin install ankimcp@ledhed2222
```

Or declare it in `settings.json`:

```json
{
  "extraKnownMarketplaces": {
    "ledhed2222": {
      "source": { "source": "github", "repo": "ledhed2222/claude-plugins" }
    }
  },
  "enabledPlugins": {
    "ankimcp@ledhed2222": true
  }
}
```
