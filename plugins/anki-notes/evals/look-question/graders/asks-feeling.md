---
type: llm
focus: trace
arm: with-only
---
Look at the questions Claude asks the user after drafting the charter (in an AskUserQuestion call or in its reply).

PASS if exactly one question is about the deck's look, it is marked optional or skippable, and it asks both how studying this feels and how the user would like it to feel.

FAIL if there is no such question, it is asked more than once, it is required, or it asks only one of the two (only the current feeling, or only the wanted one).
