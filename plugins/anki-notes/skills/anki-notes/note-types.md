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

## Themes

A theme gives a deck its own look, built from how the user says studying it feels and how they'd like it to feel. The point is enjoyment, which keeps people reviewing; never claim it improves recall. If someone says a subject makes them anxious, design for how they want to feel, not for the anxiety.

A theme is a spec, `theme.json`, and `scripts/build_theme.py` (its docstring has the format) turns it into the stylesheet, two note types and a preview. Never hand-write theme CSS:

- **Note types:** `<Deck> · Basic` and `<Deck> · Cloze`, with exactly the stock fields (Front and Back, Text and Extra). The skill fills them as before, and moving the deck's existing notes onto them (Change Note Type, in the browser, by the user) keeps every review. This is the one case where a note type that only changes looks is worth it.
- **What it varies:** the background, text, accent and rule colors, in light and night mode, and up to two fonts. Body text uses a plain, legible font (the system font is fine); a font with character goes on the deck label and the highlighted answer. Layout, sizes and spacing stay fixed.
- **Legibility is enforced:** the script refuses any text or accent color below 4.5:1 contrast against its background in either mode. Pick new colors; don't argue with the check.
- **Fonts** must be openly licensed: any Google Fonts family, which `build_theme.py` fetches itself as a Latin-subset `.woff2` from npm (`fetch_font.py`; npm is reachable from the claude.ai sandbox when Google's font servers aren't). Name the family in `theme.json`; don't download fonts any other way. The build names each file `_<family>.woff2` (the leading `_` keeps Anki's Check Media from deleting it), writes them next to `preview.html`, and lists them in `media.json`. When saving, call `store_media_file` once per entry with its `filename` and `path` (the path works because Claude Code and Anki run on the same machine; away from Anki, the queued charter keeps the `theme.json` and the files are fetched again when it's saved). They sync to every device, so use one or two families, or none. If a fetch fails the build warns and the theme falls back to the system font; mention it to the user.
- **Built in:** dots on the deck label for the stage (`●○○` in stage 01), and a small "rescued" badge on the back of a card tagged `rescued`.
- **Motion** is off unless the user turns it on after seeing it: a 120 ms fade of the answer and a single shimmer on the rescued badge, both off when the device asks for reduced motion. Nothing loops and nothing moves.
- **Language decks:** suggest Anki's built-in speech, `{{tts es_ES:Field}}` in the template, which reads a field aloud with the device's own voices. It belongs in a note type with a dedicated sentence field, not in the Basic copy.

To pick one: draft two or three `theme.json` files that read the user's words differently (one quieter, one bolder), build each, and show the previews (in Claude Code, `preview.html` from the build; elsewhere, draw the sample cards inline). Ask which they want with the app's question tool, offering "none" too. On a pick, ask whether to turn motion on. On save, `create_model` with each object in the build's `models.json`. If the deck uses note types the user keeps in a repo, the theme goes into that repo's stylesheet instead, and the user applies it.

To change a theme, edit its `theme.json` (its mood and colors are in the comment at the top of the CSS), rebuild, and apply with `update_model_styling` to both note types.

## Propose before building

Check the design first: write the templates (as `model_templates` returns them) and a sample note to a JSON file and run `python3 -I <this skill dir>/scripts/render_note.py <spec.json>`, or for an existing type `render_note.py <note.json> --model <type>`. It renders every card, fails when a front shows its answer or a back reuses `{{FrontSide}}` under a scripted front that hides it, and can't run JavaScript, so a scripted type still needs a preview in Anki. Show the user the type's name and fields, how many cards each note makes and what each asks, the templates, and one sample note as each of its cards' fronts and backs would show it. Build only on a yes.

## Build

- **If the user keeps note types in a repo or folder**, write the templates there and tell them how to apply them. Don't also create them in Anki: two copies drift.
- **Otherwise** create it with `create_model`: the fields in order, one card template per card (`Name`, `Front`, `Back`), and the CSS.
- Before adding many notes of a new type, have the user preview a few cards in Anki and review one on each device they study on, phone included.

## Change

A change to a note type changes every note of that type. Count them (`find_notes` with `note:"<type>"`), show the old and new templates or fields, and apply only on a yes:

- **Templates and CSS**: `update_model_templates` (patch mode for small edits) and `update_model_styling`.
- **Renaming a field** (`model_field_rename`) keeps its content and rewrites the templates that use it. It doesn't force a full sync by itself, but if its `will_force_full_sync` comes back true, an earlier change already did: handle the sync as below.
- **Adding or reordering a field** (`model_field_add`, `model_field_reposition`) forces the next sync to be a full one, which replaces the collection on one side. Do it in this order so no reviews are lost: (1) the user syncs every other device and confirms; (2) sync here, so this collection holds every review; (3) make the change; (4) sync, which uploads this collection over AnkiWeb and the other devices. If Anki asks which side to keep instead, stop and let the user choose.
- **Removing a field** deletes its content from every note, and there is no tool for it: the user does it in Anki (Tools → Manage Note Types → Fields), in the same sync order.
- **Moving notes to another type** is the user's job, in Anki's browser (Change Note Type), never this skill's. It also forces a full sync, so give the user the same sync order, and suggest moving notes in batches rather than one at a time.
