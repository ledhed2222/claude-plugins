# anki-notes

The owner's own skill, not a wrapper around someone else's service: it turns what Claude teaches into staged Anki flashcards. It writes to Anki only through `ankimcp`'s tools, so it lists `ankimcp` in `dependencies` (installed with it) instead of declaring an MCP server of its own.

This file is for working on the plugin in this repo. `claude plugin validate` warns that it isn't loaded for people who install the plugin; that is intended, so leave it here rather than moving it into a skill.

## Compatibility

The plugin must install and work on both Claude Code and claude.ai (web, desktop chat and mobile). Every change keeps both working:

- Claude Code with Anki open is the only place cards reach Anki. Everywhere else the skill queues them in the `Anki inbox` doc, and that path must keep working without Anki, hooks or a local server.
- Shipped scripts run on whatever `python3` the user's machine or the claude.ai sandbox has, with nothing installed: standard library only, and no language or library features newer than those interpreters ship. The root `mise.toml` pins the latest Python and Node for development and CI only, so passing tests there doesn't prove a script runs for users.
- `SKILL.md` and its guides must make sense on both surfaces. Say which steps need Claude Code with Anki open, and give the claude.ai path for each.
- Hooks run only in Claude Code, so nothing a user needs may depend on one.

## Layout

- `skills/anki-notes/SKILL.md` -- the skill. Its card rules came from the owner reviewing real cards; keep them general. Rules for one subject belong in that deck's charter (its description in Anki), never here.
- `skills/anki-notes/charter-template.md` -- the skeleton for a new deck's charter.
- `skills/anki-notes/charters.md` -- how to write and change a deck's charter; `note-types.md` -- how to design a note type. The skill reads each only when it needs to.
- `skills/anki-notes/scripts/` -- deterministic checks and writes the skill runs instead of following instructions by hand: `lint_cards.py` (card checks), `find_dupes.py` (close matches in the deck), `format_mix.py` (share of the deck's most common card format), `add_cards.py` (add, order, sync), `charter.py` (charter lint and one-section edits), `render_note.py` (note-type leak check), `apply_stage.py` (whole-stage plans). All share `ankimcp_client.py`, which talks to the add-on's HTTP server at `127.0.0.1:3141` directly, so those only work in Claude Code on the machine running Anki; `lint_cards.py` and `charter.py lint` without `--deck` need nothing but Python. Standard library only (see Compatibility and Async): Team or Enterprise orgs can turn off the claude.ai sandbox's network, so a PyPI dependency would stop the linters there. Third-party libraries are fine in repo tooling that never ships to users.
- This plugin's tasks are in its own `mise.toml` (`mise tasks` in this folder lists them); run them from here, or from the root with `mise -C plugins/anki-notes run <task>`. `eval`, `record` and `diff` run from the repo root whichever folder you're in, so give result paths from the root. The file ships with the plugin and does nothing for users.
- Script tests: `mise run test` (it runs `python3 -m unittest` in `scripts/`; not `-I`, which hides the modules). They use a fake add-on server, never a real Anki. The `EvalCaseTests` classes cover what the eval cases no-giveaway, closed-list, inbox-path, charter-lean, charter-change-minimal and nt-no-leak check, and `test_eval_fixtures.py` runs the scripts on those cases' own fixtures (inbox blocks, mock charters), so a fixture change that a script can't read fails here. `claude plugin eval` has no script grader, so the cases themselves keep their LLM judges, and they don't allow Bash: the scripts would reach a real Anki on port 3141, past the mocks. CI runs the tests.
- `hooks/hooks.json` -- one SessionStart hook (`startup`): if the add-on answers, it tells the session to empty the `Anki inbox` doc. It runs at the start of every Claude Code session, so keep it that cheap and silent when Anki is closed. It exits early when `EVAL_SKIP_INBOX_HOOK` is set.
- `evals/` -- the eval suite; see below.

## Async

This project strives to be very async: every script here, shipped or eval tooling, runs on `asyncio` with standard-library tools only, and any I/O that doesn't depend on other I/O runs at the same time.

- Entry points are `async def main()` run by `asyncio.run`.
- File reads and writes go through `asyncio.to_thread`; subprocesses through `asyncio.create_subprocess_exec`; HTTP through `ankimcp_client.Client`.
- Independent work runs together with `asyncio.gather`, which keeps results in input order: reads of several decks (`charter.py`, `find_dupes.py`), a file read alongside an Anki call (`apply_stage.py`), one thread per eval case (`check_cases.py`, `gen_spec.py`), git calls (`record_run.py`).
- Anki writes stay one at a time, in order: they all change one collection, and card order and the `.applied.json` record depend on that order. Only calls that read can be gathered; the add-on answers concurrent reads correctly.
- Steps that depend on each other's results stay sequential: paging with `hasMore`, sync polling, and anything that needs a note id first.
- Keep pure logic (lint rules, diffing, rendering) synchronous and testable on its own; make only the I/O around it async.

## Where cards go

- Claude Code with Anki open: written to Anki, then synced.
- Anywhere else (the claude.ai apps, or Anki closed): queued as json code blocks in a Claude Docs doc titled `Anki inbox`, found by title in the user's artifacts. Don't hardcode its link or ids: they're one person's, and this plugin is public.
- The skill never deletes notes: it tags them `to-delete` for the user.

## Evals

- One case per directory under `evals/`. The first ones each reproduce a mistake the owner flagged in a real card review; the rest test the formulation checks, `charters.md` and `note-types.md`. `evals/SPEC.md` says what each case tests and the pass bar.
- **The harness must start at the repo root**, which `mise run eval` does for you (`claude plugin eval . --trust-plugin -j 8`; extra args pass through, e.g. `mise run eval --case <name>`). Results land in `<repo root>/evals/results/<time>/`, because the harness writes under its working directory, not the plugin's. Each case loads `ankimcp` too (`plugins: ["../..", "../../../ankimcp"]`), and the harness only loads plugins under the directory it was pointed at.
- `evals/mocks/anki/` replaces the Anki server for every case. `_tools.json` is the real server's `tools/list` for the mocked tools; save it again from the running add-on if those tools change. A case overrides one mock with its own `mocks/anki/<tool>.md`.
- `evals/check_cases.py` checks the rules below that a script can (CI runs it): each case's description, `plugins`, `EVAL_SKIP_INBOX_HOOK` and `Read` (for cases tagged charter, note-type or questionnaire); that every allowed ankimcp tool has a mock, so no call reaches a real Anki; the pairing of trace judges with call graders; and that every JSON mock reply has the keys `_shapes.json` lists for its tool. `_shapes.json` comes from the add-on's source (its version is in the file); update it when the add-on's replies change.
- Mock replies must look like real ones. A reply that disagrees with the request (say, "1 created" for a batch of 6) makes Claude stop to investigate, and the run fails for reasons that have nothing to do with the skill.
- An `llm` grader with `focus: trace` sees only the first and last 12 messages, so it can miss the tool call it is meant to judge. Pair each such rule with a `regex` grader on `target: mock_calls`, which sees every call.
- Every case sets `EVAL_SKIP_INBOX_HOOK: "1"` in `env`, or the hook reaches a real Anki open on the machine and adds noise to the run.
- Cases where the skill reads `charters.md`, `note-types.md` or another file next to `SKILL.md` must list `Read` in `allowed_tools`, or the read is blocked and Claude works without the guide.
- To simulate Anki being closed, override every shared mock with a connection-refused error (see `inbox-path/mocks/anki/`). Leaving `ankimcp` out of `plugins` doesn't work: the suite's mocks still serve the Anki tools.
- `AskUserQuestion` isn't available in headless runs even when allowed, so grade questionnaires from the reply.
- `model_field_names.md` and `model_templates.md` answer per note type from `mocks/anki/fixtures/`; add a fixture when a case needs another type. The lookup rejects a file name with spaces or accents, so mock note types get plain names (`Reconocimiento`, not `Español Reconocimiento`).
- When a reply must depend on a name with a space (a deck like `AI Engineering`), use a `type: agent` mock with the verbatim reply for each name and the real error for anything else; see `mocks/anki/get_deck_description.md`. A fixed mock answers every name the same, so a check for an unknown deck gets a charter back.
- Grader regexes are JavaScript: no inline `(?i)`. `tool_used` has no flags field, so spell out both cases (`[nN]ame`).
- **Record every run you mean to keep**: `mise run record evals/results/<time>/aggregate-result.json --note "<why it ran>"`, then commit `evals/history.jsonl` with the change it measured. It prints the overall score and every case that moved since that case's last recorded score; `mise run diff <result.json>` shows the same without recording. The root `evals/results/` is gitignored, so the history file is the only record that lasts. Skip throwaway debugging runs. A case runs 3 times, so a move of one run (0.33 or less) is often noise: re-run the case before acting on it.
- A full run is 288 sessions without the `themes` cases, about 25 minutes with `-j 8`, and about $60 (the `themes` cases add 108 sessions and roughly $30); run one case with `--case <name>` while iterating, with `--runs 1 --ablation none` for a quick check.
- Most `themes` cases run `build_theme.py`, so they need `--allow-tools Write Bash` (`mise run eval --tag themes --allow-tools Write Bash`). The eval sandbox usually can't run npm, so font cases grade the family names Claude chooses (the strings in its `fetch_font.py --info` calls and theme.json), never whether a font downloaded; a theme falls back to the system font there.

### Adding or changing a case

1. Write `evals/<case>/prompt.md` (with a one-sentence `description`) and its `graders/`.
2. Run it: `mise run eval --case <case>`.
3. Regenerate the spec, `mise run spec`, and commit it with the case. CI fails when `SPEC.md` doesn't match the cases.
