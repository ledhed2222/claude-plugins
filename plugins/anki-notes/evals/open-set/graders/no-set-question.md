---
type: llm
focus: trace
arm: with-only
---
Look at the cards in every add_notes call.

PASS if no card asks for the whole set ("name three text-generation metrics") or for "an example of" a category. Each metric is carded by what it does or measures, or the metric is named and the card asks what it measures or what kind of metric it is.

FAIL if any card's answer is a list, or the question has many right answers because it asks for any member of the set.
