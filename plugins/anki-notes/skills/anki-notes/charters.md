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

- **Selection.** What makes an item worth a card here: for vocabulary, how common it is or whether the user met it in real use; for a technical field, whether it changes how the user works; for an exam, whether the syllabus covers it.
- **Note types and direction.** The default asks description→name with Basic and Cloze. In a language, recognizing a word and producing it are separate skills, so a language deck may want both directions or a custom note type (see "Choosing note types").
- **Context and personal hooks.** The topic label on the front, or a different cue. Example sentences from the user's own life, work or reading stick better than textbook ones. Images or audio where they carry the answer (pronunciation, a diagram, a map).
- **Variety.** Which card shapes suit the subject, and whether the deck should stay uniform on purpose (vocabulary in fixed recognition and production types): a `Variety:` line, only when it differs from the skill's default.
- **What goes stale.** Fast-moving fields (models, libraries, prices, law) need a date or version in the question; stable ones (grammar, math) don't. Say which this is.
- **Tags.** A prefix no other deck uses (`aie`, `es`) and the areas under it (`es::grammar`, `es::vocab`), so a topic can be found across stages.
- **Sources.** Where the material comes from: sessions with Claude, a textbook (its chapters can shape the stages), the user's reading and lookups.

## Creating a charter

1. **Ask with a questionnaire.** Use the app's question tool when there is one (`AskUserQuestion` in Claude Code), otherwise one message with a short numbered list. Give each question three or four concrete options drawn from the subject and from what the user has said, and keep a free answer open. Skip any question the conversation has already answered. The first round:
   - **Why do you need to learn this?** For work you do now, for an exam (and when), to live or travel with it, out of curiosity. This sets Scope and Selection.
   - **How do you plan to study it?** Where new material comes from (sessions with Claude, a course or book, your own reading with lookups) and where you review (phone, desktop, both). This sets Sources and Adding, and which devices a note type must work on.
   - **What do you already know?** This sets `Assumes:` and stage `01`.
   - **Do you need to understand it or produce it?** Recognize it when reading or hearing, produce it when speaking, writing or building, or both. This sets card direction and note types.
2. **Read what exists**: the other charters (`list_decks`, then `get_deck_description` on each top-level deck) and the collection's note types (`model_names`). Scope must not overlap another deck's: if it does, ask which deck owns the overlap and say so in both decks' Out of scope. The tag prefix must be unused.
3. **Draft** from `charter-template.md`, against the rules above. Every answer from step 1 must show up in some line of the charter; an answer that changes nothing was a wasted question.
4. **Choose the note types** (next section).
5. **Test it before showing it.** Run `python3 -I <this skill dir>/scripts/charter.py lint <draft.md> --deck <subject>` (without `--deck` away from Anki) and fix every error: it checks the sections, `Assumes:`, Adding, stage numbering and descriptions, length, and that the tag prefix is unused. Then pick three things likely to come up: one clearly in, one borderline, one adjacent but out. Decide each from the charter's text alone; if the text doesn't settle the borderline one, tighten Scope or Out of scope. Then write one sample note in the chosen note type under the Conventions and check that it passes every rule in `SKILL.md`.
6. **Show** the draft, the three test cases and how it decided them, and the sample note as each of its cards would show it. Ask what's left as a second, shorter questionnaire: Automatic or Ask (suggest Ask until the first few batches look right), the note-type choice when there's a real alternative, anything step 5 left open, and one optional question for the deck's look: **how does studying this make you feel, and how would you like it to feel?** (options like calm, playful, focused, cozy, plus a free answer). Never repeat a round-one question. Revise until the user says yes.
7. **Pick a look**, as "Themes" in `note-types.md` says: build two or three themes from the answer (or from the subject, if the user skipped it), show each on the sample note, and let the user pick one, or none. On a pick, Conventions name the theme's note types, `<Deck> · Basic` and `<Deck> · Cloze`, in place of Basic and Cloze.
8. **Save**: the theme's note types and any other new note type first (as `note-types.md` says), then `create_deck` for the subject and for each stage (`<Subject>::01 <name>`), then `update_deck_description` on the top-level deck with the full text and `is_markdown: true`, then sync as in `SKILL.md`. Report in one line.

## Choosing note types

Basic and Cloze cover most subjects. Look for something better only when the subject's cards keep the same multi-part shape. Check in this order:

1. **Reuse what the user has.** If `model_names` lists a type that fits, read its fields and templates (`model_field_names`, `model_templates`) and use it. Never create a near-copy of a type the user already has.
2. **A new type is worth proposing when**:
   - Most cards share one shape with several parts (a word, the sentence it appeared in, a gloss, where it came from) that Basic would cram into one Back field.
   - One note should give cards for different skills from the same fields, such as recognizing a word and producing it.
   - A template can derive a view the user would otherwise type twice, such as blanking the word in its own sentence for production and bolding it for recognition. The answer lives in one field, so the two views can't drift apart.
3. **It isn't worth it when** the cards vary in shape (most technical subjects: Basic plus Cloze is enough), only a handful of cards would use it, or the only gain is looks. The one exception is a deck's theme: copies of Basic and Cloze with the same fields and only new styling (see "Themes" in `note-types.md`).
4. **Count the costs in the proposal.** The templates need a versioned home (if the user keeps note types in a repo, the change goes there, not into a second copy in Anki). Anki doesn't officially support JavaScript in templates, so a scripted template must be tested on every device the user reviews on. Every way cards come in, this skill included, has to fill the fields right.
5. **Two types for two levels of one item** (recognition and production) need a default and a test for moving a note up, written in the charter: for example, "default to recognition; move a word to production once you've reached for it and not had it, or keep using the wrong word for it". The user moves a note in Anki's browser (Change Note Type), which keeps its review history but forces a full sync, like a field change (see `note-types.md` for the sync order); so suggest moving notes in batches, and never do it yourself.

Write the outcome into Conventions: which note type each kind of card uses, what goes in each field, and the move-up rule if there is one. To design, build or change a note type, read `note-types.md` in this skill's directory first.

## Changing a charter

Change one when the user asks. Propose a change yourself only when the evidence shows the charter, not the cards, is the cause: the same kind of card rejected or rewritten more than once, or problem cards that share a cause.

1. **Read** the current text (`get_deck_description`) and the evidence: the user's complaint, the deck's problem cards (`tag:leech or tag:marked`), and the subdecks that exist (`list_decks`) against the stages listed.
2. **Name the cause** in one sentence ("Scope doesn't say whether regional slang is in, so it's been carded inconsistently"). A topic that keeps getting carded and rejected belongs in Out of scope; a rule that keeps getting broken belongs in Conventions; cards whose parts keep getting crammed into one field may point to a note type.
3. **Make the smallest change** that fixes it, and keep every other line word for word: the user may have edited the description by hand. Save the current text to a file and the new section body to another, then run `charter.py edit <current.md> "<section>" <body.md> <new.md>`: it changes only that section and prints the diff to show the user. Lint `new.md` as in "Creating a charter".
4. **List what it does to existing cards**: how many cards fall out of scope (offer to tag them `to-delete`), which stages are renamed, split or reordered (a stage rebuild, as in `SKILL.md`), which cards break a new convention (offer a rebuild; never rewrite them silently), and how many notes a note-type change touches.
5. **Show** the old and new text of each changed section, with those consequences, and update only on a yes. `update_deck_description` replaces the whole description, so send the full text, then sync.

## Away from Anki

Without the Anki tools, charters and note types can't be read or saved. Run the questionnaire and draft a new charter the same way, skipping the steps that need Anki (other charters, the collection's note types, existing cards), and once the user approves it, queue it in the Anki inbox as one json block:

```json
{"charter": {"deck": "Spanish", "stages": ["01 Sounds and spelling", "02 Present tense"], "description": "<full charter text>", "theme": {"...": "the picked theme.json, or null"}}}
```

The theme can still be picked away from Anki: `build_theme.py` needs only Python, and the previews can be drawn inline. Its note types are created when the charter is saved.

A change to an existing charter needs its current text, so queue the request instead, in the user's words:

```json
{"charter_change": {"deck": "Spanish", "request": "stop carding regional slang"}}
```

When the inbox is emptied, these go before any card. For a queued charter, run the skipped steps; if they change nothing, save it, since the user already approved it, and otherwise show the change first. If the deck already exists or has a description, that is a change too: show the old and new text, as in "Changing a charter", and save only on a yes. If the skipped note-type check finds a type that fits, that is a change: ask before switching. A queued change goes through "Changing a charter" from the top. Delete each charter block from the inbox once it is saved or applied, so it isn't replayed.
