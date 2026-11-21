---
type: llm
focus: last_message
arm: with-only
---
The deck has an `Reconocimiento` note for "darse cuenta", and the charter says to move a note to `Produccion` when the user keeps using the wrong word for it.

PASS if the reply recommends moving that note to production, drafts a `Pista` for it (a short English gloss such as "to realize, notice"), and tells the user to do the move with Change Note Type in Anki's browser.

FAIL if it doesn't suggest moving the note, creates a separate production note instead, or claims it changed the note type itself.
