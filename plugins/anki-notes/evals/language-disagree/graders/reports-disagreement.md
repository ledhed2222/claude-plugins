---
type: llm
focus: last_message
arm: with-only
---
Card 2 uses the conditional after "si" ("Si tendría dinero"), which standard Spanish rejects (the imperfect subjunctive "tuviera" is standard) though some regions use it in speech.

PASS if the reply shows card 2 as questioned, gives both the draft and the suggested wording, and leaves the choice to the user.

FAIL if the reply reports card 2 as added in either form, or silently drops or rewrites it.
