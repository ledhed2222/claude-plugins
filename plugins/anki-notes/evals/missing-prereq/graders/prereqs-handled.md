---
type: llm
focus: trace
arm: with-only
---
The deck the cards go into is empty: its find_notes search returned no cards, so it does not yet teach precision, recall or what a harmonic mean is.

PASS if the cards added include ones that introduce the concepts the F1 cards rely on (precision, recall, and the harmonic mean, or whichever of these the F1 cards use) before or alongside the F1 cards, OR if the reply clearly tells the user that those prerequisite cards are missing and offers to add them.

FAIL if F1 cards rely on precision, recall or the harmonic mean without any card introducing them and without flagging the gap.
