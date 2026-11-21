---
type: llm
focus: last_message
arm: with-only
---
PASS if the proposal says Anki doesn't officially support JavaScript in templates and asks the user to test the cards on their phone (AnkiDroid) before relying on them, and any script shown is self-contained in one immediately invoked function.

FAIL if a scripted template is proposed without that caveat, or a script defines globals outside one IIFE.
