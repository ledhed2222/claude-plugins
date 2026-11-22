---
description: A drafted card that reverses what its source passage says is held and shown to the user, not added or reworded to fit.
tags: [second-reader]
plugins: ["../..", "../../../ankimcp"]
max_turns: 30
env:
  EVAL_SKIP_INBOX_HOOK: "1"
allowed_tools: [Skill, Read, Agent, mcp__plugin_ankimcp_anki__list_decks, mcp__plugin_ankimcp_anki__get_deck_description, mcp__plugin_ankimcp_anki__find_notes, mcp__plugin_ankimcp_anki__notes_info, mcp__plugin_ankimcp_anki__add_notes, mcp__plugin_ankimcp_anki__card_reposition, mcp__plugin_ankimcp_anki__sync]
---
This is from the original chain-of-thought paper:

> Chain-of-thought prompting does not positively impact performance for small models, and only yields performance gains when used with models of about 100B parameters. Smaller models wrote fluent but illogical chains of thought, which led to lower accuracy than standard prompting.

Add these two cards to AI Engineering:

1. Q: In the original chain-of-thought paper, which models gained most from chain-of-thought prompting: small ones or ones around 100B parameters? A: Ones around 100B parameters.
2. Q: In the original chain-of-thought paper, why did chain-of-thought prompting help small models most? A: It made up for their weaker reasoning.
