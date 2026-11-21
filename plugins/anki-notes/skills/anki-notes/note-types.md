# Designing a note type

Read this only when a charter calls for a new note type or a change to one. Whether a subject needs one at all is decided in `charters.md`.

## Design

- **One field per part** of the card: the word, its sentence, the gloss, a hint, the source. A part that's sometimes missing is an optional field the template hides when empty (`{{#Source}}…{{/Source}}`).
- **The answer is typed once.** Every view of it (bolded on one card, blanked on another) comes from the same field through the template.
- **The front never shows the answer.** Check each card's front against a sample note. A back built on `{{FrontSide}}` inherits whatever the front did, so the back of a card whose front hides the answer must render the fields fresh.
- **A production card gets a hint field** that makes exactly one answer right, such as a short gloss in the user's own language shown under the blank. This is `SKILL.md`'s one-right-answer rule built into the type.
- **Plain templates first.** Use CSS and Anki's field filters (`{{text:Field}}` strips pasted HTML) before JavaScript. If a script is unavoidable, keep it self-contained in one IIFE: a back that reuses `{{FrontSide}}` runs it a second time in the same page.
- **Name fields for good.** Templates refer to fields by exact name, accents included.
- Close void tags in templates: `<br />`, `<hr />`.

## Propose before building

Show the user the type's name and fields, how many cards each note makes and what each asks, the templates, and one sample note as each of its cards' fronts and backs would show it. Build only on a yes.

## Build

- **If the user keeps note types in a repo or folder**, write the templates there and tell them how to apply them. Don't also create them in Anki: two copies drift.
- **Otherwise** create it with `create_model`: the fields in order, one card template per card (`Name`, `Front`, `Back`), and the CSS.
- Before adding many notes of a new type, have the user preview a few cards in Anki and review one on each device they study on, phone included.

## Change

A change to a note type changes every note of that type. Count them (`find_notes` with `note:"<type>"`), show the old and new templates or fields, and apply only on a yes:

- **Templates and CSS**: `update_model_templates` (patch mode for small edits) and `update_model_styling`.
- **Renaming a field** (`model_field_rename`) keeps its content and rewrites the templates that use it. It doesn't force a full sync by itself, but if its `will_force_full_sync` comes back true, an earlier change already did: handle the sync as below.
- **Adding or reordering a field** (`model_field_add`, `model_field_reposition`) forces the next sync to be a full one, which replaces the collection on one side. Before doing it, sync, and ask the user to sync every other device first so no reviews are lost; then make the change and sync, and if Anki asks which side to keep, stop and let the user choose.
- **Removing a field** deletes its content from every note, and there is no tool for it: the user does it in Anki (Tools → Manage Note Types → Fields), after the same sync-every-device step.
- **Moving notes to another type** is the user's job, in Anki's browser (Change Note Type), never this skill's.
