---
description: Emptying the inbox saves a queued charter first, without re-asking, then adds its cards.
tags: [charter, inbox]
plugins: ["../..", "../../../ankimcp"]
max_turns: 40
env:
  EVAL_SKIP_INBOX_HOOK: "1"
allowed_tools: [Skill, Read, mcp__plugin_ankimcp_anki__list_decks, mcp__plugin_ankimcp_anki__get_deck_description, mcp__plugin_ankimcp_anki__find_notes, mcp__plugin_ankimcp_anki__notes_info, mcp__plugin_ankimcp_anki__add_notes, mcp__plugin_ankimcp_anki__card_reposition, mcp__plugin_ankimcp_anki__sync, mcp__plugin_ankimcp_anki__create_deck, mcp__plugin_ankimcp_anki__update_deck_description, mcp__plugin_ankimcp_anki__model_names, mcp__plugin_ankimcp_anki__model_field_names, mcp__plugin_ankimcp_anki__model_templates, mcp__plugin_ankimcp_anki__create_model, mcp__plugin_ankimcp_anki__tag_add]
---
Empty my Anki inbox. The docs tools aren't available here, so here's everything that's in it:

```json
{"charter": {"deck": "Spanish", "stages": ["01 Sounds and spelling", "02 Present tense", "03 Past tenses"], "description": "## Scope\nSpanish for living in Madrid: everyday grammar, common verbs, and words met in reading. In: verb tenses, ser vs estar, por vs para.\n\nAssumes: present and past tense forms.\n\n## Out of scope\nLatin American slang (nowhere). Travel logistics (looked up).\n\n## Adding\nAsk.\n\n## Stages\n`01 Sounds and spelling` — accents and stress.\n`02 Present tense` — irregular verbs, ser/estar and por/para.\n`03 Past tenses` — preterite vs imperfect.\n\n## Conventions\n- Prefer cloze sentences from my reading.\n- Tags: `es::<area>::<topic>`."}}
```

```json
{"deck": "Spanish", "stage": null, "model": "Cloze", "fields": {"Text": "La farmacia {{c1::está}} al final de la calle.", "Extra": "estar: location"}, "tags": ["es::grammar::ser-estar", "type::application"]}
```
