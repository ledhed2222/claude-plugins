# anki-notes

The owner's own skill, not a wrapper around someone else's service: it turns what Claude teaches into staged Anki flashcards. It writes to Anki only through `ankimcp`'s tools, so it lists `ankimcp` in `dependencies` (installed with it) instead of declaring an MCP server of its own.

This file is for working on the plugin in this repo. `claude plugin validate` warns that it isn't loaded for people who install the plugin; that is intended, so leave it here rather than moving it into a skill.

## Layout

- `skills/anki-notes/SKILL.md` -- the skill. Its card rules came from the owner reviewing real cards; keep them general. Rules for one subject belong in that deck's charter (its description in Anki), never here.
- `skills/anki-notes/charter-template.md` -- the skeleton for a new deck's charter.
- `skills/anki-notes/charters.md` -- how to write and change a deck's charter; `note-types.md` -- how to design a note type. The skill reads each only when it needs to.
- `skills/anki-notes/scripts/` -- deterministic checks and writes the skill runs instead of following instructions by hand: `lint_cards.py` (card checks), `find_dupes.py` (close matches in the deck), `add_cards.py` (add, order, sync), `charter.py` (charter lint and one-section edits), `render_note.py` (note-type leak check), `apply_stage.py` (whole-stage plans). All share `ankimcp_client.py`, which talks to the add-on's HTTP server at `127.0.0.1:3141` directly, so those only work in Claude Code on the machine running Anki; `lint_cards.py` and `charter.py lint` without `--deck` need nothing but Python. Standard library only, asyncio for I/O, calls sequential since they all write one collection.
- Script tests: `cd plugins/anki-notes/skills/anki-notes/scripts && python3 -m unittest` (not `-I`, which hides the modules). They use a fake add-on server, never a real Anki. The `test_*` classes named `EvalCaseTests` grade cases from the eval list in PR #6 without an LLM. CI runs them.
- `hooks/hooks.json` -- one SessionStart hook (`startup`): if the add-on answers, it tells the session to empty the `Anki inbox` doc. It runs at the start of every Claude Code session, so keep it that cheap and silent when Anki is closed. It exits early when `EVAL_SKIP_INBOX_HOOK` is set.
- `evals/` -- the eval suite; see below.

## Where cards go

- Claude Code with Anki open: written to Anki, then synced.
- Anywhere else (the claude.ai apps, or Anki closed): queued as json code blocks in a Claude Docs doc titled `Anki inbox`, found by title in the user's artifacts. Don't hardcode its link or ids: they're one person's, and this plugin is public.
- The skill never deletes notes: it tags them `to-delete` for the user.

## Evals

- One case per directory under `evals/`. The first ones each reproduce a mistake the owner flagged in a real card review; the rest test the formulation checks, `charters.md` and `note-types.md`. `evals/SPEC.md` says what each case tests and the pass bar.
- **Run from the repo root**, not from this folder: `claude plugin eval . --trust-plugin`. Each case loads `ankimcp` too (`plugins: ["../..", "../../../ankimcp"]`), and the harness only loads plugins under the directory it was pointed at.
- `evals/mocks/anki/` replaces the Anki server for every case. `_tools.json` is the real server's `tools/list` for the mocked tools; save it again from the running add-on if those tools change. A case overrides one mock with its own `mocks/anki/<tool>.md`.
- Mock replies must look like real ones. A reply that disagrees with the request (say, "1 created" for a batch of 6) makes Claude stop to investigate, and the run fails for reasons that have nothing to do with the skill.
- An `llm` grader with `focus: trace` sees only the first and last 12 messages, so it can miss the tool call it is meant to judge. Pair each such rule with a `regex` grader on `target: mock_calls`, which sees every call.
- Every case sets `EVAL_SKIP_INBOX_HOOK: "1"` in `env`, or the hook reaches a real Anki open on the machine and adds noise to the run.
- Cases where the skill reads `charters.md`, `note-types.md` or another file next to `SKILL.md` must list `Read` in `allowed_tools`, or the read is blocked and Claude works without the guide.
- To simulate Anki being closed, override every shared mock with a connection-refused error (see `inbox-path/mocks/anki/`). Leaving `ankimcp` out of `plugins` doesn't work: the suite's mocks still serve the Anki tools.
- `AskUserQuestion` isn't available in headless runs even when allowed, so grade questionnaires from the reply.
- `model_field_names.md` and `model_templates.md` answer per note type from `mocks/anki/fixtures/`; add a fixture when a case needs another type. The lookup rejects a file name with spaces or accents, so mock note types get plain names (`Reconocimiento`, not `Español Reconocimiento`).
- When a reply must depend on a name with a space (a deck like `AI Engineering`), use a `type: agent` mock with the verbatim reply for each name and the real error for anything else; see `mocks/anki/get_deck_description.md`. A fixed mock answers every name the same, so a check for an unknown deck gets a charter back.
- Grader regexes are JavaScript: no inline `(?i)`. `tool_used` has no flags field, so spell out both cases (`[nN]ame`).
- A full run is 288 sessions, about 25 minutes with `-j 8`, and about $60; run one case with `--case <name>` while iterating, with `--runs 1 --ablation none` for a quick check.

### Adding or changing a case

1. Write `evals/<case>/prompt.md` (with a one-sentence `description`) and its `graders/`.
2. Run it: `claude plugin eval . --trust-plugin --case <case>`.
3. Regenerate the spec, `python3 -I plugins/anki-notes/evals/gen_spec.py`, and commit it with the case. CI fails when `SPEC.md` doesn't match the cases.
