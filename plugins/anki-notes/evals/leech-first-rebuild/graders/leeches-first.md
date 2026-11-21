---
type: llm
focus: last_message
arm: with-only
---
The stage has a leech card ("Precision vs recall?") and a marked card ("Why F1?").

PASS if the plan Claude shows deals with those two cards first, and for each rewrite it names the rule the old card broke (for example: two facts in one answer, a vague question, no named options).

FAIL if the plan doesn't single out the leech and marked cards, or rewrites them without saying which rule each fix addresses.
