---
description: After an outage, cards drafted earlier in the conversation are checked against the deck before they're added, and a card the deck already holds is reported, not added again.
tags: [remote, unreachable]
plugins: ["../.."]
max_turns: 25
allowed_tools: [Skill, mcp__plugin_anki-notes_anki__anki_decks_list, mcp__plugin_anki-notes_anki__anki_decks_get, mcp__plugin_anki-notes_anki__anki_notes_search, mcp__plugin_anki-notes_anki__anki_notes_get, mcp__plugin_anki-notes_anki__anki_note_types_list, mcp__plugin_anki-notes_anki__anki_note_types_get, mcp__plugin_anki-notes_anki__anki_notes_create, mcp__plugin_anki-notes_anki__anki_notes_create_batch, mcp__plugin_anki-notes_anki__anki_cards_search, mcp__plugin_anki-notes_anki__anki_cards_reposition, mcp__plugin_anki-notes_anki__anki_sync]
---
Earlier in this conversation you drafted these cards for my AI Engineering deck, and I approved them, but the Anki server was down so nothing was saved:

```json
[
 {
  "deck": "AI Engineering",
  "stage": null,
  "model": "Basic",
  "fields": {
   "Front": "What does a binary classifier do?",
   "Back": "Sorts each input into one of <b>two classes</b>."
  },
  "tags": [
   "aie::metrics::basics",
   "type::definition",
   "src::metrics"
  ]
 },
 {
  "deck": "AI Engineering",
  "stage": null,
  "model": "Basic",
  "fields": {
   "Front": "A spam filter flags a real email as spam. Which kind of error is this: a false positive or a false negative?",
   "Back": "<b>A false positive.</b>"
  },
  "tags": [
   "aie::metrics::errors",
   "type::application",
   "src::metrics"
  ]
 },
 {
  "deck": "AI Engineering",
  "stage": null,
  "model": "Basic",
  "fields": {
   "Front": "A classifier misses a fraudulent payment and lets it through. Which kind of error is this: a false positive or a false negative?",
   "Back": "<b>A false negative.</b>"
  },
  "tags": [
   "aie::metrics::errors",
   "type::application",
   "src::metrics"
  ]
 }
]
```

I've restarted the server. Add them now.
