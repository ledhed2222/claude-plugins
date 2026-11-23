# ankimcp

A Claude Code plugin that connects Claude Code to an Anki MCP server, so the server can be enabled from `settings.json` instead of a per-machine `claude mcp add`. It works with either of two servers; you choose one by the URL you give it.

Unofficial; not affiliated with Anki, AnkiWeb or AnkiMCP.

## Choose a server

The two servers have different tools, so a skill written for one may not work with the other.

### Local: the AnkiMCP add-on

Runs inside Anki Desktop on your machine.

- Requires Anki 25.07 or newer with the [AnkiMCP](https://ankimcp.ai) add-on installed (AnkiWeb code `124672614`).
- Anki must be running: the add-on serves MCP only while Anki is open.
- Server URL: `http://127.0.0.1:3141/`
- Auth: none. The add-on only listens on your machine, so there is nothing to sign in to.

### Remote: anki-sync-mcp

A headless server you host, such as in Docker. It syncs with AnkiWeb or your own sync server, so Anki doesn't need to be open.

- Requires a running [anki-sync-mcp](https://github.com/ledhed2222/anki-sync-mcp) server in built-in OAuth mode (`MCP_AUTH_MODE=builtin`), reachable over HTTPS. See its README for setup.
- Add `http://localhost:33418/callback` to the server's `MCP_OAUTH_REDIRECT_URIS`. The server only accepts redirect URIs it lists exactly, so the plugin pins Claude Code's OAuth callback to port 33418.
- Server URL: `https://<your-host>/mcp`
- Auth: OAuth. After enabling the plugin, run `/mcp`, choose the `anki` server and sign in with the server's owner password in your browser. Claude Code keeps the token and refreshes it.

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

When the plugin is enabled, Claude Code asks for the server URL. Enter the one for the server you chose above.
