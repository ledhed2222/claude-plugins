---
type: llm
focus: last_message
arm: with-only
---
PASS if the reply gives one json block of the form {"charter": {"deck": ..., "stages": [...], "description": ..., "theme": {...}}} with the full approved charter text and the picked theme (not null), and says it couldn't be saved to Anki yet.

FAIL if the theme is missing or null, the charter is split across several blocks, or Claude claims it saved anything to Anki.
