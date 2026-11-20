# claude-plugins

ledhed2222's public Claude Code plugin marketplace. Each plugin lives in `plugins/<name>/`.

## Layout

- `.claude-plugin/marketplace.json` -- the marketplace, named `ledhed2222`. Lists each plugin with `"source": "./plugins/<name>"`, so `/plugin marketplace add ledhed2222/claude-plugins` works straight from GitHub.
- `plugins/<name>/` -- a self-contained plugin. Only this folder is copied on install, so each one carries its own `.claude-plugin/plugin.json`, `README.md` and `LICENSE`.

Install ids are `<plugin>@ledhed2222`. Renaming the marketplace or a plugin breaks every user's `enabledPlugins` entry.

To add a plugin: create `plugins/<name>/`, add an entry to `marketplace.json`, and add a row to the root `README.md`.

## Checks

- Before every commit: `claude plugin validate .` (marketplace) and `claude plugin validate plugins/<name>` for each changed plugin. CI runs both.
- Test a plugin from disk without installing: `claude --plugin-dir plugins/<name>`.
- Bump `version` in a plugin's `plugin.json` on any change that should reach existing installs.
- Icons are fixed the first time a plugin is submitted to the plugin directory, so add one before submitting.

## Plugins

### rememberthemilk

Unofficial. Declares Remember The Milk's hosted MCP server (`https://www.rememberthemilk.com/mcp`, HTTP transport) so users can enable it from `settings.json` instead of running `claude mcp add` on every machine. The URL comes from Remember The Milk's own Claude Code instructions: https://www.rememberthemilk.com/services/mcp/connect/#connect-claude-code. The server, its tools and its sign-in flow belong to Remember The Milk; the plugin ships config, not code. After installing, `/mcp` signs in.

- Stay clearly unofficial: no Remember The Milk logo, icon or branding that implies affiliation. An icon, if added, must be original art. The only expected validator warning is the missing icon.
- `privacyPolicyUrl` points at Remember The Milk's policy (https://www.rememberthemilk.com/help/privacy.rtm) because their server handles the data; the plugin itself collects nothing. Keep it that way: no hooks or telemetry.
- The MCP server requires a Remember The Milk Pro account; its README says so and should keep saying so.

### ankimcp

Unofficial. Declares the MCP server that the [AnkiMCP](https://ankimcp.ai) Anki add-on (AnkiWeb code `124672614`) runs locally at `http://127.0.0.1:3141/` (HTTP transport), so users can enable it from `settings.json` instead of running `claude mcp add` on every machine. The URL comes from AnkiMCP's own client setup docs: https://ankimcp.ai/docs/how-to/connect-mcp-clients/. The server and its tools belong to the add-on; the plugin ships config, not code.

- Stay clearly unofficial: no AnkiMCP or Anki logo or branding. An icon, if added, must be original art.
- The server only exists while Anki is open with the add-on installed; the README says so and should keep saying so. No `privacyPolicyUrl`: the server is local and the plugin collects nothing. Keep it that way: no hooks or telemetry.

### anki-notes

The owner's own skill, not a wrapper around someone else's service. It writes to Anki only through `ankimcp`'s tools and queues to Remember The Milk through `rememberthemilk`'s, so it depends on both plugins without declaring any MCP server itself. Its one hook (`hooks/hooks.json`, SessionStart on `startup`) only checks whether the AnkiMCP add-on answers on `127.0.0.1:3141` and, if so, tells the session to empty the `Anki inbox` list. Keep the hook that cheap and silent when Anki is closed: it runs at the start of every Claude Code session.

- The skill's card rules came from the owner reviewing real cards; subject-specific rules belong in each Anki deck's charter (its description), not in `SKILL.md`.
- `scripts/apply_stage.py` talks to the add-on's HTTP server directly, so it only works in Claude Code on the machine running Anki.
