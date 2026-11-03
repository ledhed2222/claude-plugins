# rememberthemilk-claude-plugin

A public, unofficial Claude Code plugin whose only job is to declare Remember The Milk's hosted MCP server (`https://www.rememberthemilk.com/mcp`, HTTP transport), so users can enable it from `settings.json` instead of running `claude mcp add` on every machine. The server, its tools and its sign-in flow belong to Remember The Milk; this repo ships config, not code.

## Layout

The repo is both the plugin and its own marketplace:

- `.claude-plugin/plugin.json` -- plugin manifest.
- `.claude-plugin/marketplace.json` -- lists the one plugin with `"source": "./"`, so `/plugin marketplace add ledhed2222/rememberthemilk-claude-plugin` works straight from GitHub.
- `.mcp.json` -- the server declaration. The URL comes from Remember The Milk's own Claude Code instructions: https://www.rememberthemilk.com/services/mcp/connect/#connect-claude-code

Plugin and marketplace are both named `rememberthemilk`, so the install id is `rememberthemilk@rememberthemilk`. Renaming either breaks every user's `enabledPlugins` entry.

## Checks

- `claude plugin validate .` before every commit. The only expected warning is the missing icon.
- Test from disk without installing: `claude --plugin-dir .`, then `/mcp` to sign in.
- Bump `version` in `plugin.json` on any change that should reach existing installs.

## Constraints

- Stay clearly unofficial: no Remember The Milk logo, icon or branding that implies affiliation. An icon, if added, must be original art.
- `privacyPolicyUrl` points at Remember The Milk's policy (https://www.rememberthemilk.com/help/privacy.rtm) because their server handles the data; the plugin itself collects nothing. Keep it that way: no hooks or telemetry.
- The MCP server requires a Remember The Milk Pro account; the README says so and should keep saying so.
