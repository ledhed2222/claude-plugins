---
description: Cards for a themed deck use its own Basic or Cloze copy with the stock fields.
tags: [themes, routing]
plugins: ["../..", "../../../ankimcp"]
max_turns: 25
timeout_seconds: 900
env:
  EVAL_SKIP_INBOX_HOOK: "1"
allowed_tools: [Skill, mcp__plugin_ankimcp_anki__list_decks, mcp__plugin_ankimcp_anki__get_deck_description, mcp__plugin_ankimcp_anki__find_notes, mcp__plugin_ankimcp_anki__notes_info, mcp__plugin_ankimcp_anki__model_names, mcp__plugin_ankimcp_anki__model_field_names, mcp__plugin_ankimcp_anki__add_notes, mcp__plugin_ankimcp_anki__card_reposition, mcp__plugin_ankimcp_anki__sync]
---
Explain what precision measures for a binary classifier, and when you'd care about it more than recall.
