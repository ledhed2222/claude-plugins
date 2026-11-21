---
type: llm
focus: trace
arm: with-only
---
Look at the cards in every add_notes call.

PASS if no card asks the learner to compute a value from numbers (for example "TP = 8, FP = 2: what is precision?").

FAIL if any card is an arithmetic drill. A card may still contain a formula, as long as it tests what the formula means rather than asking for a calculation.
