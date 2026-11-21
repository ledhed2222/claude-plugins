# anki-notes

The owner's own skill, not a wrapper around someone else's service: it turns what Claude teaches into staged Anki flashcards. It writes to Anki only through `ankimcp`'s tools, so it lists `ankimcp` in `dependencies` (installed with it) instead of declaring an MCP server of its own.

This file is for working on the plugin in this repo. `claude plugin validate` warns that it isn't loaded for people who install the plugin; that is intended, so leave it here rather than moving it into a skill.

## Layout

- `skills/anki-notes/SKILL.md` -- the skill. Its card rules came from the owner reviewing real cards; keep them general. Rules for one subject belong in that deck's charter (its description in Anki), never here.
- `skills/anki-notes/charter-template.md` -- the skeleton for a new deck's charter.
- `skills/anki-notes/charters.md` -- how to write and change a deck's charter; `note-types.md` -- how to design a note type. The skill reads each only when it needs to.
- `skills/anki-notes/scripts/apply_stage.py` -- applies a whole-stage plan. It talks to the add-on's HTTP server at `127.0.0.1:3141` directly, so it only works in Claude Code on the machine running Anki.
- `hooks/hooks.json` -- one SessionStart hook (`startup`): if the add-on answers, it tells the session to empty the `Anki inbox` doc. It runs at the start of every Claude Code session, so keep it that cheap and silent when Anki is closed. It exits early when `EVAL_SKIP_INBOX_HOOK` is set.
- `evals/` -- the eval suite; see below.

## Where cards go

- Claude Code with Anki open: written to Anki, then synced.
- Anywhere else (the claude.ai apps, or Anki closed): queued as json code blocks in a Claude Docs doc titled `Anki inbox`, found by title in the user's artifacts. Don't hardcode its link or ids: they're one person's, and this plugin is public.
- The skill never deletes notes: it tags them `to-delete` for the user.

## Evals

- One case per directory under `evals/`, each reproducing a mistake the owner flagged in a real card review. `evals/SPEC.md` says what each case tests and the pass bar.
- **Run from the repo root**, not from this folder: `claude plugin eval . --trust-plugin`. Each case loads `ankimcp` too (`plugins: ["../..", "../../../ankimcp"]`), and the harness only loads plugins under the directory it was pointed at.
- `evals/mocks/anki/` replaces the Anki server for every case. `_tools.json` is the real server's `tools/list` for the mocked tools; save it again from the running add-on if those tools change. A case overrides one mock with its own `mocks/anki/<tool>.md`.
- Mock replies must look like real ones. A reply that disagrees with the request (say, "1 created" for a batch of 6) makes Claude stop to investigate, and the run fails for reasons that have nothing to do with the skill.
- An `llm` grader with `focus: trace` sees only the first and last 12 messages, so it can miss the tool call it is meant to judge. Pair each such rule with a `regex` grader on `target: mock_calls`, which sees every call.
- Every case sets `EVAL_SKIP_INBOX_HOOK: "1"` in `env`, or the hook reaches a real Anki open on the machine and adds noise to the run.
- A full run is 42 sessions and about $6; run one case with `--case <name>` while iterating.

### Adding or changing a case

1. Write `evals/<case>/prompt.md` (with a one-sentence `description`) and its `graders/`.
2. Run it: `claude plugin eval . --trust-plugin --case <case>`.
3. Regenerate the spec, `python3 -I plugins/anki-notes/evals/gen_spec.py`, and commit it with the case. CI fails when `SPEC.md` doesn't match the cases.
