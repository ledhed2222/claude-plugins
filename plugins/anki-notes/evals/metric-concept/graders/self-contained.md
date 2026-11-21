---
type: llm
focus: trace
arm: with-only
---
Look at the cards in every add_notes call.

PASS if every card makes sense on its own, shuffled among hundreds of others months later: each term it relies on is either standard in the field or defined in the card, and the question names its options when there are only two or three.

FAIL if any card relies on wording or context from the conversation or from another card (for example "which kind?" or "the example above"), or is a telegraphic fragment rather than a complete question.
