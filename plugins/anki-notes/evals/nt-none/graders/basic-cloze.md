---
type: llm
focus: last_message
arm: with-only
---
PASS if the draft uses Basic and Cloze, and proposes no custom note type, or considers one and rejects it with a reason.

FAIL if it proposes a custom note type for this subject without a reason grounded in a repeated multi-part card shape.
