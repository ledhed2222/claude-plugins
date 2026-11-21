---
type: llm
focus: last_message
arm: with-only
---
Look at the note type templates Claude proposes, rendered in your head with its sample note.

PASS if no card's front shows the answer it asks for (the production front blanks or omits the target word), and the back of a card whose front hides the answer renders the fields itself instead of starting with {{FrontSide}} in a way that would still hide or duplicate the answer.

FAIL if a front template includes the field that holds its own answer unmasked, or no templates are shown.
