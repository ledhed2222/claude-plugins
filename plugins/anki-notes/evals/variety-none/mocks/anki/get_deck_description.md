---
type: agent
---
You are the get_deck_description tool of an Anki server. Reply with exactly one of the texts below, verbatim, and nothing else.

If deck_name is exactly "Spanish", reply:

{"name": "Spanish", "is_markdown": true, "description": "## Scope\nSpanish vocabulary for a C1 learner, from the user's own reading.\n\nAssumes: all A1-B2 grammar and core vocabulary.\n\n## Out of scope\nGrammar rules (looked up). Travel logistics (nowhere).\n\n## Adding\nAutomatic: whenever Claude explains a word the user met.\n\n## Stages\n- `01 Basics`: words met in reading.\n\n## Conventions\n- Note type: Reconocimiento for every word. Lema is the dictionary form, Palabra the form in the text, Oración the sentence it came from, Definición a short Spanish gloss, Fuente where it was read.\n- Variety: none. Every card stays a Reconocimiento note.\n- Tags: `es::vocab::<lemma>`.\n\nLint skip: answer-in-question"}

For any other deck_name, reply with this text, with the requested name in place of NAME:

Error executing tool get_deck_description: [not_found] Deck "NAME" not found (hint: list_decks lists the available decks)
