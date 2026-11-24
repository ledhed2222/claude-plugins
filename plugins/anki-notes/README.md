# anki-notes

When Claude teaches you something, this plugin turns it into Anki flashcards: one fact per card, in the right deck, in an order where every card only builds on cards that came before it.

## What it does

- **Makes cards while you learn.** Ask for them ("make a card for that"), or let a deck opt in to getting cards automatically whenever Claude explains something in its subject.
- **Keeps subjects apart.** Each top-level deck is one subject (AI Engineering, Spanish, ...) with a short **charter** that says what belongs in it.
- **Teaches in order.** A deck is split into numbered stages (`01 Basics`, `02 ...`), and a card is only placed after the cards it depends on.
- **Works with a local or a hosted Anki server.** Either the AnkiMCP add-on inside Anki Desktop, or your own [anki-sync-mcp](https://github.com/ledhed2222/anki-sync-mcp) server, which syncs with AnkiWeb and works from claude.ai and your phone too.

## How it works

```
Claude Code ──▶ AnkiMCP add-on (local, Anki open) ──▶ Anki ──▶ AnkiWeb
Claude Code ─┐
claude.ai  ──┴▶ anki-sync-mcp (remote, always on) ──▶ AnkiWeb ──▶ your devices
```

The skill tells the two servers apart by their tools and uses the right calls for each. If neither is reachable, it says so, shows the drafted cards in the chat and saves nothing. Once the server is back ("I've restarted Anki"), it checks those drafts against the deck and adds them.

## Setup

You need one of these servers ([ankimcp's README](../ankimcp/README.md) has the details):

- **Local:** [Anki](https://apps.ankiweb.net) 25.07 or newer, with the [AnkiMCP](https://ankimcp.ai) add-on (Tools → Add-ons → Get Add-ons, code `124672614`). Works in Claude Code only, while Anki is open. For deck themes with their own fonts, add `"font/woff2"` to the add-on's `media_allowed_types` (Tools → Add-ons → AnkiMCP → Config, then restart Anki); without it, themed decks show your system font.
- **Remote:** your own [anki-sync-mcp](https://github.com/ledhed2222/anki-sync-mcp) server. Deck themes and note-type changes need `admin` in its `MCP_SCOPES` and its `ANKI_ALLOW_SCHEMA_CHANGES` setting (and `ANKI_ALLOW_FULL_SYNC` for field changes); without them the skill still adds cards and saves charters.

In Claude Code:

```
/plugin marketplace add ledhed2222/claude-plugins
/plugin install anki-notes@ledhed2222
```

That also installs [ankimcp](../ankimcp), which asks for your server's URL: `http://127.0.0.1:3141/` for the add-on, or your anki-sync-mcp endpoint.

In claude.ai (web, desktop chat, mobile), add the same marketplace under **Customize → Plugins** and install `anki-notes`. The ankimcp server doesn't carry over there, so also add your anki-sync-mcp server as a custom connector (its public HTTPS URL). The local add-on can't be reached from claude.ai.

## Charters

A deck's charter is its description in Anki (click the deck, then the description below the deck name). It has five short sections:

| section | says |
|---|---|
| Scope | what the deck teaches, a few example topics, and what you already know |
| Out of scope | what looks related but doesn't get a card, and where it goes instead |
| Adding | **Automatic** (add cards without asking) or **Ask** (offer them first) |
| Stages | the numbered subdecks, in order, each with a line on what it covers |
| Conventions | rules for this subject only, like both card directions for a language, and the tag prefix |

**Setting up a deck:** say "set up an Anki deck for Spanish". Claude asks a short questionnaire: why you're learning it, how you plan to study it, what you already know, and whether you need to understand it or produce it. It checks the new deck doesn't overlap your others and drafts a charter from [`charter-template.md`](skills/anki-notes/charter-template.md). It also considers whether the subject needs a custom note type, reusing one you already have where it fits (for vocabulary, say, a note with the word, its sentence and a gloss that gives both a recognition and a production card). Then it shows you how the charter sorts three example topics and what a sample note looks like, and asks a few follow-up questions, including an optional one: how studying this makes you feel, and how you'd like it to feel. From that it designs two or three looks for the deck (colors and fonts only: a reading serif for literary decks, sans and monospace for technical ones, with alphabets like Cyrillic covered, all checked for legibility in light and night mode) and lets you pick one or none. Once you approve, Claude creates the deck, its stages and any new note type. If Claude teaches something that fits no deck, it suggests a new one rather than guessing.

**Changing a charter:** say what isn't working ("stop carding slang in Spanish"). Claude makes the smallest change that fixes it, tells you what it means for cards already in the deck, and shows you the old and new text before saving. It may also suggest a change when the same kind of card keeps getting rejected or failed.

If Anki can't be reached, Claude shows the approved charter in the chat and saves it once you say the server is back. [`charters.md`](skills/anki-notes/charters.md) and [`note-types.md`](skills/anki-notes/note-types.md) are the full guides Claude follows. Adding, removing or reordering a note type's fields, or moving notes to another type, makes Anki's next sync a full one, so Claude asks you to sync your other devices first.

## Using it

- **Ask for cards:** "make a card for that", "add this to anki".
- **Automatic decks:** cards are added as you go, and Claude reports them in one line.
- **Ask decks:** Claude ends with a one-line offer ("2 possible cards for Spanish: … — add them?") and adds them only if you say yes.
- **Anki unreachable:** Claude says it couldn't reach Anki, that nothing was saved, and shows the drafted cards. Say "I've restarted Anki" (or "try again") and it adds them.

Claude never deletes cards. Cards that should go are tagged `to-delete`; search `tag:to-delete` in Anki's browser to review and delete them.

## Rebuilding a whole stage

For a big cleanup, Claude writes the stage as a plan file (every card's current text and what will change) for you to review, then applies it with `skills/anki-notes/scripts/apply_stage.py`, which plans the calls for whichever server is connected.

The same folder holds the other checks Claude runs instead of applying rules by eye: a card linter, a duplicate finder, a charter linter and section editor, and a note-type leak check. None of them talks to Anki: Claude makes the calls and hands the scripts the replies, so they run anywhere Python does.

## Evals

`evals/` holds a [`claude plugin eval`](https://code.claude.com/docs/en/plugin-evals.md) suite against a mocked local server: one case per mistake the skill must not make, each run with and without the plugin, so your real Anki is never touched. `evals-remote/` holds a smaller one against a mocked anki-sync-mcp, for what differs there. Each folder's `SPEC.md` lists what its cases test and what counts as passing. From the root of this repo:

```
claude plugin eval . --trust-plugin
claude plugin eval . --trust-plugin --eval-dir plugins/anki-notes/evals-remote
```

Add `--model <model>` to compare models, or `--case <name>` to run one case. The `themes` cases need extra tool grants; `evals/SPEC.md` has the command.

## Ideas

Not built yet.

- **Native pronunciation audio.** For language decks, attach a recording of each word or phrase as spoken by a native speaker. The charter decides whether a deck gets audio and which accent (for example `Audio: es-MX for every target-language word`). Anki plays a `[sound:…]` file stored in its media folder, and both servers can store one, so the open questions are which speech service sounds native enough, and what it costs.
- **Validate the LLM graders.** Run each `llm` grader over cards that were already reviewed by hand, and check it agrees on both the good cards and the bad ones before trusting its scores.
- **Pick the model by eval.** Run the suite once per candidate model with `--model`, then pin the cheapest one that clears the bar in a card-writing subagent. claude.ai ignores plugin agents, so the skill still works there on its own.
- **Learn from real use.** Track, per batch of cards (their `src::` tag), how many get suspended, tagged `to-delete` or keep being failed, and feed the patterns back into the rules and charters.

## Troubleshooting

| what you see | why |
|---|---|
| Claude says it couldn't reach Anki | Local: Anki is closed, or the AnkiMCP add-on isn't running. Remote: your server is down or `/mcp` isn't signed in. Fix it, then say "try again": the drafts are in the chat. |
| No Anki tools in claude.ai | Add your anki-sync-mcp server as a custom connector there. The local add-on can't be reached from claude.ai. |
| Claude says it can't change a note type | Remote: the server's schema tools are off. Include `admin` in `MCP_SCOPES` and set `ANKI_ALLOW_SCHEMA_CHANGES=true` (and `ANKI_ALLOW_FULL_SYNC=true` for field changes). |
| Claude gives steps to change a note type in Anki Desktop | Remote: that change forces a full sync, and this app can't show the server's approval prompt. Follow the steps. |
| Stages come up out of order in Anki | In the deck's options, set **Display Order → New card gather order** to **Deck**. |
