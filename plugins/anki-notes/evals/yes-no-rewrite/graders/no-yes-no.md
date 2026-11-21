---
type: llm
focus: trace
arm: with-only
---
Look at the cards in every add_notes call.

PASS if no card's question can be answered with yes or no; each asks what, why, which or how.

FAIL if any card's question is a yes/no question (for example "Does temperature 0 make outputs identical?").
