---
type: llm
focus: trace
arm: with-only
---
The user's diagram has the title "Precision-Recall curve" and axes labeled Precision and Recall, and they asked for a card with it on the front asking what kind of curve it is. Look at the reply and at every add_notes and store_media_file call.

PASS if no card shows the labeled diagram on its front with that question: the reply says the labels give the answer away, and either the diagram is stored and used without the title and axis labels, or it moves to the back, or the card waits for an unlabeled version.

FAIL if a card's front shows the diagram with its title or axis labels and asks what the curve is, or the reply doesn't mention that the labels give the answer away.
