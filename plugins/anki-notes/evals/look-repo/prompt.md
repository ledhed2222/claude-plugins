---
description: Theming a deck whose note types live in a repo proposes a change to the repo's stylesheet, not new or restyled note types.
tags: [themes]
plugins: ["../..", "../../../ankimcp"]
max_turns: 40
timeout_seconds: 900
env:
  EVAL_SKIP_INBOX_HOOK: "1"
allowed_tools: [Skill, Read, AskUserQuestion, mcp__plugin_ankimcp_anki__list_decks, mcp__plugin_ankimcp_anki__get_deck_description, mcp__plugin_ankimcp_anki__model_names, mcp__plugin_ankimcp_anki__model_field_names, mcp__plugin_ankimcp_anki__model_templates, mcp__plugin_ankimcp_anki__model_styling, mcp__plugin_ankimcp_anki__create_model, mcp__plugin_ankimcp_anki__update_model_styling]
---
Give my Spanish deck a theme. I'd like it to feel like a sunny plaza.
