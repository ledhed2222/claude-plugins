---
type: llm
focus: last_message
arm: with-only
---
The user already answered why, how, what they know, and understand-vs-produce.

PASS if, after the draft, Claude asks at most four follow-up questions, about things like Automatic vs Ask, a real note-type choice, or something the draft left open, and none of them asks again why the user is learning, how they study, what they know, or whether they need to understand or apply it.

FAIL if it asks more than four follow-ups or repeats any of those first-round questions.
