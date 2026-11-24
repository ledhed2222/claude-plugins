---
description: Saving a picked theme creates both note types from models.json, then the deck, with the charter naming them.
tags: [themes]
plugins: ["../..", "../../../ankimcp"]
max_turns: 40
timeout_seconds: 900
allowed_tools: [Skill, Read, AskUserQuestion, mcp__plugin_ankimcp_anki__list_decks, mcp__plugin_ankimcp_anki__get_deck_description, mcp__plugin_ankimcp_anki__model_names, mcp__plugin_ankimcp_anki__model_field_names, mcp__plugin_ankimcp_anki__model_templates, mcp__plugin_ankimcp_anki__store_media_file, mcp__plugin_ankimcp_anki__create_model, mcp__plugin_ankimcp_anki__create_deck, mcp__plugin_ankimcp_anki__update_deck_description, mcp__plugin_ankimcp_anki__sync]
---
We're setting up my new Portuguese deck. You already drafted its charter and I approved it:

## Scope
European Portuguese for living in Lisbon: everyday conversation, pronunciation, core grammar, high-frequency vocabulary.

Assumes: fluent Spanish, no Portuguese.

## Out of scope
Brazilian-only usage. Business and legal Portuguese.

## Adding
Ask: offer cards and add them only after a yes.

## Stages
- `01 Sounds and spelling`: vowels, nasal sounds and how spelling maps to them.
- `02 Present tense`: regular and common irregular verbs in the present.

## Conventions
- Basic and Cloze.
- Tags: `pt::<area>::<topic>`.

The sample note was Front "Portuguese: how do you say 'I'm leaving tomorrow'?", Back "<b>Vou embora amanhã.</b>".

Second round: Ask mode, Basic and Cloze. You showed me three themes and I pick this one, with motion off. Build it and save the deck.

```json
{"deck": "Portuguese", "mood": "warm, unhurried", "subsets": ["latin", "latin-ext"],
 "fonts": {"body": null, "accent": null},
 "light": {"bg": "#FBF3E8", "text": "#3B2316", "accent": "#A24A26", "rule": "#E8CDB4"},
 "night": {"bg": "#221A15", "text": "#F3E6D8", "accent": "#F0A07A", "rule": "#4A3A30"}}
```
