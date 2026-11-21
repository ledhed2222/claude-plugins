---
type: llm
focus: trace
arm: with-only
---
Look at the cards in every add_notes call.

PASS if no card asks for the whole list ("name the four cells"). Each cell that gets a card is asked for on its own, by what it means; or all four sit in one Cloze note with one blank per cell, in a fixed order, where the visible cells don't give a blank away.

FAIL if any card asks for two or more cells in one answer, or asks for the set as a whole.
