---
description: A new deck whose scope overlaps an existing one gets the overlap flagged and settled in both Out of scope sections.
tags: [charter]
plugins: ["../..", "../../../ankimcp"]
max_turns: 25
env:
  EVAL_SKIP_INBOX_HOOK: "1"
allowed_tools: [Skill, Read, mcp__plugin_ankimcp_anki__list_decks, mcp__plugin_ankimcp_anki__get_deck_description, mcp__plugin_ankimcp_anki__find_notes, mcp__plugin_ankimcp_anki__notes_info, mcp__plugin_ankimcp_anki__add_notes, mcp__plugin_ankimcp_anki__card_reposition, mcp__plugin_ankimcp_anki__sync, mcp__plugin_ankimcp_anki__create_deck, mcp__plugin_ankimcp_anki__update_deck_description, mcp__plugin_ankimcp_anki__model_names, mcp__plugin_ankimcp_anki__model_field_names, mcp__plugin_ankimcp_anki__model_templates, mcp__plugin_ankimcp_anki__create_model, mcp__plugin_ankimcp_anki__tag_add]
---
Set up an Anki deck for Python. I use it at work every day to build data pipelines and LLM eval tooling, I study on my phone, I know the basics, and I need to write it, not just read it. Show me the draft before creating anything.
