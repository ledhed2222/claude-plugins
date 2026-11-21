---
type: llm
focus: last_message
arm: with-only
---
The collection has only Basic and Cloze.

PASS if the reply proposes a note type (or considers one and explains the choice) with one field per part of the card, the answer word stored in a single field that both card views use, a hint field on the production card that makes one answer right, and optional fields hidden when empty; shows a sample note as each of its cards would appear; and asks before creating it.

FAIL if a proposed type stores the answer twice, has no hint on the production card, has no sample note, or says the type was created.
