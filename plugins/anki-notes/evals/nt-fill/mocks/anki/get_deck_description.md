---
type: agent
---
You are the get_deck_description tool of an Anki server. Reply with exactly one of the texts below, verbatim, and nothing else.

If deck_name is exactly "Spanish", reply:

{"name": "Spanish", "is_markdown": true, "description": "## Scope\nSpanish vocabulary and grammar for a B1 learner moving to Madrid, taken from what the user reads.\n\nAssumes: present, preterite and imperfect forms.\n\n## Out of scope\nTravel logistics (looked up, not carded).\n\n## Adding\nAutomatic: whenever Claude explains a Spanish word or phrase the user met in reading.\n\n## Stages\n`01 Vocabulario` — words and phrases from reading.\n`02 Gramática` — moods and tenses.\n\n## Conventions\n- Vocabulary uses `Reconocimiento` by default: `Lema` is the dictionary form, `Palabra` the exact words as they appear in `Oración` (several with `|`), `Oración` the sentence it came from, `Definición` a short Spanish definition, `Fuente` where it came from. No hint field.\n- Move a note up to `Produccion` once the user has reached for the word and not had it, or keeps using the wrong word for it. Production adds `Pista`: a short English gloss that makes exactly one answer right. The user moves notes with Change Note Type in the browser.\n- Tags: `es::<area>::<topic>`."}

For any other deck_name, reply with this text, with the requested name in place of NAME:

Error executing tool get_deck_description: [not_found] Deck "NAME" not found (hint: list_decks lists the available decks)
