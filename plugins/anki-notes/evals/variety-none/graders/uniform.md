---
type: llm
focus: trace
arm: with-only
---
The Spanish charter says "Variety: none. Every card stays a Reconocimiento note." Look at every add_notes call.

PASS if every note added is a Reconocimiento note for «atardecer», filled as the charter says, and no Cloze, Basic, scenario or extra variant is added to vary the deck.

FAIL if any note uses another note type, or a second card in another shape is added for variety.
