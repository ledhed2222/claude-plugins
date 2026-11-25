# Designing a note type

Read this only when a charter calls for a new note type or a change to one. Whether a subject needs one at all is decided in `charters.md`.

## Design

- **One field per part** of the card: the word, its sentence, the gloss, a hint, the source. A part that's sometimes missing is an optional field the template hides when empty (`{{#Source}}…{{/Source}}`).
- **The answer is typed once.** Every view of it (bolded on one card, blanked on another) comes from the same field through the template.
- **The front never shows the answer.** Check each card's front against a sample note. A back built on `{{FrontSide}}` inherits whatever the front did, so the back of a card whose front hides the answer must render the fields fresh.
- **A production card gets a hint field** that makes exactly one answer right, such as a short gloss in the user's own language shown under the blank. This is `SKILL.md`'s one-right-answer rule built into the type.
- **Plain templates first.** Use CSS and Anki's field filters (`{{text:Field}}` strips pasted HTML) before JavaScript. If a script is unavoidable, keep it self-contained in one IIFE: a back that reuses `{{FrontSide}}` runs it a second time in the same page.
- **The last field is `Feedback`, in no template.** It's where the user, while reviewing, types why a note is badly made; it never shows on a card, only in the note editor. `build_theme.py` adds it to a theme's types; add it to any other type you create. `render_note.py` errors if a template shows it.
- **Name fields for good.** Templates refer to fields by exact name, accents included.
- Close void tags in templates: `<br />`, `<hr />`.

## Themes

A theme gives a deck its own look, built from how the user says studying it feels and how they'd like it to feel. The point is enjoyment, which keeps people reviewing; never claim it improves recall. If someone says a subject makes them anxious, design for how they want to feel, not for the anxiety.

A theme is a spec, `theme.json`, and `scripts/build_theme.py` (its docstring has the format) turns it into the stylesheet, two note types and a preview. Never hand-write theme CSS:

- **Note types:** `<Deck> · Basic` and `<Deck> · Cloze`, with the stock fields (Front and Back, Text and Extra). The skill fills them as before, and moving the deck's existing notes onto them (Change Note Type, in the browser, by the user) keeps every review. This is the one case where a note type that only changes looks is worth it.
- **What it varies:** the background, text, accent and rule colors, in light and night mode, and up to two fonts. Layout, sizes and spacing stay fixed.
- **Legibility is enforced:** the script refuses any text or accent color below 4.5:1 contrast against its background in either mode. Pick new colors; don't argue with the check.
- **Alphabets:** set `subsets` to every script the deck's cards use (`latin` covers Spanish, French and German; add `cyrillic` for Russian or Ukrainian, `greek`, `vietnamese`, and the `-ext` subsets for rarer accented letters). Each is a separate small file that a device only loads when a card uses it. Languages these subsets don't cover (Chinese, Japanese, Korean, Arabic, Hebrew, Indic scripts) keep the system font: set both fonts to null.
- **Fonts** are any Google Fonts family, all openly licensed. `build_theme.py` fetches them itself from npm with `fetch_font.py` (npm is reachable from the claude.ai sandbox when Google's font servers aren't); never download fonts another way. Before proposing a family, run `fetch_font.py --info "<Family>"`: it prints the category, alphabets, weights and styles, and the build fails if a font lacks one of the deck's alphabets (Fraunces and Atkinson Hyperlegible have no Cyrillic, for example). The body font gets real bold (`weights: [400, 700]`) since cards bold key terms; set `italic: true` when cards quote or use italics. The build writes each file as `_<family>-<subset>-<weight>[-italic].woff2` (the leading `_` keeps Anki's Check Media from deleting it) and lists them in `media.json`; when saving, store each entry ("Store a media file"). On local, `store_media_file` takes its `filename` and `path` (Claude Code and Anki share a machine). The AnkiMCP add-on stores only images, audio and video unless its config allows more, so the first font may fail with `File type not allowed for media import`. Then don't retry, and save everything else: the note types work without the files and show the system font. Tell the user to add `"font/woff2"` to `media_allowed_types` in Tools → Add-ons → AnkiMCP → Config and then restart Anki, and store the fonts once they say it's done. On remote, `anki_media_store` takes the file's bytes as `content_base64` (`base64 -i <path>`), up to the server's media limit (1 MB by default). A new server refuses media with `MEDIA_SYNC_IN_PROGRESS` until its first media download finishes: save everything else, as above, and store the fonts once the user says the download is done (`SKILL.md` has the details). Everything syncs to every device, so two families at most.

### Choosing fonts

Pick from what the deck's cards are made of, then let the mood choose within that:

- **The body font is what the user reads hundreds of times a day.** Choose a face made for reading at text size, in the category that fits the material. Display faces, such as Fraunces at its expressive settings, go only on the deck label.
- **Literary material** (vocabulary in example sentences, quotations, history, philosophy): a text serif, with italics. For example Literata, Source Serif 4, Lora, EB Garamond, PT Serif.
- **Technical material** (engineering, code, data): a clean sans for the body and a monospace for the label and highlighted terms. For example IBM Plex Sans with IBM Plex Mono, or Inter with JetBrains Mono.
- **Formulas and symbols** (math, chemistry): a serif with clear numerals and distinct `l`, `1` and `I`, like Source Serif 4 or Literata.
- **Mood within the category:** warm and unhurried leans to Lora or a soft serif label; calm and quiet to Literata or Source Serif 4 with a muted accent; playful to a rounded sans like Nunito on the label; precise to Plex. If the mood answer was skipped, the material alone decides.

These are starting points, not a list to stay inside. Every family above was checked with `--info`; check anything else the same way.

- **Built in:** dots on the deck label for the stage (`●` in stage 01, `●●●●` in stage 04), and a small "rescued" badge on the back of a card tagged `rescued`.
- **Motion** is off unless the user turns it on after seeing it: a 120 ms fade of the answer and a single shimmer on the rescued badge, both off when the device asks for reduced motion. Nothing loops and nothing moves.
- **Language decks:** suggest Anki's built-in speech, `{{tts es_ES:Field}}` in the template, which reads a field aloud with the device's own voices. It belongs in a note type with a dedicated sentence field, not in the Basic copy.

### Picking and changing a theme

To pick one: draft two or three `theme.json` files, each a different font pairing as well as a different palette (one quieter, one bolder; for a literary deck, say, Literata, Lora with a Nunito label, and Source Serif 4). Build each with the deck's sample note as its `sample` (without one, the preview shows a generic English card) and show the previews on it in the deck's own language (in Claude Code, put the builds side by side in one folder, named by their fonts and feel, run `build_theme.py --compare <folder>/compare.html <out dir>...` and open only `compare.html`: it shows every option in one browser tab, each with its fetched fonts; elsewhere, or when a build fails (npm unreachable, say), draw the sample cards inline, so the user still sees each option on the sample note). Ask which they want with the app's question tool, naming each option by its fonts and feel ("Literata, warm paper"), and offering "none" too. If the user likes one palette but another's fonts, combine them and rebuild. On a pick, ask whether to turn motion on; on a yes, turn `motion` on in its `theme.json` and rebuild, since the drafts were built without it. On save, first store every font file the build fetched, or the cards fall back to the system font (the preview loads them from its own folder, Anki only from its media): local, call `store_media_file` with each entry of `media.json` as it is (the add-on refuses `.woff2` until its `media_allowed_types` config lists `font/woff2`; on that refusal, tell the user to add that in Tools → Add-ons → Config and stop); remote, call `anki_media_store` with each entry of `media-remote.json` as it is (each names the file's pinned jsdelivr `url`, and the server downloads it). Then create each note type in the build's `models.json` (local) or `models-remote.json` (remote), as in "Build" below. If the deck uses note types the user keeps in a repo, the theme goes into that repo's stylesheet instead, and the user applies it.

To change a theme, edit its `theme.json` (its mood and colors are in the comment at the top of the CSS), rebuild, store its font files as on save if the fonts, weights or alphabets changed, and apply the new CSS to both note types, as in "Change" below.

## Propose before building

Check the design first: write the templates (as `model_templates` returns them) and a sample note to a JSON file and run `python3 -I <this skill dir>/scripts/render_note.py <spec.json>`, or for an existing type save its "Read a note type" reply (`model_templates` or `anki_note_types_get`) and run `render_note.py <note.json> --templates <reply.json>`. It renders every card, fails when a front shows its answer or a back reuses `{{FrontSide}}` under a scripted front that hides it, and can't run JavaScript, so a scripted type still needs a preview in Anki. Show the user the type's name and fields, how many cards each note makes and what each asks, the templates, and one sample note as each of its cards' fronts and backs would show it. Build only on a yes.

## Build

- **If the user keeps note types in a repo or folder**, write the templates there and tell them how to apply them. Don't also create them in Anki: two copies drift.
- **Otherwise** create it in Anki: the fields in order, one card template per card, and the CSS.
  - **local:** `create_model` with `model_name`, `in_order_fields`, `card_templates` (`Name`, `Front`, `Back`), `css` and `is_cloze`: the shape of `models.json`.
  - **remote:** `anki_note_types_change_preview` with `operation: "create"`, `name`, `fields`, `templates` (`name`, `question_format`, `answer_format`) and `css`, then `anki_note_types_create` with the same values and the preview's `confirmation_token`, plus `kind: "cloze"` for a Cloze type. Preview and create one type at a time, never previews in parallel: each create invalidates every other outstanding token. The server refuses a Cloze type unless it has exactly one template whose front names one of its fields as literally `{{cloze:<Field>}}`: no filter chain such as `{{text:cloze:<Field>}}`, though Anki itself accepts one; a theme's `models-remote.json` holds these values.
- Before adding many notes of a new type, have the user preview a few cards in Anki and review one on each device they study on, phone included.

## Change

A change to a note type changes every note of that type. Count them (search notes with `note:"<type>"`), show the old and new templates or fields, and apply only on a yes.

### local

- **Templates and CSS**: `update_model_templates` (patch mode for small edits) and `update_model_styling`.
- **Renaming a field** (`model_field_rename`) keeps its content and rewrites the templates that use it. It doesn't force a full sync by itself, but if its `will_force_full_sync` comes back true, an earlier change already did: handle the sync as below.
- **Adding or reordering a field** (`model_field_add`, `model_field_reposition`) forces the next sync to be a full one, which replaces the collection on one side. Do it in this order so no reviews are lost: (1) the user syncs every other device and confirms; (2) sync here, so this collection holds every review; (3) make the change; (4) sync, which uploads this collection over AnkiWeb and the other devices. If Anki asks which side to keep instead, stop and let the user choose.
- **Removing a field** deletes its content from every note, and there is no tool for it: the user does it in Anki (Tools → Manage Note Types → Fields), in the same sync order.

### remote

Note-type changes need the server's schema tools, which a deployment turns on separately: `admin` in `MCP_SCOPES` and `ANKI_ALLOW_SCHEMA_CHANGES`, plus `ANKI_ALLOW_FULL_SYNC` for field and template changes. If a tool below isn't listed, the change can't be made from here: say so in one line, and treat theming as optional.

- **Templates text, CSS and renames** sync normally. Call `anki_note_types_change_preview` with `operation: "update"`, the `note_type_id` and only what changes (`css` to restyle, `templates` for template text, `name` or `fields` to rename), then `anki_note_types_update` with exactly the same values and the preview's `confirmation_token`: the token covers what was sent, so a different set is refused. Anything left out stays as it is (send `css: ""` to clear the CSS), and a field rename also updates the templates that use it. The field and template counts must stay the same.
- **Adding, removing or reordering a field or template** forces a full sync. Preview it with `operation: "fields_update"` and `field_mappings` (every field in its new order; an existing one keeps its `source_ordinal`, a new one has none), or `"templates_update"` with `template_mappings`, then call `anki_note_type_fields_update` or `anki_templates_update` with the mappings and the token. The server asks the user to approve it itself.
  - **`MANUAL_CHANGE_REQUIRED`**: this app can't show the server's approval prompt. The error's `details` hold the field list and `steps` for making the change in Anki Desktop. Show them to the user as they are, numbered, and don't retry.
  - **`CONFIRMATION_DECLINED`**: the user said no. Don't retry, and say the note type is unchanged.

### Either server

- **Moving notes to another type** is the user's job, in Anki's browser (Change Note Type), never this skill's. It also forces a full sync, so give the user the same sync order, and suggest moving notes in batches rather than one at a time.
