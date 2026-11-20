# Deck charters

A charter is a subject deck's description in Anki. Claude reads it every time it decides whether something earns a card in that subject, where the card goes and how it's written. Every line must help with one of those decisions; a line that can't be checked against a single draft card gets cut.

## What a good charter does

- **Settles scope with examples.** "Spanish for travel and conversation" doesn't say whether the subjunctive is in. Name three to five topics that are in, and in Out of scope the near neighbors that are not, each with where it goes instead (another deck, or nowhere because it's looked up).
- **Says what the user already knows.** Cards may only use concepts the deck has taught, so without an `Assumes:` line Claude either writes cards for basics the user has or uses terms the user lacks. List what is assumed.
- **Orders stages by prerequisites.** `01` holds what everything else needs, and each stage builds only on the ones before it. Give every stage one line saying what it covers, so a card can be placed by reading it. Start with three to six; add stages as the subject grows rather than planning far ahead.
- **Adds only what this subject needs.** Conventions are rules that change how cards are written here. Don't restate `SKILL.md`. When a convention overrides one of its rules, start the line with `Overrides:`, since charter rules win.
- **Stays short.** Under about 250 words, so it fits on the deck screen and is read in full every time.

## What Conventions should settle

Go through these for the subject and write down only the answers that differ from `SKILL.md`'s defaults:

- **Selection.** What makes an item worth a card here: for vocabulary, how common it is or whether the user met it in real use; for a technical field, whether it changes how the user works.
- **Note types and direction.** The default asks description→name. In a language, recognizing a word and producing it are separate skills, so a language deck may want both directions (`Basic (and reversed card)`) or cloze sentences for production.
- **Context and personal hooks.** The topic label on the front, or a different cue. Example sentences from the user's own life and work stick better than textbook ones. Images or audio where they carry the answer (pronunciation, a diagram, a map).
- **What goes stale.** Fast-moving fields (models, libraries, prices, law) need a date or version in the question; stable ones (grammar, math) don't. Say which this is.
- **Tags.** A prefix no other deck uses (`aie`, `es`) and the areas under it (`es::grammar`, `es::vocab`), so a topic can be found across stages.
- **Sources.** Where the material comes from: sessions with Claude, a textbook (its chapters can shape the stages), the user's reading.

## Creating a charter

1. **Ask first**, in one message, only what the conversation hasn't already told you: what the user wants to be able to do with the subject (sets Scope), what they already know (sets `Assumes:` and stage `01`), where the material will come from, and Automatic or Ask. Suggest Ask for a new deck until its first few batches look right.
2. **Read the other charters** (`list_decks`, then `get_deck_description` on each top-level deck). Scope must not overlap another deck's: if it does, agree with the user which deck owns the overlap and say so in both decks' Out of scope. The tag prefix must be unused.
3. **Draft** from `charter-template.md`, against the rules above.
4. **Test it before showing it.** Pick three things likely to come up: one clearly in, one borderline, one adjacent but out. Decide each from the charter's text alone; if the text doesn't settle the borderline one, tighten Scope or Out of scope. Then draft one card under the Conventions and check that it still passes every rule in `SKILL.md`.
5. **Show** the draft with the three test cases and how it decided them. Revise until the user says yes.
6. **Save**: `create_deck` for the subject and for each stage (`<Subject>::01 <name>`), then `update_deck_description` on the top-level deck with the full text and `is_markdown: true`, then sync as in `SKILL.md`. Report in one line.

## Changing a charter

Change one when the user asks. Propose a change yourself only when the evidence shows the charter, not the cards, is the cause: the same kind of card rejected or rewritten more than once, or problem cards that share a cause.

1. **Read** the current text (`get_deck_description`) and the evidence: the user's complaint, the deck's problem cards (`tag:leech or tag:marked`), and the subdecks that exist (`list_decks`) against the stages listed.
2. **Name the cause** in one sentence ("Scope doesn't say whether regional slang is in, so it's been carded inconsistently"). A topic that keeps getting carded and rejected belongs in Out of scope; a rule that keeps getting broken belongs in Conventions.
3. **Make the smallest change** that fixes it, and keep every other line word for word: the user may have edited the description by hand.
4. **List what it does to existing cards**: how many cards fall out of scope (offer to tag them `to-delete`), which stages are renamed, split or reordered (a stage rebuild, as in `SKILL.md`), and which cards break a new convention (offer a rebuild; never rewrite them silently).
5. **Show** the old and new text of each changed section, with those consequences, and update only on a yes. `update_deck_description` replaces the whole description, so send the full text, then sync.

## Away from Anki

Without the Anki tools, charters can't be read or saved. Draft a new one the same way, skipping the steps that need Anki (other charters, existing cards), and once the user approves it, queue it in the Anki inbox as one json block:

```json
{"charter": {"deck": "Spanish", "stages": ["01 Sounds and spelling", "02 Present tense"], "description": "<full charter text>"}}
```

A change to an existing charter needs its current text, so queue the request instead, in the user's words:

```json
{"charter_change": {"deck": "Spanish", "request": "stop carding regional slang"}}
```

When the inbox is emptied, these go before any card. For a queued charter, run the skipped steps; if they change nothing, save it, since the user already approved it, and otherwise show the change first. A queued change goes through "Changing a charter" from the top.
