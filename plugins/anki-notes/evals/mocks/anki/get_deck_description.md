---
type: agent
---
You are the get_deck_description tool of an Anki server. Reply with exactly one of the texts below, verbatim, and nothing else.

If deck_name is exactly "AI Engineering", reply:

{"name": "AI Engineering", "is_markdown": true, "description": "## Scope\nGeneral AI-engineering knowledge that carries over between projects: concepts, metrics, failure modes, eval techniques, design tradeoffs.\n\n## Out of scope\nAnything specific to one project (module, client, corpus or ticket names). Commands, flags and config syntax.\n\n## Adding\nAutomatic: whenever Claude teaches an AI-engineering concept.\n\n## Stages\n`01 Classification metrics` → `02 Eval basics` → `03 Prompting and generation` → `04 Retrieval and grounding` → `05 Security and safety`.\n\n## Conventions\n- No arithmetic drills: test what a metric means and when it matters, not the calculation.\n- Tags: `aie::<area>::<topic>`."}

If deck_name is exactly "Spanish", reply:

{"name": "Spanish", "is_markdown": true, "description": "## Scope\nSpanish grammar and vocabulary for a C1 learner.\n\n## Out of scope\nTravel logistics.\n\n## Adding\nAsk: offer cards and add them only after a yes.\n\n## Stages\n`01 Basics`.\n\n## Conventions\n- Prefer cloze sentences.\n- Tags: `es::<area>::<topic>`."}

For any other deck_name, reply with this text, with the requested name in place of NAME:

Error executing tool get_deck_description: [not_found] Deck "NAME" not found (hint: list_decks lists the available decks)
