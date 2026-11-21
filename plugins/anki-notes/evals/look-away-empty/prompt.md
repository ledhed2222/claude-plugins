---
description: Emptying a queued charter with a theme creates its note types before saving the description.
tags: [themes, inbox]
plugins: ["../..", "../../../ankimcp"]
max_turns: 40
timeout_seconds: 900
env:
  EVAL_SKIP_INBOX_HOOK: "1"
allowed_tools: [Skill, Read, AskUserQuestion, mcp__plugin_ankimcp_anki__list_decks, mcp__plugin_ankimcp_anki__get_deck_description, mcp__plugin_ankimcp_anki__model_names, mcp__plugin_ankimcp_anki__model_field_names, mcp__plugin_ankimcp_anki__model_templates, mcp__plugin_ankimcp_anki__store_media_file, mcp__plugin_ankimcp_anki__create_model, mcp__plugin_ankimcp_anki__create_deck, mcp__plugin_ankimcp_anki__update_deck_description, mcp__plugin_ankimcp_anki__sync]
---
Anki is open now. Empty my Anki inbox. Here is everything under "Queued cards" in it:

```json
{"charter": {"deck": "Portuguese", "stages": ["01 Sounds and spelling", "02 Present tense"], "description": "## Scope\nEuropean Portuguese for living in Lisbon: everyday conversation, pronunciation, core grammar, high-frequency vocabulary.\n\nAssumes: fluent Spanish, no Portuguese.\n\n## Out of scope\nBrazilian-only usage. Business and legal Portuguese.\n\n## Adding\nAsk: offer cards and add them only after a yes.\n\n## Stages\n- `01 Sounds and spelling`: vowels, nasal sounds and how spelling maps to them.\n- `02 Present tense`: regular and common irregular verbs in the present.\n\n## Conventions\n- Note types: `Portuguese · Basic` and `Portuguese · Cloze` (the deck's theme).\n- Tags: `pt::<area>::<topic>`.", "theme": {"deck": "Portuguese", "mood": "warm, unhurried", "subsets": ["latin", "latin-ext"], "fonts": {"body": null, "accent": null}, "light": {"bg": "#FBF3E8", "text": "#3B2316", "accent": "#A24A26", "rule": "#E8CDB4"}, "night": {"bg": "#221A15", "text": "#F3E6D8", "accent": "#F0A07A", "rule": "#4A3A30"}, "motion": false}}}
```
