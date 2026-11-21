---
type: llm
focus: trace
arm: with-only
---
Look at the cards in every add_notes call.

PASS if the cards test decisions in the procedure (when to take a step, why it's needed, what goes wrong without it), and none asks for the order of steps or what comes next.

FAIL if any card asks for a step's position in the sequence, the next step, or a command or flag.
