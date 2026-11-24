---
type: llm
focus: trace
arm: with-only
---
Claude was asked to cover a solera in depth, which makes several cards about one structure. Look at every add_notes call and count, for each image file (<img src="...">), how many notes use it.

PASS if no single image file is used on more than three notes.

FAIL if the same image appears on four or more notes.
