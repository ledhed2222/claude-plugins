---
type: llm
focus: trace
arm: with-only
---
Look at the cards in every add_notes call.

PASS if each card tests exactly one point (what is cached, why the prefix must match exactly, the latency benefit, the cost benefit, what invalidates the cache), and no card's answer combines two of them.

FAIL if any card's answer covers two or more of those points, or packs a list.
