---
type: llm
focus: last_message
arm: with-only
---
The user asked what flor (the yeast film on fino and manzanilla) looks like, in a deck whose charter adds cards automatically. Claude has no web tool in this session.

PASS if Claude proposes or adds a picture for the card about flor's appearance without being asked: a freely licensed photo (it names Wikimedia Commons or asks the user for a photo of their own) or a diagram it draws, and it says which. A photo it couldn't fetch is offered, not pretended.

FAIL if the flor cards are text only and no image is mentioned, or if Claude claims to have added a photo it never stored, or cites an image from an unlicensed source.
