---
description: A Japanese deck keeps the system font (both fonts null) and still gets themed colors.
tags: [themes]
plugins: ["../..", "../../../ankimcp"]
max_turns: 40
timeout_seconds: 900
env:
  EVAL_SKIP_INBOX_HOOK: "1"
allowed_tools: [Skill, Read, AskUserQuestion, mcp__plugin_ankimcp_anki__list_decks, mcp__plugin_ankimcp_anki__get_deck_description, mcp__plugin_ankimcp_anki__model_names, mcp__plugin_ankimcp_anki__model_field_names, mcp__plugin_ankimcp_anki__model_templates]
---
We're setting up my new Japanese deck. You already drafted its charter and I approved it:

## Scope
Japanese for travel and conversation: kana, core kanji, polite speech.

Assumes: no Japanese.

## Out of scope
Business keigo.

## Adding
Ask.

## Stages
- `01 Kana`: hiragana and katakana.
- `02 Core kanji`: the kanji on signs, menus and stations.

## Conventions
- Basic and Cloze.
- Tags: `ja::<area>::<topic>`.

The sample note was Front "Japanese: how do you say 'Where is the station?'", Back "<b>駅はどこですか。</b>"

Second round: Ask mode, Basic and Cloze. For the feeling question: I'd like it to feel playful.
