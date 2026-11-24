# claude-plugins

ledhed2222's public Claude Code plugin marketplace. Each plugin lives in `plugins/<name>/`.

## Layout

- `.claude-plugin/marketplace.json` -- the marketplace, named `ledhed2222`. Lists each plugin with `"source": "./plugins/<name>"`, so `/plugin marketplace add ledhed2222/claude-plugins` works straight from GitHub.
- `plugins/<name>/` -- a self-contained plugin. Only this folder is copied on install, so each one carries its own `.claude-plugin/plugin.json`, `README.md` and `LICENSE`.

Install ids are `<plugin>@ledhed2222`. Renaming the marketplace or a plugin breaks every user's `enabledPlugins` entry.

To add a plugin: create `plugins/<name>/`, add an entry to `marketplace.json`, and add a row to the root `README.md`.

## Checks

- The root `mise.toml` sets the tool versions (latest Python, LTS Node) and the repo-wide tasks: `validate` and `ci`. A plugin with its own checks keeps its tasks in `plugins/<name>/mise.toml` with a `ci` task, which the root `ci` runs. Before every commit: `mise run ci` from the root. CI runs the same task.
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

Unofficial. Declares one HTTP MCP server, `anki`, whose URL is a `userConfig` value (`server_url`) asked for on enable, so users can enable it from `settings.json` instead of running `claude mcp add` on every machine. Two servers are supported and the README documents both: the local [AnkiMCP](https://ankimcp.ai) add-on (AnkiWeb code `124672614`, `http://127.0.0.1:3141/`, no auth, only while Anki is open) and the owner's self-hosted [anki-sync-mcp](https://github.com/ledhed2222/anki-sync-mcp) fork (built-in OAuth, signed into through `/mcp`). Their tools differ. The plugin ships config, not code.

- Stay clearly unofficial: no Anki or AnkiMCP logo or branding. An icon, if added, must be original art.
- No `privacyPolicyUrl`: the server runs locally or is hosted by the user, and the plugin collects nothing, so the validator's privacy warning is expected. Keep it that way: no hooks or telemetry.
- `.mcp.json` pins the OAuth callback to port 33418 because the server matches redirect URIs exactly. Changing the port breaks every server that allow-lists `http://localhost:33418/callback`.
- anki-notes supports both servers (see its `CLAUDE.md`, "Two servers"). A change to either server's tools needs unit tests for both there.

### anki-notes

The owner's own skill for turning what Claude teaches into Anki flashcards. It depends on `ankimcp` and has an eval suite; its conventions are in [`plugins/anki-notes/CLAUDE.md`](plugins/anki-notes/CLAUDE.md).
