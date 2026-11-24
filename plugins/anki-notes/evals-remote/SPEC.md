# anki-notes remote eval spec

What the [`claude plugin eval`](https://code.claude.com/docs/en/plugin-evals.md) suite in this folder tests: the skill against the remote server, [anki-sync-mcp](https://github.com/ledhed2222/anki-sync-mcp). The case list below is generated from the case files by `../evals/gen_spec.py evals-remote`; everything else here is written by hand.

## What it protects

The local suite in `../evals/` tests how cards are written. This one tests what is different on the remote server: ids instead of names, one `anki_notes_create` per card with an idempotency key, saving charters with `anki_decks_update`, note-type changes through a preview token, `MANUAL_CHANGE_REQUIRED`, a server without the schema tools, and the error-and-retry path when the server can't be reached.

## How a run works

As in `../evals/SPEC.md`, except that `mocks/anki/` holds only the remote server's tools, so Claude sees an anki-sync-mcp server. `_tools.json` is a subset of its real `tools/list` (ledhed2222/anki-sync-mcp at 47c5699), and the mock replies follow replies recorded from a live server. The note-type tools are mocked per case, so `remote-no-schema` sees a server without them.

Run it with `mise run eval-remote` (from the plugin folder), which points the harness at this folder with `--eval-dir evals-remote`.

## Scoring and the pass bar

The same as the local suite: every grader passes in every run (pass bar 1.00).

## Cases

<!-- generated:start -->
| case | what it checks |
|---|---|
| [`remote-add-cards`](#remote-add-cards) | On the remote server, teaching a concept adds one-fact cards in an anki_notes_create_batch that skips duplicates, with the stage deck's and note type's ids. |
| [`remote-charter-save`](#remote-charter-save) | On the remote server, an approved charter creates the deck and its stages, saves the full text with anki_decks_update. |
| [`remote-manual-change`](#remote-manual-change) | A structural note-type change that this client can't approve shows the server's MANUAL_CHANGE_REQUIRED steps to the user instead of retrying. |
| [`remote-no-schema`](#remote-no-schema) | When the server doesn't offer the note-type tools, a CSS change is declined in one line and nothing claims it was made. |
| [`remote-restyle`](#remote-restyle) | Changing a note type's CSS on the remote server previews just the CSS, then updates it with the same values and the preview's token. |
| [`remote-retry`](#remote-retry) | After an outage, cards drafted earlier in the conversation are checked against the deck before they're added, and a card the deck already holds is reported, not added again. |
| [`remote-unreachable`](#remote-unreachable) | When the server can't be reached, the reply says so in one line, says nothing was saved, and shows the drafted cards in full instead of queuing them. |

### remote-add-cards

On the remote server, teaching a concept adds one-fact cards in an anki_notes_create_batch that skips duplicates, with the stage deck's and note type's ids.

**User message:**

> Can you explain precision and recall for a classifier? I get them mixed up.

**Deck:** the shared mock deck.

| grader | kind | passes when |
|---|---|---|
| `creates` | tool check | `anki_notes_create_batch` is called at least once |
| `keyed` | tool check | `anki_notes_create_batch` with input matching `idempotency_key` is called at least once |
| `looks-up-types` | tool check | `anki_note_types_list` is first called before `anki_notes_create_batch` |
| `one-fact` | LLM judge, reads the transcript | Look at the cards in every anki_notes_create_batch call. PASS if every card's answer (Back, or each cloze blank) is one fact that can be recalled exactly: a word, a number, or one short clause, with any context in an optional Why/Example line. FAIL if any card's answer packs two or more separate facts, a list, or more than one sentence of explanation. |
| `skips-duplicates` | tool check | `anki_notes_create_batch` with input matching `\"skip_duplicates\":\\s*true` is called at least once |
| `uses-stage-id` | tool check | `anki_notes_create_batch` with input matching `\"deck_id\":\\s*170000000000[2-6]` is called at least once |
| `uses-type-id` | tool check | `anki_notes_create_batch` with input matching `\"note_type_id\":\\s*170000000010[12]` is called at least once |

### remote-charter-save

On the remote server, an approved charter creates the deck and its stages, saves the full text with anki_decks_update.

**User message:**

> Yes, that charter looks right. Save it for my new Spanish deck exactly as below.
>
> ## Scope
> Spanish for living in Madrid: everyday grammar, common verbs, and words met in reading. In: verb tenses, ser vs estar, por vs para.
>
> Assumes: present and past tense forms.
>
> ## Out of scope
> Latin American slang (nowhere). Travel logistics (looked up).
>
> ## Adding
> Ask.
>
> ## Stages
> `01 Sounds and spelling` — accents and stress.
> `02 Present tense` — irregular verbs, ser/estar and por/para.
> `03 Past tenses` — preterite vs imperfect.
>
> ## Conventions
> - Prefer cloze sentences from my reading.
> - Tags: `es::<area>::<topic>`.

**Deck:** the shared mock deck, with this case's own `anki_decks_list`.

| grader | kind | passes when |
|---|---|---|
| `creates-deck` | tool check | `anki_decks_create` with input matching `\"name\":\\s*\"Spanish\` is called at least once |
| `creates-stage-03` | tool check | `anki_decks_create` with input matching `Spanish::03 Past tenses` is called at least once |
| `deck-before-description` | tool check | `anki_decks_create` is first called before `anki_decks_update` |
| `saves-full-text` | tool check | `anki_decks_update` with input matching `Out of scope[\\s\\S]*03 Past tenses[\\s\\S]*Tags` is called at least once |

### remote-manual-change

A structural note-type change that this client can't approve shows the server's MANUAL_CHANGE_REQUIRED steps to the user instead of retrying.

**User message:**

> Add an Extra field to my Basic note type, after Back. I've already synced my other devices, so go ahead.

**Deck:** the shared mock deck, with this case's own `anki_note_type_fields_update`, `anki_note_types_change_preview`, `anki_note_types_update`.

| grader | kind | passes when |
|---|---|---|
| `shows-steps` | LLM judge, reads the final reply | PASS if the reply says the field wasn't added from here and gives the user the server's steps to do it in Anki Desktop: open Tools > Manage Note Types, select Basic, click Fields, add Extra after Back, accept the one-way sync and sync choosing Upload. FAIL if it says the field was added, leaves out the steps, or says it will keep retrying. |
| `tries-once` | tool check | `anki_note_type_fields_update` is called at least once |

### remote-no-schema

When the server doesn't offer the note-type tools, a CSS change is declined in one line and nothing claims it was made.

**User message:**

> In my Basic note type, change the card CSS's font-size from 20px to 22px. Go ahead without asking.

**Deck:** the shared mock deck.

| grader | kind | passes when |
|---|---|---|
| `no-type-writes` | tool check | `anki_notes_create` is never called |
| `says-unavailable` | LLM judge, reads the final reply | PASS if the reply says the note type can't be changed from here because the server doesn't offer note-type editing (its schema tools aren't turned on), and doesn't claim the CSS was changed. FAIL if it says the CSS was changed, or invents a tool or workaround that changes the note type anyway. |

### remote-restyle

Changing a note type's CSS on the remote server previews just the CSS, then updates it with the same values and the preview's token.

**User message:**

> In my Basic note type, change the card CSS's font-size from 20px to 22px. I've seen the change and want it, so go ahead without asking again.

**Deck:** the shared mock deck, with this case's own `anki_note_type_fields_update`, `anki_note_types_change_preview`, `anki_note_types_update`.

| grader | kind | passes when |
|---|---|---|
| `css-only` | tool check | `anki_note_types_update` with input matching `^(?![\\s\\S]*\"templates\")[\\s\\S]*font-size:\\s*22px` is called at least once |
| `new-css` | tool check | `anki_note_types_update` with input matching `font-size:\\s*22px` is called at least once |
| `previews-first` | tool check | `anki_note_types_change_preview` is first called before `anki_note_types_update` |
| `sends-token` | tool check | `anki_note_types_update` with input matching `BEqYW5eqbdOTUeCMU3EbqJ2rpoK4--izQ_aVfujWItc` is called at least once |

### remote-retry

After an outage, cards drafted earlier in the conversation are checked against the deck before they're added, and a card the deck already holds is reported, not added again.

**User message:**

> Earlier in this conversation you drafted these cards for my AI Engineering deck, and I approved them, but the Anki server was down so nothing was saved:
>
> ```json
> [
>  {
>   "deck": "AI Engineering",
>   "stage": null,
>   "model": "Basic",
>   "fields": {
>    "Front": "What does a binary classifier do?",
>    "Back": "Sorts each input into one of <b>two classes</b>."
>   },
>   "tags": [
>    "aie::metrics::basics",
>    "type::definition",
>    "src::metrics"
>   ]
>  },
>  {
>   "deck": "AI Engineering",
>   "stage": null,
>   "model": "Basic",
>   "fields": {
>    "Front": "A spam filter flags a real email as spam. Which kind of error is this: a false positive or a false negative?",
>    "Back": "<b>A false positive.</b>"
>   },
>   "tags": [
>    "aie::metrics::errors",
>    "type::application",
>    "src::metrics"
>   ]
>  },
>  {
>   "deck": "AI Engineering",
>   "stage": null,
>   "model": "Basic",
>   "fields": {
>    "Front": "A classifier misses a fraudulent payment and lets it through. Which kind of error is this: a false positive or a false negative?",
>    "Back": "<b>A false negative.</b>"
>   },
>   "tags": [
>    "aie::metrics::errors",
>    "type::application",
>    "src::metrics"
>   ]
>  }
> ]
> ```
>
> I've restarted the server. Add them now.

**Deck:** the shared mock deck.

| grader | kind | passes when |
|---|---|---|
| `adds-the-rest` | tool check | `anki_notes_create_batch` with input matching `spam filter[\\s\\S]*fraudulent\|fraudulent[\\s\\S]*spam filter` is called at least once |
| `reports-the-duplicate` | LLM judge, reads the final reply | PASS if the reply says the two error cards (the spam filter and the fraudulent payment) were added, and that the binary-classifier card was not added again because the deck already has it. FAIL if it says all three were added, says nothing about the binary-classifier card, or says a card failed. |
| `searches-first` | tool check | `anki_notes_search` is first called before `anki_notes_create_batch` |

### remote-unreachable

When the server can't be reached, the reply says so in one line, says nothing was saved, and shows the drafted cards in full instead of queuing them.

**User message:**

> Can you explain what an F1 score is and why it uses a harmonic mean? Add it to my AI Engineering deck.

**Deck:** the shared mock deck, with this case's own `anki_cards_reposition`, `anki_cards_search`, `anki_decks_get`, `anki_decks_list`, `anki_note_types_get`, `anki_note_types_list`, `anki_notes_create`, `anki_notes_create_batch`, `anki_notes_get`, `anki_notes_search`, `anki_sync`.

| grader | kind | passes when |
|---|---|---|
| `error-and-drafts` | LLM judge, reads the final reply | PASS if the reply says Anki (or the Anki server) couldn't be reached and that nothing was saved, and shows the drafted cards in full (front and back, or the cloze text), so they could be added later. FAIL if it claims any card was added, says the cards were queued, saved to a doc, an inbox or a file, or gives only a summary of the cards instead of their full text. |
| `no-write-succeeds` | tool check | `anki_sync` is never called |
<!-- generated:end -->
