---
type: llm
focus: trace
arm: with-only
---
Look at the cards in every add_notes call.

PASS if every card's question has exactly one right answer: someone who knows the topic could not give a different answer that is also correct, because the question names the situation, the options, or the specific mechanism it asks about.

FAIL if any question (for example "What reduces hallucination in RAG?") admits several correct answers.
