# anki-notes

The owner's own skill, not a wrapper around someone else's service: it turns what Claude teaches into staged Anki flashcards. It writes to Anki only through `ankimcp`'s `anki` MCP server, so it lists `ankimcp` in `dependencies` (installed with it) instead of declaring an MCP server of its own. That server is one of two, chosen by the URL the user gives ankimcp: see "Two servers".

This file is for working on the plugin in this repo. `claude plugin validate` warns that it isn't loaded for people who install the plugin; that is intended, so leave it here rather than moving it into a skill.

## Compatibility

The plugin must install and work on both Claude Code and claude.ai (web, desktop chat and mobile). Every change keeps both working:

- Cards reach Anki wherever the `anki` tools are connected: Claude Code with either server, and claude.ai only with the remote one, added there by the user as a custom connector (a plugin's `${user_config.*}` server and its dependencies don't carry over to claude.ai, and claude.ai can't reach localhost). Without the tools, the skill errors and shows the drafts in chat; there is no queue.
- Shipped scripts run on whatever `python3` the user's machine or the claude.ai sandbox has, with nothing installed: standard library only, and no language or library features newer than those interpreters ship. The root `mise.toml` pins the latest Python and Node for development and CI only, so passing tests there doesn't prove a script runs for users.
- `SKILL.md` and its guides must make sense on both surfaces and with both servers.
- No hooks: they only run in Claude Code, and the plugin has none.

## Layout

- `skills/anki-notes/SKILL.md` -- the skill. Its card rules came from the owner reviewing real cards; keep them general. Rules for one subject belong in that deck's charter (its description in Anki), never here.
- `skills/anki-notes/charter-template.md` -- the skeleton for a new deck's charter.
- `skills/anki-notes/charters.md` -- how to write and change a deck's charter; `note-types.md` -- how to design a note type; `media.md` -- when and how a card gets a diagram, photo or sound. The skill reads each only when it needs to.
- `skills/anki-notes/scripts/` -- deterministic checks and plans the skill runs instead of following instructions by hand: `lint_cards.py` (card checks), `find_dupes.py` (close matches in the deck), `format_mix.py` (share of the deck's most common card format), `add_cards.py` (plan the adds, then order and sync), `charter.py` (charter lint and one-section edits), `render_note.py` (note-type leak check), `apply_stage.py` (whole-stage plans), `build_theme.py` (deck themes). None reaches Anki: Claude makes every call through the connected server and saves each reply to a file, `replies.py` reads either server's replies, and the write scripts print the calls to make, for `--server local|remote`. So they run anywhere Python does. Standard library only (see Compatibility and Async): Team or Enterprise orgs can turn off the claude.ai sandbox's network, so a PyPI dependency would stop the linters there. Third-party libraries are fine in repo tooling that never ships to users.
- This plugin's tasks are in its own `mise.toml` (`mise tasks` in this folder lists them); run them from here, or from the root with `mise -C plugins/anki-notes run <task>`. `eval`, `record` and `diff` run from the repo root whichever folder you're in, so give result paths from the root. The file ships with the plugin and does nothing for users.
- Script tests: `mise run test` (it runs `python3 -m unittest` in `scripts/`; not `-I`, which hides the modules). They read saved replies in `scripts/testdata/`, never a real Anki; see "Two servers" for how they're split. The `EvalCaseTests` classes cover what the eval cases no-giveaway, closed-list, charter-lean, charter-change-minimal and nt-no-leak check, and `test_eval_fixtures.py` runs the scripts on those cases' own fixtures (mock charters), so a fixture change that a script can't read fails here. `claude plugin eval` has no script grader, so the cases themselves keep their LLM judges. CI runs the tests.
- `evals/` -- the eval suite for the local server; `evals-remote/` -- the one for the remote server. See "Evals".

## Two servers

The skill supports two MCP servers, told apart by tool name, and every change must keep both working:

- **local**: the AnkiMCP add-on inside Anki Desktop (AnkiWeb `124672614`), tools like `list_decks` and `add_notes`.
- **remote**: anki-sync-mcp (https://github.com/ledhed2222/anki-sync-mcp), tools like `anki_decks_list` and `anki_notes_create`. It takes ids rather than names, requires exact note-type fields, fails a whole batch on one duplicate, and takes an `idempotency_key` on every write.

`SKILL.md`'s "Anki tools" table maps each operation to both servers' tools. A tool named anywhere in the skill must appear in the right column.

**Any change that touches either server needs unit tests for both.** That covers a tool call, a reply the scripts read, a fixture, the tools table, or a script that plans calls. The split is built into the tests so it can't be skipped:

- **Fixtures come in pairs.** `scripts/testdata/local/<op>.json` and `remote/<op>.json` are the same operation's reply on each server, for the same collection, and `testdata/operations.json` names each one's tool. Remote replies were recorded from a live server; local ones hold the same notes in the add-on's shapes. A new operation gets both files and an entry; a reply only one server has goes under `only`.
- **Tests are contracts.** A test that reads a reply or plans a call is written once, in a `*Contract` mixin that uses `self.server`, and runs as a `Local<Name>` and a `Remote<Name>` class (`both_servers.py` has the pattern). Server-specific extras go on those classes.
- **Calls are checked against the real schemas.** Contracts pass every planned call to `both_servers.check_call`, which checks it against that server's saved `tools/list` (`evals/mocks/anki/_tools.json` for local, `evals-remote/mocks/anki/_tools.json` for remote): the tool exists, required arguments are there, and none is unknown or mistyped. `UNVERIFIED` lists the few add-on tools with no saved schema yet. Save them from a running add-on rather than adding to it.
- **`test_both_servers.py` enforces the rules**: every shared operation has both fixtures, every Contract runs on both servers, no server-pinned test lives outside a Contract, the tools table names real tools in the right columns, and every tool a script calls exists on its server. `test_replies.py` also checks that both servers' fixtures normalize to identical values.

When either server's tools change, save its `tools/list` again (remote: start it from its repo with `ANKI_ALLOW_SCHEMA_CHANGES=true` and `ANKI_ALLOW_FULL_SYNC=true`, so the schema tools are listed), record any reply whose shape changed into `testdata/`, and run the tests.

## Async

This project strives to be very async: every script here, shipped or eval tooling, runs on `asyncio` with standard-library tools only, and any I/O that doesn't depend on other I/O runs at the same time.

- Entry points are `async def main()` run by `asyncio.run`.
- File reads and writes go through `asyncio.to_thread`; subprocesses through `asyncio.create_subprocess_exec`.
- Independent work runs together with `asyncio.gather`, which keeps results in input order: reads of several saved replies (`replies.read`), a plan and its `.applied.json` (`apply_stage.py`), one thread per eval case (`check_cases.py`, `gen_spec.py`), git calls (`record_run.py`).
- The write scripts print Anki calls in the order Claude must make them, one at a time: they all change one collection, and card order and the `.applied.json` record depend on that order.
- Keep pure logic (lint rules, diffing, rendering) synchronous and testable on its own; make only the I/O around it async.

## Where cards go

- Wherever the `anki` tools are connected: written to Anki, then synced.
- Anywhere else, or when the server can't be reached: the skill says so in one line and shows the drafts in chat. When the user says Anki is back, it runs every step on those drafts. Nothing is queued anywhere.
- The skill never deletes notes: it tags them `to-delete` for the user.

## Evals

- One case per directory under `evals/` (local server) or `evals-remote/` (remote server). A tool is visible to a case only if it has a mock, and a case's mocks override its suite's file by file, so each suite's `mocks/anki/` holds only its own server's tools; that is why the servers have separate suites. The first ones each reproduce a mistake the owner flagged in a real card review; the rest test the formulation checks, `charters.md` and `note-types.md`. `evals/SPEC.md` says what each case tests and the pass bar.
- **The harness must start at the repo root**, which `mise run eval` does for you (`claude plugin eval . --trust-plugin -j 8`; extra args pass through, e.g. `mise run eval --case <name>`). `mise run eval-remote` runs the remote suite. Results land in `<repo root>/evals/results/<time>/`, because the harness writes under its working directory, not the plugin's. Each case loads `ankimcp` too (`plugins: ["../..", "../../../ankimcp"]`), and the harness only loads plugins under the directory it was pointed at.
- `evals/mocks/anki/` and `evals-remote/mocks/anki/` replace the Anki server for every case. Each `_tools.json` is its real server's `tools/list` for the mocked tools; save it again when those tools change. A case overrides one mock with its own `mocks/anki/<tool>.md`.
- `evals/check_cases.py` checks the rules below that a script can (CI runs it): each case's description, `plugins`, that its allowed tools are all one server's, and `Read` (for cases tagged charter, note-type, questionnaire or media); that every allowed ankimcp tool has a mock, so no call reaches a real Anki; the pairing of trace judges with call graders; and that every JSON mock reply has the keys `_shapes.json` lists for its tool. Each suite has its own `_shapes.json`, with its source in the file; update it when that server's replies change. Run it on the remote suite with `python3 -I evals/check_cases.py evals-remote` (CI does both).
- Mock replies must look like real ones. A reply that disagrees with the request (say, "1 created" for a batch of 6) makes Claude stop to investigate, and the run fails for reasons that have nothing to do with the skill.
- An `llm` grader with `focus: trace` sees only the first and last 12 messages, so it can miss the tool call it is meant to judge. Pair each such rule with a `regex` grader on `target: mock_calls`, which sees every call.
- Cases where the skill reads `charters.md`, `note-types.md`, `media.md` or another file next to `SKILL.md` must list `Read` in `allowed_tools`, or the read is blocked and Claude works without the guide.
- To simulate the server being unreachable, override every shared mock with a connection error (see `evals-remote/remote-unreachable/mocks/anki/`). Leaving `ankimcp` out of `plugins` doesn't work: the suite's mocks still serve the Anki tools.
- `AskUserQuestion` isn't available in headless runs even when allowed, so grade questionnaires from the reply.
- `model_field_names.md` and `model_templates.md` answer per note type from `mocks/anki/fixtures/`; add a fixture when a case needs another type. The lookup rejects a file name with spaces or accents, so mock note types get plain names (`Reconocimiento`, not `Español Reconocimiento`).
- When a reply must depend on a name with a space (a deck like `AI Engineering`), use a `type: agent` mock with the verbatim reply for each name and the real error for anything else; see `mocks/anki/get_deck_description.md`. A fixed mock answers every name the same, so a check for an unknown deck gets a charter back.
- Grader regexes are JavaScript: no inline `(?i)`. `tool_used` has no flags field, so spell out both cases (`[nN]ame`).
- **Record every run you mean to keep**: `mise run record evals/results/<time>/aggregate-result.json --note "<why it ran>"`, then commit `evals/history.jsonl` with the change it measured. It prints the overall score and every case that moved since that case's last recorded score; `mise run diff <result.json>` shows the same without recording. The root `evals/results/` is gitignored, so the history file is the only record that lasts. Skip throwaway debugging runs. A case runs 3 times, so a move of one run (0.33 or less) is often noise: re-run the case before acting on it.
- A full run is 288 sessions without the `themes` cases, about 25 minutes with `-j 8`, and about $60 (the `themes` cases add 108 sessions and roughly $30); run one case with `--case <name>` while iterating, with `--runs 1 --ablation none` for a quick check.
- Most `themes` cases run `build_theme.py`, so they need `--allow-tools Write Bash` (`mise run eval --tag themes --allow-tools Write Bash`). The eval sandbox usually can't run npm, so font cases grade the family names Claude chooses (the strings in its `fetch_font.py --info` calls and theme.json), never whether a font downloaded; a theme falls back to the system font there.

### Adding or changing a case

1. Write `evals/<case>/prompt.md` (or `evals-remote/<case>/` for the remote server) (with a one-sentence `description`) and its `graders/`.
2. Run it: `mise run eval --case <case>`.
3. Regenerate the spec, `mise run spec`, and commit it with the case. CI fails when `SPEC.md` doesn't match the cases.
