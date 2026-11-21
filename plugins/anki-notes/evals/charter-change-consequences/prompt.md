---
description: Narrowing a charter's scope reports how many cards fall out and offers to tag them, without tagging first.
tags: [charter]
plugins: ["../..", "../../../ankimcp"]
max_turns: 25
env:
  EVAL_SKIP_INBOX_HOOK: "1"
allowed_tools: [Skill, Read, mcp__plugin_ankimcp_anki__list_decks, mcp__plugin_ankimcp_anki__get_deck_description, mcp__plugin_ankimcp_anki__find_notes, mcp__plugin_ankimcp_anki__notes_info, mcp__plugin_ankimcp_anki__add_notes, mcp__plugin_ankimcp_anki__card_reposition, mcp__plugin_ankimcp_anki__sync, mcp__plugin_ankimcp_anki__create_deck, mcp__plugin_ankimcp_anki__update_deck_description, mcp__plugin_ankimcp_anki__model_names, mcp__plugin_ankimcp_anki__model_field_names, mcp__plugin_ankimcp_anki__model_templates, mcp__plugin_ankimcp_anki__create_model, mcp__plugin_ankimcp_anki__tag_add]
---
Narrow my Spanish deck to grammar only. No more vocabulary cards.
