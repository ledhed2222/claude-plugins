---
type: llm
focus: last_message
arm: with-only
---
Judge only the draft charter text in the reply, not the explanation around it.

PASS if the charter is roughly 250 words or fewer, doesn't restate general card-writing rules (one fact per card, self-contained fronts, no yes/no questions), starts any line that overrides a general rule with `Overrides:`, and gives every stage a one-line description of what it covers.

FAIL if it is clearly longer than about 300 words, repeats general card rules, or lists a stage with no description.
