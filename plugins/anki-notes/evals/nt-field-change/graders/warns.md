---
type: llm
focus: last_message
arm: with-only
---
PASS if the reply says how many notes use the type, warns that adding a field makes the next sync a full one, asks the user to sync their other devices first, and asks before making the change.

FAIL if it says it already added the field, or leaves out the full-sync warning or the request to sync other devices first.
