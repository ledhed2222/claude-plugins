---
type: llm
focus: last_message
arm: with-only
---
PASS if Claude builds the picked theme with motion off and asks whether to turn motion on (the answer fade and the rescued shimmer), leaving it off until the user says yes.

FAIL if it turns motion on, or never asks about it.
