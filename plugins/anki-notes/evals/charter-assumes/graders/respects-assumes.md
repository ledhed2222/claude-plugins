---
type: llm
focus: trace
arm: with-only
---
The deck's charter says it assumes basic statistics (mean, median, ratio, percentage), and the deck has no cards on precision or recall. Look at the cards in every add_notes call.

PASS if no card teaches mean, average, ratio or percentage as a concept of its own, and either cards introducing precision and recall are added before or with the F1 cards, or the reply says they're missing.

FAIL if a card teaches a basic statistics term, or F1 cards rely on precision and recall with no card or note about them.
