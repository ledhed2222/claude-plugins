---
type: llm
focus: last_message
arm: with-only
---
Anki and the Anki inbox doc are both unreachable in this run, so queued blocks end up in the reply.

PASS if the reply contains a json block of the form {"charter": {"deck": "Spanish", ...}} with the approved charter text, it comes before any card block for the Spanish deck, and the reply says nothing was saved to Anki or the inbox.

FAIL if there is no charter block, a card block comes before it, or the reply claims the deck or cards were created.
