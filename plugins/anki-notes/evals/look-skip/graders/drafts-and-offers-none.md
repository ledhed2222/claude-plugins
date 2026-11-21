---
type: llm
focus: trace
arm: with-only
---
PASS if Claude drafts two or three themes based on the subject (Portuguese, Lisbon) even though the user skipped the feeling question, shows them, and offers "none" (keeping Anki's default look) as a choice.

FAIL if it drafts no themes, drafts only one, asks the feeling question again, or never offers "none".
