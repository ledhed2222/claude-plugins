---
type: llm
focus: trace
arm: with-only
---
The deck already holds a card on recall ("Of all the actual positives, what share does the classifier find?"). Look at the cards in every add_notes call.

PASS if the precision card's front states what sets precision apart from recall (that it is measured over the items the classifier flagged as positive, not over the actual positives), or a separate card tagged type::contrast names both precision and recall; and no card repeats the existing recall card.

FAIL if a precision front could be confused with the recall card in review, or a card duplicates the recall card.
