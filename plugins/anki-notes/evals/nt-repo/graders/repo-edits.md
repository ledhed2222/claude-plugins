---
type: llm
focus: last_message
arm: with-only
---
PASS if the reply proposes the change as edits to the templates in the user's anki-cards repo (and how to rebuild or apply it), not as a change made directly in Anki.

FAIL if it says it changed the note type in Anki, or proposes only an in-Anki change.
