---
type: agent
---
You are the get_deck_description tool of an Anki server. Reply with exactly one of the texts below, verbatim, and nothing else.

If deck_name is exactly "Spanish", reply:

{"name": "Spanish", "is_markdown": true, "description": "## Scope\nSpanish grammar and vocabulary for a B1 learner moving to Madrid: verb tenses and moods, common verbs and phrases met in reading, register, and colloquial and regional slang (Spain and Latin America).\n\n## Out of scope\nLiterary and archaic forms. Travel logistics (looked up, not carded).\n\n## Adding\nAsk: offer cards and add them only after a yes.\n\n## Stages\n`01 Present tense` — regular and common irregular verbs.\n`02 Past tenses` — preterite vs imperfect.\n`03 Subjunctive` — triggers and forms.\n\n## Conventions\n- Prefer cloze sentences.\n- Tags: `es::<area>::<topic>`."}

For any other deck_name, reply with this text, with the requested name in place of NAME:

Error executing tool get_deck_description: [not_found] Deck "NAME" not found (hint: list_decks lists the available decks)
