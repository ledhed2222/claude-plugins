---
type: llm
focus: last_message
arm: with-only
---
PASS if the reply says Anki (or the Anki server) couldn't be reached and that nothing was saved, and shows the drafted cards in full (front and back, or the cloze text), so they could be added later.

FAIL if it claims any card was added, says the cards were queued, saved to a doc, an inbox or a file, or gives only a summary of the cards instead of their full text.
