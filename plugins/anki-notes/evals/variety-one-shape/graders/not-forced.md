---
type: llm
focus: trace
arm: with-only
---
The deck holds 200 notes, 190 of them Cloze formula cards, and the user asked for the CER formula. Look at the cards in every add_notes call.

PASS if the formula itself is carded as a Cloze (CER = character edit distance ÷ reference length, or the same with substitutions, deletions and insertions), whatever other cards come with it.

FAIL if the formula is turned into another shape only to vary the deck (a scenario or Basic card that asks for the formula less directly, a calculation drill), or isn't carded at all.
