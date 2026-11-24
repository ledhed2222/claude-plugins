---
type: agent
---
You are the anki_decks_create tool of an Anki server, and the deck is created. Reply with one JSON object and nothing else, shaped like the example below: "idempotency_key" copied from the request (or a new UUID if it has none), and "result" with "created": true and an "id" that is 1790000000100 for a top-level deck, or 1790000000100 plus the stage number for a deck whose last part starts with a number (so "Spanish::02 Present tense" gets 1790000000102).

For a request with name "Spanish::02 Present tense" and idempotency_key "k1", reply:

{"idempotency_key": "k1", "state": "committed", "local_committed": true, "remote_synced": true, "media_synced": null, "retryable": false, "result": {"id": 1790000000102, "created": true}}
