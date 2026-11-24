---
name: anki-notes
description: Turn something just taught into atomic Anki flashcards in the right subject deck. Use whenever the user says "add this to anki", "make a card", "flashcard this", and whenever you explain a concept the user would plausibly want to remember, in any subject (a language, a science, a technical field): the subject's deck charter then decides whether cards are added, offered or skipped. For AI engineering (evals, metrics, LLMs, grounding, extraction, RAG, agents, tooling), where cards are added automatically, including at the end of each step of a walkthrough. Also use it to set up a deck for a new subject, to write or change a deck's charter, and to add cards drafted earlier in the conversation once Anki is reachable again.
---

# Anki notes

Turn what was just taught into cards the user can actually study, then add them.

## Subjects and charters

Each subject is a top-level deck (`AI Engineering`, a language, ...), and its rules live in that deck's **charter**: its description in Anki ("Read a charter" in "Anki tools" below). The charter says what is in and out of scope, whether cards are added automatically or only proposed, the stage subdecks, and any card conventions for that subject. **Its rules add to the ones below and win where they conflict.**

- **Pick the subject** by reading the charters of the top-level decks ("List decks", then "Read a charter" on each). If nothing fits, don't guess: propose a new deck and its charter.
- **Adding:** if the charter says Automatic, add cards without asking, including mid-walkthrough. Otherwise end your reply with one line ("2 possible cards for Spanish: … — add them?") and add only on a yes.
- **Teaching, not doing:** only explanations of a concept in a charter's scope count. Most of what you explain while doing a task (a command, a config fix, a debugging step) is not.
- **Writing or changing a charter:** read `charters.md` in this skill's directory first and follow it. Never save one without showing the user the text (old and new, for a change) and getting a yes.

## What earns a card

- **Durable, general knowledge** in the charter's scope that carries over beyond the current project.
- **Not** project-specific names (modules, tickets, clients, datasets) and nothing the user would simply look up (commands, flags, config syntax). If a project taught a general lesson, write the card about the lesson and leave the project out.
- Skip anything the deck already holds (step 2 checks).

## Is it worth a card at all?

Most rejected cards failed here, not on wording. Every candidate must pass all four; drop it otherwise. Fewer, better cards beat coverage.

- **Worth memorizing:** the user would want it on recall a year from now. Not trivia (the names of OCR preprocessing steps), not one project's process decision (feed a stage stored upstream outputs; give each agent a page count it owns).
- **Not obvious:** if it reduces to common sense ("don't bias the authors", "label with the same category list the system uses", "each sender's workflow decides whether it scans"), skip it.
- **Standard vocabulary only:** never make a card whose answer or premise is a term coined during the session ("noise floor", "truth-leak check", "answer-key category", "rename table"). If the lesson is real, state it in plain words; if it only makes sense with the coined term, it isn't general knowledge.
- **Answerable from the question:** someone who learned the idea must be able to produce the answer without guessing what the author had in mind. "Which role finds the most defects?" has an open answer space; name the options in the question or drop the card. And only one answer may be right: if someone who knows the topic could give a different answer that is also correct, add the context that rules it out. A short topic label at the start of the front ("Evals: …") is often enough, and it keeps a term that means different things in different fields from being read the wrong way.

## Prerequisites come first

The user learns these topics from the cards, so a card may only use a concept the deck has already taught. Before adding a card:

- List every term it relies on (confusion matrix, few-shot, class balance, ROC curve, F-beta...). For each one, find the card that introduces it, in the same or an earlier stage. If there isn't one, write that card first.
- Introduce a concept with the plain questions a newcomer would ask, each its own card: **What is X? What problem does it solve? Why is it built this way** (e.g. why F1 uses a harmonic mean)? Cards about edge cases and tradeoffs come after those.
- **No lone cards.** A concept that earns a card usually gets two or three, each from a different angle: what it is, why it works that way, how it differs from its nearest neighbor, when you'd reach for it. One isolated card is easy to forget and hard to use. Be strict about which concepts get in, not about how many angles each one gets, but each angle must still pass every rule under "What earns a card" on its own; never pad a concept with a weak card.

## Writing the front

- **Self-contained.** The card must make sense alone, shuffled among 200 others, months later. Define any term it relies on inside the card, or use only terms standard in the field. Never assume another card was seen first.
- **A concrete "you" scenario** in plain, complete sentences, then the question. No telegraphic fragments ("Test for whether something belongs in input?") and no compressed jargon.
- **Name the choices** when there are two or three: "Which eval step costs more: inference or scoring?" Name them in every card, never "which kind?" shorthand that leans on a sibling card.
- **Keep the wording short.** A rewrite that adds clauses to "set up context" often reads worse than the original. If the original was clear, keep it and fix only what was wrong.
- **One idea that has two parts stays one note.** "Raising the threshold: precision goes up, recall goes down" is a single relationship. Write it as one Cloze note (`precision {{c1::rises}}, recall {{c2::falls}}`): Anki makes a card per blank from one note, so the idea stays together without two separate notes.
- **For a term, give the description and ask for the name**, not the reverse: "You split a bundled PDF into its component documents. What is this step called?" → **Document segmentation.**

## The rule that matters: one fact per card

A card is studyable only if its back can be recalled **exactly**: one word, a number, or a short clause. The user has rejected cards for being "too broad/vague". So:

- **Split** compound ideas. "Synthetic vs real data" becomes "main advantage of synthetic?", "main weakness of synthetic?", "one job only real data can do?"
- **Prefer scenarios to definitions.** Not "What is a false gold label?" but "An answer key lists a fact that isn't in the input. Which metric drops for every system?" → **Recall.**
- Use **Cloze** for definitions, formulas and three-part structures: `CER = character {{c1::edit distance}} ÷ {{c2::reference length}}`.
- No back longer than one sentence. Context goes in an optional `Why/Example` line, never in the answer itself.

Bad → good:

| bad | good |
|---|---|
| Q: What is pooled recall? A: A label-free technique where the union of systems' outputs… (3 sentences) | Q: In pooled recall, what serves as the pseudo answer key? A: **The union of all systems' outputs.** |
| Q: Grounding vs attribution? A: paragraph | Cloze: Grounding is a {{c1::noun}}; attribution is a {{c2::verb}}. |
| Q: Resuming a half-finished eval after a prompt change produces what kind of run? | Q: You start an eval, pause it, change the prompt, then resume it. Which prompt does the score reflect? A: **A mix of both.** |
| Q: A cache key for saved model outputs must include what, beyond model and settings? | Q: You're building a cache key for model outputs. It already includes the model and its settings. What else must it include for caching to stay correct? A: **A version or hash of the prompt.** |
| Q: Which eval step is expensive and which is cheap: inference or scoring? | Q: Which eval step costs more: inference or scoring? A: **Inference.** |
| Cloze: A {{c1::noise floor}} is how much outputs differ across {{c2::reruns}}… (coined term) | Q: You rerun an unchanged eval and the score moves 3 points. A prompt change then gains 2. What can you conclude? A: **Nothing yet: the gain is within run-to-run variation.** |
| Q: An automated check fails when a gold value appears on an input page. What is it called? A: A truth-leak check. | Drop it: the name is session jargon, and the lesson (don't put answers in the input) is obvious. |

## Vary the shape

A deck where every card is the same plain question gets static. Aim for no more than about 85% of a deck's notes in one format (note type, `type::` tag, with or without media), or the charter's `Variety:` line where it has one; `Variety: none` means keep the deck uniform.

- **Variety is a tiebreaker, never a reason to write a worse card.** When the content has one right shape, it gets that shape. Only when two shapes would teach equally well does the under-used one win.
- **Shapes to pick from**, within what the charter allows: a definition, a contrast, a "you see X, what do you do?" scenario, predict-the-result, spot-the-error, a cloze; and recognition or production of the same item where the charter has both note types.
- **Media only when it carries part of the answer**: a diagram the user supplies or one you draw, or audio in a language deck. Never decorative, and never one whose visible content gives the answer away on the front.
- **Mnemonics are offered, not added**: for an arbitrary fact (a name, a number, an ordered list), propose one or two in your reply and put the one the user picks in the `Why/Example` line or `Extra`. Not for a card the user can reason their way to.

## Last checks before adding

Run every draft through these. They come from the spaced-repetition literature rather than from the user's reviews of real cards, so the rules above win if the two ever disagree.

- **Make it take effort.** No yes/no questions: rewrite them as what, why or which. The front must not hint at its answer: no option that is obviously the right one, no word from the answer in the question, no cloze whose visible text gives the blank away. Paired relationships like the threshold example above are the exception, since recalling both halves together is the point.
- **Lists: one item per card.** Never ask for a whole set ("Name the four…"); card each member that matters by what it does, not just its name. For a short list whose order matters, write one Cloze note with a blank per item, in the same order every time; if the items left visible give a blank away, use separate notes. Never ask for "an example of X", which has many right answers: turn it around, name the example and ask what it's an example of. For a procedure, card the decision points (when to take a step, and why), not the sequence of steps.
- **Separate near neighbors.** When step 2 turns up a card on a similar concept (precision next to recall, few-shot next to fine-tuning), the two will get confused in review. Put the distinguishing feature in the new card's front, or add a `type::contrast` card that names both.
- **Stamp what can go stale.** If the answer depends on a date, a model or library version, a vendor, a benchmark result or a single paper, say so in the question ("As of 2026, …", "In the original RAG paper, …") and tag the source. Better still, card the durable principle behind it and leave the number out. Naming a source is fine when the claim is that source's own; never ask what an article or session said ("what does the post argue about…"), ask about the subject itself.

## Anki tools

Cards reach Anki through the `anki` MCP server of the `ankimcp@ledhed2222` plugin, which connects to one of two servers. Tell which from the tools you have: `anki_decks_list` means **remote** (a self-hosted anki-sync-mcp; it syncs with AnkiWeb itself, so Anki needn't be open), `list_decks` means **local** (the AnkiMCP add-on inside a running Anki Desktop). Use only that server's column below. In claude.ai, the remote server's tools are there only if the user added it as a custom connector; the local one never is.

| Operation | local | remote |
|---|---|---|
| List decks | `list_decks` | `anki_decks_list` (page while `has_more`: the next `offset` is this one plus the reply's `limit`, which can be smaller than the one you sent) |
| Read a charter | `get_deck_description(deck_name)` | `anki_decks_get(name)`: its `description`, and its `id` for saving (`name` is the full deck path, matched without regard to case) |
| Save a charter | `update_deck_description(deck_name, description, is_markdown: true)` | `anki_decks_update(deck_id, description)` |
| Create a deck | `create_deck(deck_name)` | `anki_decks_create(name)` |
| Search notes | `find_notes(query, include_first_field: true, limit, offset)` | `anki_notes_search(query, limit, offset)`: each item has the first field, note type and tags; add `include_fields: true` for every field |
| Read notes in full | `notes_info(notes)` | `anki_notes_search(query: "nid:<id>,<id>,...", include_fields: true)`, one call per page; `anki_notes_get(note_id)` for one note |
| Change a note's fields | `update_note_fields(id, fields)` | `anki_notes_update_fields(note_id, fields)` |
| Tag notes | `tag_add(note_ids, tags: "a b")` | `anki_notes_add_tags(note_ids, tags: ["a", "b"])` |
| List note types | `model_names` | `anki_note_types_list` |
| Read a note type | `model_field_names`, `model_templates`, `model_styling` | `anki_note_types_get(note_type_id)`: fields, templates and CSS |
| Store a media file | `store_media_file` | `anki_media_store(filename, content_base64)` |
| Sync | `sync()`, then poll `sync(job_id)` until it isn't `running`; on `conflict`, call `sync(job_id, resolve: "cancel")` and stop | `anki_sync()`, only when a write's receipt says `remote_synced: false` (the server syncs each write itself by default) |

Note-type changes are in `note-types.md`. On remote:

- **Sync before the first read.** The server syncs with AnkiWeb on every write but not on reads, so its copy can miss changes made on another device since its last write (a deck deleted in Anki Desktop still shows up). Pass `sync_before: true` on the first read of a session, normally "List decks".
- **Ids, not names, for writes.** A charter read by name gives that deck's `id`; other deck ids come from `anki_decks_list`, and note type ids from `anki_note_types_list`.
- **Fields must match exactly.** A note's `fields` must name every field of its note type and no others: read them with `anki_note_types_get` once per type. Stock Cloze's second field is `Back Extra`.
- **Add in batches that skip duplicates.** `anki_notes_create_batch` with `skip_duplicates: true` reports a card whose first field the deck already has as `duplicate`, with `duplicate_of` naming that note, instead of failing the batch; `add_cards.py` plans these. Without `skip_duplicates`, one duplicate fails the whole batch with `DUPLICATE_NOTE`, as `anki_notes_create` does for one card.
- **Every write takes an `idempotency_key`.** The scripts derive one from the content, so re-sending a planned call after a failure applies it at most once. Give one to any write you make by hand too. A key whose first try failed with `INTERNAL_ERROR` stays failed: re-sending it returns `"state": "outcome_unknown"` and does nothing. Then check whether the write landed (search for the note, or `anki_media_get` the file), and if it didn't, send it again with `-retry1` appended to the key.
- **`RESPONSE_TOO_LARGE`** means one page didn't fit the server's response limit: ask again with half the `limit`. The server already trims a page that would be too big to fewer items (the reply's `limit` says how many), so this only happens when a single note is too large.
- **Errors carry a `code`.** `MANUAL_CHANGE_REQUIRED` and `CONFIRMATION_DECLINED` are in `note-types.md`. On `AUTHENTICATION_FAILED`, `MEDIA_SYNC_FAILED`, `NETWORK_ERROR` or `SYNC_*`, stop and tell the user: the server needs fixing, not the cards. On `FULL_SYNC_REQUIRED`, stop too, and don't re-add anything: the write was saved on the server but not synced, because another device changed a note type's structure, and AnkiWeb and the server now each hold changes the other lacks. Tell the user the cards are on the server but not on AnkiWeb yet, and that resolving it means a full sync in one direction, which loses the other side's changes. That choice is theirs; never pick a direction.
- **A new server downloads its media first.** Until that finishes, the `anki_media_*` tools return `MEDIA_SYNC_IN_PROGRESS` (a write may first wait a few seconds for the download); deck, note and card tools work as usual. Don't retry the media call and don't stop the rest: say in one line that the server is still downloading media (the number before `↓` in `details.media_sync.added` is how many files it has so far), and store the file when the user says it's done (or when `anki_status` no longer reports `initial_media_sync_in_progress`).

The scripts named below are in this skill's `scripts/` directory; run each as `python3 -I <this skill dir>/scripts/<name>.py`, with no argument for its usage. They never reach Anki themselves: you make every Anki call, save each reply's JSON to its own scratch file, and pass the files in. The write scripts print the calls to make, in order, for the server you name with `--server local` or `--server remote`. Drafts go in a scratch JSON list of cards, `{"deck", "stage", "model", "fields", "tags"}`.

## Steps

1. **Read the charter** of the subject deck. Then restate what was just taught as a few one-point sentences, and draft cards so that each one tests exactly one of them, against the charter and the rules above. A point you can't state in one sentence needs splitting before it becomes a card. Before choosing shapes, measure the deck's format mix: search notes with `deck:"<subject>"`, save every page (on local, save `notes_info` for the ids found, 100 at a time; on remote, search with `include_fields: true` and save those pages), and run `format_mix.py <replies>...`. If its last line says the top format is over the target, follow "Vary the shape". On a large deck, the `total` of each search for `deck:"<subject>"` plus `tag:type::<kind>` gives the same answer with less copying.
2. **Check the deck** for overlap and prerequisites. Save the pages of a search for `deck:"<subject>"` (local: with `include_first_field: true`) and run `find_dupes.py <drafts.json> <replies>...`: it lists, for each draft, the deck's notes and the batch's earlier drafts worded most like it, across every note type; decide from those which drafts repeat a card or need a near-neighbor contrast. A score of 1.00 is the same first field, which Anki rejects as a duplicate. For prerequisites, search with `deck:"<subject>"` plus key terms. Search each term as a whole word with `w:term`, so a short stem doesn't match unrelated words, and include its other forms (`w:embedding or w:embeddings`), since `w:` doesn't match plurals or other inflections. For a word in a language deck, also search its dictionary form, because the deck may already hold another inflection of it. Drop drafts that repeat a card; write any missing prerequisite card first.
3. **Pick the stage**: the earliest stage subdeck that already teaches everything the card relies on. If no stage fits, propose a new one to the user instead of guessing.
4. **Lint** the drafts: `lint_cards.py <drafts.json> --prefix <charter's tag prefix>`, adding `--skip <checks>` when the charter's Conventions has a `Lint skip:` line. Fix every error and every warning, or say in your reply why a warning is wrong for that card.
5. **Add** with `add_cards.py plan <drafts.json> --server <server>` (remote also takes `--decks` and `--note-types`: saved `anki_decks_list` and `anki_note_types_list` replies). It refuses the batch on any lint error or missing stage, and prints the add calls in order: make each, saving each reply, error replies included. Then run `add_cards.py order <drafts.json> --server <server> <replies>...` with those replies in call order: it says which cards were added, which were duplicates and which failed, and prints the calls left (placing `"first"` cards, then the sync); make those too. Write each card's fields as follows:
   - `Basic`: `{"Front": ..., "Back": ...}`. Bold the key term with `<b>`. An optional context line goes at the end of Back: `<br /><br /><small><b>Why/Example:</b> one sentence</small>`.
   - `Cloze`: `{"Text": ..., "Back Extra": ""}`, or the second field's name in the collection if it differs.
   - Any other note type the charter names: fill its fields the way Conventions says ("Read a note type" lists them).
   - Tags: the charter's prefix (`<prefix>::<area>::<topic>`), `type::definition|contrast|application|formula`, and `src::<topic>` so a batch can be found together. Name the topic, never the project or session it came from: no client, module or dataset names in tags either.
   - **Order**: new cards are studied in the file's order, after those already queued. Put prerequisites first, and give a card `"first": true` when it must come before new cards the deck already holds.
6. **Report** in one line: how many were added, to which deck and stage, their fronts in short form, and whether the sync succeeded. On a sync conflict, tell the user and never pick a direction.

If a script can't run, or fails for a reason other than the cards (a tool changed, say), make the same calls by hand, following every step.

For a bulk restructure (re-reviewing or rebuilding a whole stage), write the stage as a plan file (`apply_stage.py`'s docstring has the format) and run `apply_stage.py plan <plan.json> --server <server>`, then make its calls; then `record` with the replies of its new-note calls, then `place` (twice: first for the card-id lookup, then with `--cards <reply>` for each page of it, plus `--sync`). It unsuspends every card of the notes it places, `keep` ones included, so say so in the plan when a kept note is suspended. If a run fails partway, fix the cause and plan again: recorded new notes are skipped, and remote writes carry idempotency keys. Show the user the plan for review first, as a file with the current text of every card it touches. Start a stage rebuild with its problem cards (search the stage's deck plus `(tag:leech or tag:marked)`): Anki tags cards the user keeps failing as leeches, and the user marks cards that confused them during review. Those usually break a rule here rather than the user's memory. In the plan, name the rule each rewrite fixes, and tag each rewritten leech `rescued` in its rewrite item's `tags` (a themed deck shows it a small badge). If a leech already follows every rule, add a mnemonic to its `Why/Example` line instead of rewording it.

Edits to existing cards ("Change a note's fields") keep review history. Never delete notes yourself: tag them `to-delete` and tell the user, who deletes them in the browser.

## When Anki can't be reached

The Anki tools are missing, or a call fails because the server can't be reached (connection refused, a timeout, Anki closed on local). Then stop writing, and:

1. Say so in one line that names the cause and that nothing was saved: "Couldn't reach Anki (connection refused). Nothing was saved."
2. Show the drafted cards in full, as the JSON list you'd add, so the conversation keeps them. For a charter, show its approved text. Save nothing anywhere else.
3. Keep teaching. Don't block the lesson on it.

When the user says Anki is back ("I've restarted Anki", "try again"), take the drafts from earlier in the conversation and run every step above on them: read the charter, check overlap and prerequisites, pick the stage, lint, then add. Those checks may never have run. A draft the user already approved stays approved, even in an Ask deck. Re-sending planned calls is safe: remote writes carry idempotency keys, and both servers report a card already added as a duplicate, which `order` lists. On remote, `order` also gives each duplicate's `duplicate_of` note: when that note is one the interrupted run added, report the card as added, not as a repeat.
