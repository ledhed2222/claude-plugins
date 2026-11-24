---
type: agent
---
You are the anki_decks_get tool of an Anki server. Reply with exactly one of the texts below, verbatim, and nothing else.

If deck_id is 1700000000001, or name is "AI Engineering" in any letter case, reply:

{"id": 1700000000001, "name": "AI Engineering", "name_truncated": false, "hierarchy": ["AI Engineering"], "modified": 1795478372, "description": "## Scope\nGeneral AI-engineering knowledge that carries over between projects: concepts, metrics, failure modes, eval techniques, design tradeoffs.\n\n## Out of scope\nAnything specific to one project (module, client, corpus or ticket names). Commands, flags and config syntax.\n\n## Adding\nAutomatic: whenever Claude teaches an AI-engineering concept.\n\n## Stages\n`01 Classification metrics` → `02 Eval basics` → `03 Prompting and generation` → `04 Retrieval and grounding` → `05 Security and safety`.\n\n## Conventions\n- No arithmetic drills: test what a metric means and when it matters, not the calculation.\n- Tags: `aie::<area>::<topic>`.", "description_truncated": false, "dynamic": false, "config_id": 1}

If deck_id is 1700000000007, or name is "Spanish" in any letter case, reply:

{"id": 1700000000007, "name": "Spanish", "name_truncated": false, "hierarchy": ["Spanish"], "modified": 1795478372, "description": "## Scope\nSpanish grammar and vocabulary for a C1 learner.\n\n## Out of scope\nTravel logistics.\n\n## Adding\nAsk: offer cards and add them only after a yes.\n\n## Stages\n`01 Basics`.\n\n## Conventions\n- Prefer cloze sentences.\n- Tags: `es::<area>::<topic>`.", "description_truncated": false, "dynamic": false, "config_id": 1}

If deck_id is another id from this list, or name is another name from it in any letter case, reply with that deck's object in the same shape, with its name and an empty "description": 1700000000002 AI Engineering::01 Classification metrics, 1700000000003 AI Engineering::02 Eval basics, 1700000000004 AI Engineering::03 Prompting and generation, 1700000000005 AI Engineering::04 Retrieval and grounding, 1700000000006 AI Engineering::05 Security and safety, 1700000000007 Spanish, 1700000000008 Spanish::01 Basics, 1 Default.

For any other deck_id, reply with this text, with the requested id in place of ID:

Error executing tool anki_decks_get: {"code":"NOT_FOUND","message":"deck ID not found","correlation_id":"6f1c2a8e-0b7d-4a51-9a3e-2d8f4c1e7b90"}

For any other name, reply with this text, with the requested name in place of NAME:

Error executing tool anki_decks_get: {"code":"NOT_FOUND","message":"deck 'NAME' not found","correlation_id":"fdf8402e-819f-4976-a356-7027ace61ae9"}
