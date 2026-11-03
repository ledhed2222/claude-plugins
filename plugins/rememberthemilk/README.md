# rememberthemilk

A Claude Code plugin that connects to [Remember The Milk](https://www.rememberthemilk.com)'s hosted MCP server, so the server can be enabled from `settings.json` instead of a per-machine `claude mcp add`.

Unofficial; not affiliated with Remember The Milk. The MCP server itself requires a Remember The Milk Pro account.

## Install

```
/plugin marketplace add ledhed2222/claude-plugins
/plugin install rememberthemilk@ledhed2222
```

Then run `/mcp`, pick `rememberthemilk`, and sign in.

Or declare it in `settings.json`:

```json
{
  "extraKnownMarketplaces": {
    "ledhed2222": {
      "source": { "source": "github", "repo": "ledhed2222/claude-plugins" }
    }
  },
  "enabledPlugins": {
    "rememberthemilk@ledhed2222": true
  }
}
```
