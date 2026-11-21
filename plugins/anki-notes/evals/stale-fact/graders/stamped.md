---
type: llm
focus: trace
arm: with-only
---
Look at the cards in every add_notes call.

PASS if every card whose answer depends on a particular model, version, vendor, date or benchmark result says so in the question ("As of 2026, …", "For model X, …") and carries a src:: tag; or the cards test the durable principle (for example why long context doesn't replace retrieval) and leave model-specific numbers out.

FAIL if any card states a context-window size or another fast-changing figure without dating or attributing it in the question.
