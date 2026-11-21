---
type: llm
focus: last_message
arm: with-only
---
PASS if the reply asks, as a numbered list in one message, why the user is learning Spanish, how they plan to study it, what they already know, and whether they need to understand or produce it, each with a few concrete options, and doesn't draft a charter yet.

FAIL if any of the four questions is missing, they aren't a numbered list with options, or a charter is drafted before the answers.
