---
description: A procedure is carded at its decision points, not as a sequence of steps or commands.
tags: [formulation]
plugins: ["../..", "../../../ankimcp"]
max_turns: 25
env:
  EVAL_SKIP_INBOX_HOOK: "1"
allowed_tools: [Skill, Read, mcp__plugin_ankimcp_anki__list_decks, mcp__plugin_ankimcp_anki__get_deck_description, mcp__plugin_ankimcp_anki__find_notes, mcp__plugin_ankimcp_anki__notes_info, mcp__plugin_ankimcp_anki__add_notes, mcp__plugin_ankimcp_anki__card_reposition, mcp__plugin_ankimcp_anki__sync]
---
Walk me through setting up an eval run for a new prompt version, step by step. What do I do first, and why?
