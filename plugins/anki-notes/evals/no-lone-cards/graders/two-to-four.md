---
type: llm
focus: trace
arm: with-only
---
Look at the cards in every add_notes call. Count the cards about few-shot prompting itself (a Cloze note counts once per blank).

PASS if there are two, three or four, and they come from different angles (what it is, why it works, how it differs from a neighbor such as zero-shot or fine-tuning, when to use it).

FAIL if there is only one card about few-shot prompting, more than four, or several cards ask the same thing in different words.
