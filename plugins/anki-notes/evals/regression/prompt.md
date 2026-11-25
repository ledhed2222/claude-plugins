---
description: Known-bad drafts are rewritten into the reviewed good shapes, and paired-relationship clozes are left alone.
tags: [formulation, smoke]
plugins: ["../.."]
max_turns: 25
allowed_tools: [Skill, Read, mcp__plugin_anki-notes_anki__list_decks, mcp__plugin_anki-notes_anki__get_deck_description, mcp__plugin_anki-notes_anki__find_notes, mcp__plugin_anki-notes_anki__notes_info, mcp__plugin_anki-notes_anki__add_notes, mcp__plugin_anki-notes_anki__card_reposition, mcp__plugin_anki-notes_anki__sync]
---
Here are some cards I drafted for my AI Engineering deck. Fix whatever's wrong with them and add them:

1. Q: What is pooled recall? A: A label-free technique where the union of several systems' outputs is treated as a pseudo answer key, so recall can be estimated without gold labels, at the cost of missing items no system found.
2. Q: Grounding vs attribution? A: Grounding means the output is supported by the source; attribution means pointing to which part of the source supports it.
3. Q: Which eval step is expensive and which is cheap: inference or scoring?
4. Q: A cache key for saved model outputs must include what, beyond model and settings?
5. Cloze: Raising a classifier's threshold makes precision {{c1::rise}} and recall {{c2::fall}}.
