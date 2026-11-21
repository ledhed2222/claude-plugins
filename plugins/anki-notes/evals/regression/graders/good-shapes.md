---
type: llm
focus: trace
arm: with-only
---
Look at the cards in every add_notes call.

PASS if all of these hold: the pooled-recall card's answer is one short fact (for example what serves as the pseudo answer key); grounding vs attribution is a single paired Cloze note or split cards, not one card with a paragraph answer; the inference/scoring card asks which one costs more; the cache-key card is a concrete scenario with a one-clause answer (a version or hash of the prompt); and the threshold Cloze keeps both blanks in one note rather than being split or flagged as a giveaway.

FAIL if any rewritten card still has a multi-sentence answer, asks two things at once, or the threshold note was split into two notes.
