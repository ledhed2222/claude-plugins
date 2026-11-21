---
name: anki-notes
description: Turn something just taught into atomic Anki flashcards in the right subject deck. Use whenever the user says "add this to anki", "make a card", "flashcard this", and whenever you explain a concept the user would plausibly want to remember, in any subject (a language, a science, a technical field): the subject's deck charter then decides whether cards are added, offered or skipped. For AI engineering (evals, metrics, LLMs, grounding, extraction, RAG, agents, tooling), where cards are added automatically, including at the end of each step of a walkthrough. Also use it to set up a deck for a new subject, to write or change a deck's charter, and when told to empty the Anki inbox.
---

# Anki notes

Turn what was just taught into cards the user can actually study, then add them.

## Subjects and charters

Each subject is a top-level deck (`AI Engineering`, a language, ...), and its rules live in that deck's **charter**: its description in Anki, read with `get_deck_description`. The charter says what is in and out of scope, whether cards are added automatically or only proposed, the stage subdecks, and any card conventions for that subject. **Its rules add to the ones below and win where they conflict.**

- **Pick the subject** by reading the charters of the top-level decks (`list_decks`). If nothing fits, don't guess: propose a new deck and its charter.
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

## Last checks before adding

Run every draft through these. They come from the spaced-repetition literature rather than from the user's reviews of real cards, so the rules above win if the two ever disagree.

- **Make it take effort.** No yes/no questions: rewrite them as what, why or which. The front must not hint at its answer: no option that is obviously the right one, no word from the answer in the question, no cloze whose visible text gives the blank away. Paired relationships like the threshold example above are the exception, since recalling both halves together is the point.
- **Lists: one item per card.** Never ask for a whole set ("Name the four…"); card each member that matters by what it does, not just its name. For a short list whose order matters, write one Cloze note with a blank per item, in the same order every time; if the items left visible give a blank away, use separate notes. Never ask for "an example of X", which has many right answers: turn it around, name the example and ask what it's an example of. For a procedure, card the decision points (when to take a step, and why), not the sequence of steps.
- **Separate near neighbors.** When step 2 turns up a card on a similar concept (precision next to recall, few-shot next to fine-tuning), the two will get confused in review. Put the distinguishing feature in the new card's front, or add a `type::contrast` card that names both.
- **Stamp what can go stale.** If the answer depends on a date, a model or library version, a vendor, a benchmark result or a single paper, say so in the question ("As of 2026, …", "In the original RAG paper, …") and tag the source. Better still, card the durable principle behind it and leave the number out. Naming a source is fine when the claim is that source's own; never ask what an article or session said ("what does the post argue about…"), ask about the subject itself.

## Steps

Cards are only written to Anki from Claude Code, through the `anki` MCP server of the `ankimcp@ledhed2222` plugin, which talks to the AnkiMCP add-on (AnkiWeb code `124672614`) inside a running Anki. When those tools aren't available (another Claude app, or Anki is closed), queue the cards instead: see "The Anki inbox" below.

1. **Read the charter** of the subject deck. Then restate what was just taught as a few one-point sentences, and draft cards so that each one tests exactly one of them, against the charter and the rules above. A point you can't state in one sentence needs splitting before it becomes a card.
2. **Check the deck** for overlap and prerequisites: `find_notes` with `deck:"<subject>"` plus key terms, `include_first_field: true`. Search each term as a whole word with `w:term`, so a short stem doesn't match unrelated words, and include its other forms (`w:embedding or w:embeddings`), since `w:` doesn't match plurals or other inflections. Search every note type in the deck, since the same idea may sit in an older note type than the one you're writing to. For a word in a language deck, also search its dictionary form, because the deck may already hold another inflection of it. Drop drafts that repeat a card; write any missing prerequisite card first.
3. **Pick the stage**: the earliest stage subdeck that already teaches everything the card relies on. If no stage fits, propose a new one to the user instead of guessing.
4. **Add** with `add_notes`, one call per stage and note type.
   - `Basic`: `{"Front": ..., "Back": ...}`. Bold the key term with `<b>`. An optional context line goes at the end of Back: `<br><br><small><b>Why/Example:</b> one sentence</small>`.
   - `Cloze`: `{"Text": ..., "Extra": ""}`.
   - Any other note type the charter names: fill its fields the way Conventions says (`model_field_names` lists them).
   - Tags: the charter's prefix (`<prefix>::<area>::<topic>`), `type::definition|contrast|application|formula`, and `src::<topic>` so a batch can be found together. Name the topic, never the project or session it came from: no client, module or dataset names in tags either.
5. **Order** them: new cards land at the end of the queue, so if a card belongs before others in its stage, move it with `card_reposition`.
6. **Sync**: `sync()`, then poll `sync(job_id)` until it reports `success`. If it ends in `conflict`, never pick a direction yourself; cancel and tell the user.
7. **Report** in one line: how many were added, to which deck and stage, their fronts in short form, and whether the sync succeeded.

For a bulk restructure (re-reviewing or rebuilding a whole stage), write the stage as a plan file and run `python3 -I <this skill dir>/scripts/apply_stage.py <plan.json>` (a dry run), then again with `--apply --sync`. Its docstring has the plan format. It unsuspends every card of the notes it places, `keep` ones included, so say so in the plan when a kept note is suspended. If a run fails partway, fix the cause and re-run the same command: notes it already added are recorded beside the plan and not added twice. Show the user the plan for review first, as a file with the current text of every card it touches. Start a stage rebuild with its problem cards (`find_notes` with the stage's deck plus `(tag:leech or tag:marked)`): Anki tags cards the user keeps failing as leeches, and the user marks cards that confused them during review. Those usually break a rule here rather than the user's memory. In the plan, name the rule each rewrite fixes. If a leech already follows every rule, add a mnemonic to its `Why/Example` line instead of rewording it.

Edits to existing cards (`update_note_fields`) keep review history. Never delete notes yourself: tag them `to-delete` with `tag_add` and tell the user, who deletes them in the browser.

## The Anki inbox

A Claude Docs doc titled **Anki inbox** queues cards drafted where Anki can't be reached. Find it in the user's artifacts by that title; if there is none, create it with that title, one line saying what it is for, and a `## Queued cards` heading. Use the docs tools as their guide says.

**Queue** when the Anki tools are missing or fail. Draft each card exactly as you would add it, then append one ```json code block per card to the end of the doc:

```json
{"deck": "AI Engineering", "stage": "02 Eval basics", "model": "Basic", "fields": {"Front": "...", "Back": "..."}, "tags": ["..."]}
```

Leave `stage` null if you can't tell; it is decided when the card is added. Without the deck's charter you can't check overlap or prerequisites, so only queue what clearly passes the rules above, and only in a subject the user has a deck for (or asked for). Report in one line: "Queued 2 cards in the Anki inbox." If the doc can't be reached either, give the drafts in chat and say they weren't saved anywhere.

**Empty the inbox** when the Anki tools work: in Claude Code, a session-start hook says when Anki is open. Read the doc and take each json code block under "Queued cards". Handle `charter` and `charter_change` blocks first, as `charters.md` says. Add each card through the normal steps above, which are the overlap, prerequisite and stage checks the queuing session couldn't do. A queued card was already approved when it was queued, so add it without the Ask offer, even in an Ask deck. Delete each card's code block once the card is added, or once you've dropped it as a duplicate, and each charter block once it is saved or applied; leave anything you couldn't parse and say so. Then sync and report in one line what was added, dropped, and left queued.

If neither Anki nor the inbox is reachable, say so in one line and keep teaching. Don't block the lesson on it.
