# anki-notes

When Claude teaches you something, this plugin turns it into Anki flashcards: one fact per card, in the right deck, in an order where every card only builds on cards that came before it.

## What it does

- **Makes cards while you learn.** Ask for them ("make a card for that"), or let a deck opt in to getting cards automatically whenever Claude explains something in its subject.
- **Keeps subjects apart.** Each top-level deck is one subject (AI Engineering, Spanish, ...) with a short **charter** that says what belongs in it.
- **Teaches in order.** A deck is split into numbered stages (`01 Basics`, `02 ...`), and a card is only placed after the cards it depends on.
- **Works away from your computer.** In the Claude apps, or whenever Anki isn't open, cards are queued in a Claude Docs doc. The next time you start Claude Code with Anki open, it adds them.

## How it works

```
Claude Code, Anki open            ──▶  card added to Anki, synced to AnkiWeb
claude.ai / mobile / Anki closed  ──▶  card queued in the "Anki inbox" doc
                                          │
next Claude Code session, Anki open  ◀────┘  queued cards added to Anki
```

Only Claude Code writes to Anki, because it reaches the AnkiMCP add-on on your own computer. Anywhere else, the skill drafts the card the same way and queues it instead. Queued cards still get checked against the deck (for duplicates and missing background cards) when they're added.

## Setup

You need:

- [Anki](https://apps.ankiweb.net) 25.07 or newer, with the [AnkiMCP](https://ankimcp.ai) add-on (Tools → Add-ons → Get Add-ons, code `124672614`).

In Claude Code:

```
/plugin marketplace add ledhed2222/claude-plugins
/plugin install anki-notes@ledhed2222
```

That also installs [ankimcp](../ankimcp), which connects Claude Code to the AnkiMCP add-on.

In claude.ai (web, desktop chat, mobile), add the same marketplace under **Customize → Plugins** and install `anki-notes`. There the skill can only queue cards; it can't reach Anki.

The queue is a Claude Docs doc titled **Anki inbox**, one JSON block per card. The skill creates it the first time it needs it, and you can open it from your artifacts to see what's waiting.

## Charters

A deck's charter is its description in Anki (click the deck, then the description below the deck name). It has five short sections:

| section | says |
|---|---|
| Scope | what the deck teaches, a few example topics, and what you already know |
| Out of scope | what looks related but doesn't get a card, and where it goes instead |
| Adding | **Automatic** (add cards without asking) or **Ask** (offer them first) |
| Stages | the numbered subdecks, in order, each with a line on what it covers |
| Conventions | rules for this subject only, like both card directions for a language, and the tag prefix |

**Setting up a deck:** say "set up an Anki deck for Spanish". Claude asks a few questions (what you want to be able to do, what you already know, where the material comes from), checks the new deck doesn't overlap your others, drafts a charter from [`charter-template.md`](skills/anki-notes/charter-template.md), and shows you how it would sort three example topics. Once you approve it, Claude creates the deck and its stages. If Claude teaches something that fits no deck, it suggests a new one rather than guessing.

**Changing a charter:** say what isn't working ("stop carding slang in Spanish"). Claude makes the smallest change that fixes it, tells you what it means for cards already in the deck, and shows you the old and new text before saving. It may also suggest a change when the same kind of card keeps getting rejected or failed.

Away from Anki, an approved charter or a requested change is queued in the Anki inbox and saved the next time Claude Code starts with Anki open. [`charters.md`](skills/anki-notes/charters.md) has the full guide Claude follows.

## Using it

- **Ask for cards:** "make a card for that", "add this to anki".
- **Automatic decks:** cards are added as you go, and Claude reports them in one line.
- **Ask decks:** Claude ends with a one-line offer ("2 possible cards for Spanish: … — add them?") and adds them only if you say yes.
- **Away from Anki:** Claude says "Queued 2 cards in the Anki inbox." You don't need to do anything; they're added the next time Claude Code starts with Anki open.

Claude never deletes cards. Cards that should go are tagged `to-delete`; search `tag:to-delete` in Anki's browser to review and delete them.

## Rebuilding a whole stage

For a big cleanup, Claude writes the stage as a plan file (every card's current text and what will change) for you to review, then applies it with `skills/anki-notes/scripts/apply_stage.py`. This only works in Claude Code with Anki open.

## Troubleshooting

| what you see | why |
|---|---|
| Cards get queued even though you're in Claude Code | Anki is closed, or the AnkiMCP add-on isn't running. Open Anki. |
| The inbox isn't emptied when Claude Code starts | The check only runs when a session starts with Anki already open. Open Anki, then start a new session. |
| Claude says it couldn't save cards anywhere | Neither Anki nor the Anki inbox doc was reachable. The drafts are in the chat; copy them or ask again later. |
| Stages come up out of order in Anki | In the deck's options, set **Display Order → New card gather order** to **Deck**. |
