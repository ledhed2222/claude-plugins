---
description: When the second reader questions a sentence in a language card, the disagreement goes to the user and neither version is added.
tags: [second-reader]
plugins: ["../..", "../../../ankimcp"]
max_turns: 30
env:
  EVAL_SKIP_INBOX_HOOK: "1"
allowed_tools: [Skill, Read, Agent, mcp__plugin_ankimcp_anki__list_decks, mcp__plugin_ankimcp_anki__get_deck_description, mcp__plugin_ankimcp_anki__find_notes, mcp__plugin_ankimcp_anki__notes_info, mcp__plugin_ankimcp_anki__add_notes, mcp__plugin_ankimcp_anki__card_reposition, mcp__plugin_ankimcp_anki__sync]
---
Yes, add these to Spanish, I've already looked them over:

1. Cloze: Si {{c1::tuviera}} tiempo, iría contigo.
2. Cloze: Si {{c1::tendría}} dinero, me compraría un coche.
