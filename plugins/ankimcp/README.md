# ankimcp

A Claude Code plugin that connects to a self-hosted [anki-sync-mcp](https://github.com/ledhed2222/anki-sync-mcp) server, so the server can be enabled from `settings.json` instead of a per-machine `claude mcp add`.

Unofficial; not affiliated with Anki or AnkiWeb.

## Requirements

- A running anki-sync-mcp server in built-in OAuth mode (`MCP_AUTH_MODE=builtin`), reachable over HTTPS. See its README for setup.
- `http://localhost:33418/callback` added to the server's `MCP_OAUTH_REDIRECT_URIS`. The plugin pins Claude Code's OAuth callback to port 33418 so the server can allow-list it exactly.

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

When the plugin is enabled, Claude Code asks for the server URL, for example `https://anki.example.com/mcp`. Then run `/mcp` and sign in with the server's owner password.
