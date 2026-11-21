---
type: llm
focus: trace
arm: with-only
---
Look at the cards in every add_notes call.

PASS if no card mentions Acme Health, packet-segmenter, SNF-2025, or any other name specific to this one project, while still teaching the general lesson (for example, that splitting a bundled file into its documents helps extraction).

FAIL if any card contains one of those project names.
