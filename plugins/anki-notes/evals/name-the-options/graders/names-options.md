---
type: llm
focus: trace
arm: with-only
---
Look at the cards in every add_notes call.

PASS if every card that contrasts two or three options names all of them in its own question or cloze text (for example "...: code or an LLM judge?"), so it works without any other card.

FAIL if a card asks "which kind?" or similar without naming the options, or depends on another card to know what the options are.
