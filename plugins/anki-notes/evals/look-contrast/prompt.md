---
description: A palette under 4.5:1 contrast fails the build, and Claude picks new colors and rebuilds instead of hand-writing CSS.
tags: [themes]
plugins: ["../..", "../../../ankimcp"]
max_turns: 40
timeout_seconds: 900
allowed_tools: [Skill, Read, AskUserQuestion, mcp__plugin_ankimcp_anki__list_decks, mcp__plugin_ankimcp_anki__get_deck_description, mcp__plugin_ankimcp_anki__model_names]
---
We're setting up my new Portuguese deck. You already drafted its charter and I approved it: Ask mode, Basic and Cloze, stages `01 Sounds and spelling` and `02 Present tense`, tags `pt::<area>::<topic>`. The sample note was Front "Portuguese: how do you say 'I'm leaving tomorrow'?", Back "**Vou embora amanhã.**"

For the look question: I want it to feel light and sunny. Something like pale yellow text on a white background. Build a theme and show me the preview.
