---
type: llm
focus: trace
arm: with-only
---
Look at the cards in every add_notes call.

PASS if no card's front gives its answer away: no key word of the answer appears in the question, when options are named none is obviously the right one from its wording alone (for example "the clean set or the contaminated one?"), and no cloze leaves visible text that reveals what goes in the blank.

FAIL if any front can be answered from its own wording without knowing the topic.
