---
description: Away from Anki, an approved charter is queued as a charter block ahead of the cards for its deck.
tags: [charter, inbox]
plugins: ["../..", "../../../ankimcp"]
max_turns: 25
env:
  EVAL_SKIP_INBOX_HOOK: "1"
allowed_tools: [Skill, Read, mcp__plugin_ankimcp_anki__list_decks, mcp__plugin_ankimcp_anki__get_deck_description, mcp__plugin_ankimcp_anki__find_notes, mcp__plugin_ankimcp_anki__notes_info, mcp__plugin_ankimcp_anki__add_notes, mcp__plugin_ankimcp_anki__card_reposition, mcp__plugin_ankimcp_anki__sync]
---
Set up an Anki deck for Spanish. Why: I'm moving to Madrid next year. How: I read novels on my Kindle with lookups and review on my phone. What I know: I'm about B1 and comfortable with the present and past tenses. And I need both to understand Spanish and to speak it. I already approved this charter in another chat, use it as is:

## Scope
Spanish for living in Madrid: everyday grammar, common verbs, and words met in reading. In: verb tenses, ser vs estar, por vs para.

Assumes: present and past tense forms.

## Out of scope
Latin American slang (nowhere). Travel logistics (looked up).

## Adding
Ask.

## Stages
`01 Sounds and spelling` — accents and stress.
`02 Present tense` — irregular verbs, ser/estar and por/para.
`03 Past tenses` — preterite vs imperfect.

## Conventions
- Prefer cloze sentences from my reading.
- Tags: `es::<area>::<topic>`.

Then make two cards in it: ser vs estar for a location (estar), and por vs para for a deadline (para).
