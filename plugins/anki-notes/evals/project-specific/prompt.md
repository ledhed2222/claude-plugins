---
description: Lessons learned in a project become general cards without the project's names.
tags: [quality]
plugins: ["../..", "../../../ankimcp"]
max_turns: 25
allowed_tools: [Skill, mcp__plugin_ankimcp_anki__list_decks, mcp__plugin_ankimcp_anki__get_deck_description, mcp__plugin_ankimcp_anki__find_notes, mcp__plugin_ankimcp_anki__notes_info, mcp__plugin_ankimcp_anki__add_notes, mcp__plugin_ankimcp_anki__card_reposition, mcp__plugin_ankimcp_anki__sync]
---
At Acme Health we built a module called packet-segmenter that splits each faxed bundle in the SNF-2025 corpus into its separate documents before extraction runs. Explain why that splitting step matters for extraction accuracy.
