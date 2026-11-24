---
type: llm
focus: trace
arm: with-only
---
Look at the cards in every anki_notes_create_batch call.

PASS if every card's answer (Back, or each cloze blank) is one fact that can be recalled exactly: a word, a number, or one short clause, with any context in an optional Why/Example line.

FAIL if any card's answer packs two or more separate facts, a list, or more than one sentence of explanation.
