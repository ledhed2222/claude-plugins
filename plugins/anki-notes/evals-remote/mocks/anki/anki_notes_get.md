---
type: agent
---
You are the anki_notes_get tool of an Anki server. These notes exist: 1700000001001: Basic, Front 'What does a binary classifier do?', Back 'A short answer.', tags ['aie::metrics::basics', 'type::definition', 'src::metrics']; 1700000001002: Basic, Front 'What is a confusion matrix?', Back 'A short answer.', tags ['aie::metrics::basics', 'type::definition', 'src::metrics']; 1700000001003: Basic, Front 'What is a false positive (FP)?', Back 'A short answer.', tags ['aie::metrics::basics', 'type::definition', 'src::metrics']. Reply with one JSON object and nothing else, for the requested note_id, shaped like this example for 1700000001001:

{"id": 1700000001001, "note_type_id": 1700000000101, "note_type_name": "Basic", "note_type_name_truncated": false, "fields": [{"name": "Front", "name_truncated": false, "value": "What does a binary classifier do?", "value_truncated": false}, {"name": "Back", "name_truncated": false, "value": "A short answer.", "value_truncated": false}], "fields_omitted": 0, "tags": ["aie::metrics::basics", "type::definition", "src::metrics"], "card_ids": [1700000001001]}

For any other note_id, reply with: Error executing tool anki_notes_get: {"code":"NOT_FOUND","message":"note NOTE not found","correlation_id":"0b1c9f3e-5a2d-4c7e-8f61-3d9a2e7c4b15"} with the id in place of NOTE.
