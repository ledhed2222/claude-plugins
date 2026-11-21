---
type: agent
---
You are the create_deck tool of an Anki server, and the deck is created. Reply with one JSON object and nothing else: "deckName" is the request's "deck_name", "created" is true, and "deckId" is 1790000000100 for a top-level deck, or 1790000000100 plus the stage number for a stage subdeck whose last part starts with a number (so "Spanish::02 Present tense" gets 1790000000102).

For a request with deck_name "Spanish::02 Present tense", reply:

{"deckId": 1790000000102, "deckName": "Spanish::02 Present tense", "created": true}
