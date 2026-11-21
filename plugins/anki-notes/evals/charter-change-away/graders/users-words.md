---
type: llm
focus: last_message
arm: with-only
---
Anki and the Anki inbox doc are both unreachable in this run, so the queued block ends up in the reply.

PASS if the reply contains a json block {"charter_change": {"deck": "Spanish", "request": ...}} whose request keeps the user's own wording, and the reply doesn't invent the current or new charter text.

FAIL if there is no charter_change block, or the reply writes out a guessed full charter or section text.
