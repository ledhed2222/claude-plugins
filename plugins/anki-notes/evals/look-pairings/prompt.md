---
description: Mixing one option's palette with another's fonts gives a theme with A's colors and B's font families, previewed in the deck's language.
tags: [themes]
plugins: ["../..", "../../../ankimcp"]
max_turns: 40
timeout_seconds: 900
allowed_tools: [Skill, Read, AskUserQuestion, mcp__plugin_ankimcp_anki__list_decks, mcp__plugin_ankimcp_anki__get_deck_description, mcp__plugin_ankimcp_anki__model_names, mcp__plugin_ankimcp_anki__model_field_names, mcp__plugin_ankimcp_anki__model_templates]
---
We're setting up my new Spanish deck (charter approved; the sample note was Front "Spanish: how do you say 'I'd been waiting for hours'?", Back "<b>Llevaba horas esperando.</b>"). You showed me these two themes:

Option A, "Lora, warm paper":
```json
{"deck": "Spanish", "mood": "warm", "subsets": ["latin"], "fonts": {"body": {"family": "Lora", "italic": true}, "accent": null},
 "light": {"bg": "#FBF3E8", "text": "#3B2316", "accent": "#A24A26", "rule": "#E8CDB4"},
 "night": {"bg": "#221A15", "text": "#F3E6D8", "accent": "#F0A07A", "rule": "#4A3A30"}}
```

Option B, "Literata, quiet blue":
```json
{"deck": "Spanish", "mood": "calm", "subsets": ["latin"], "fonts": {"body": {"family": "Literata", "italic": true}, "accent": {"family": "Nunito"}},
 "light": {"bg": "#F7FAFC", "text": "#1A2733", "accent": "#1F6FB2", "rule": "#D5E1EA"},
 "night": {"bg": "#111820", "text": "#E6EEF4", "accent": "#7FB6E6", "rule": "#2A3743"}}
```

I like option A's colors but option B's fonts. Can you combine them?
