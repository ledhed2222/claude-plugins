---
description: Helping with a task, as opposed to teaching a concept, makes no cards.
tags: [routing]
plugins: ["../..", "../../../ankimcp"]
max_turns: 25
env:
  EVAL_SKIP_INBOX_HOOK: "1"
allowed_tools: [Skill, mcp__plugin_ankimcp_anki__list_decks, mcp__plugin_ankimcp_anki__get_deck_description, mcp__plugin_ankimcp_anki__find_notes, mcp__plugin_ankimcp_anki__notes_info, mcp__plugin_ankimcp_anki__add_notes, mcp__plugin_ankimcp_anki__card_reposition, mcp__plugin_ankimcp_anki__sync]
---
My tmux status bar shows the time in UTC instead of my local time. What do I put in tmux.conf to fix it?
