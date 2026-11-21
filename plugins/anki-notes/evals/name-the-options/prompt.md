---
description: A two-option idea becomes a card that names both options in its question.
tags: [quality]
plugins: ["../..", "../../../ankimcp"]
max_turns: 25
env:
  EVAL_SKIP_INBOX_HOOK: "1"
allowed_tools: [Skill, mcp__plugin_ankimcp_anki__list_decks, mcp__plugin_ankimcp_anki__get_deck_description, mcp__plugin_ankimcp_anki__find_notes, mcp__plugin_ankimcp_anki__notes_info, mcp__plugin_ankimcp_anki__add_notes, mcp__plugin_ankimcp_anki__card_reposition, mcp__plugin_ankimcp_anki__sync]
---
When should an eval use a code-based check, and when an LLM judge?
