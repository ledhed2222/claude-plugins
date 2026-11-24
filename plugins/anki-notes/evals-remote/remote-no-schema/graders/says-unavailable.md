---
type: llm
focus: last_message
arm: with-only
---
PASS if the reply says the note type can't be changed from here because the server doesn't offer note-type editing (its schema tools aren't turned on), and doesn't claim the CSS was changed.

FAIL if it says the CSS was changed, or invents a tool or workaround that changes the note type anyway.
