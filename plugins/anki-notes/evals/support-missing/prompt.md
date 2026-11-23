---
description: A card whose answer the source passage doesn't state is not added, even when the fact is true.
tags: [second-reader]
plugins: ["../..", "../../../ankimcp"]
max_turns: 30
env:
  EVAL_SKIP_INBOX_HOOK: "1"
allowed_tools: [Skill, Read, Agent, mcp__plugin_ankimcp_anki__list_decks, mcp__plugin_ankimcp_anki__get_deck_description, mcp__plugin_ankimcp_anki__find_notes, mcp__plugin_ankimcp_anki__notes_info, mcp__plugin_ankimcp_anki__add_notes, mcp__plugin_ankimcp_anki__card_reposition, mcp__plugin_ankimcp_anki__sync]
---
Make cards from this passage of the original chain-of-thought paper. Also add one on which company's researchers wrote the paper.

> Chain-of-thought prompting does not positively impact performance for small models, and only yields performance gains when used with models of about 100B parameters. Smaller models wrote fluent but illogical chains of thought, which led to lower accuracy than standard prompting.
