---
type: llm
focus: trace
arm: with-only
---
Look at the cards in every add_notes call.

PASS if every card asks about prompt injection itself (why instructions can't fix it, what makes it possible), and none asks what the post or its author said, argued or recommended.

FAIL if any card's question is about the article rather than the subject.
