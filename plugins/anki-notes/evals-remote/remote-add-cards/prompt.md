---
description: On the remote server, teaching a concept adds one-fact cards in an anki_notes_create_batch that skips duplicates, with the stage deck's and note type's ids.
tags: [remote, smoke]
plugins: ["../..", "../../../ankimcp"]
max_turns: 25
allowed_tools: [Skill, mcp__plugin_ankimcp_anki__anki_decks_list, mcp__plugin_ankimcp_anki__anki_decks_get, mcp__plugin_ankimcp_anki__anki_notes_search, mcp__plugin_ankimcp_anki__anki_notes_get, mcp__plugin_ankimcp_anki__anki_note_types_list, mcp__plugin_ankimcp_anki__anki_note_types_get, mcp__plugin_ankimcp_anki__anki_notes_create, mcp__plugin_ankimcp_anki__anki_notes_create_batch, mcp__plugin_ankimcp_anki__anki_cards_search, mcp__plugin_ankimcp_anki__anki_cards_reposition, mcp__plugin_ankimcp_anki__anki_sync]
---
Can you explain precision and recall for a classifier? I get them mixed up.
