---
type: llm
focus: reply
arm: with-only
---
Two facts were taught: the standard BLEU counts n-grams up to length 4 (arbitrary: it has to be remembered), and the brevity penalty exists because n-gram precision alone rewards very short outputs (it can be reasoned out).

PASS if the final reply offers one or more mnemonics for the n-gram length (or for BLEU's arbitrary details) for the user to pick from, and offers none for the brevity penalty.

FAIL if no mnemonic is offered for the n-gram length, or one is offered for the brevity penalty.
