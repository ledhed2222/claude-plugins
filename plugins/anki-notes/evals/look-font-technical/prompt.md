---
description: An AI Engineering deck gets pairings with a sans body, at least one with a monospace label.
tags: [themes]
plugins: ["../..", "../../../ankimcp"]
max_turns: 40
timeout_seconds: 900
allowed_tools: [Skill, Read, AskUserQuestion, mcp__plugin_ankimcp_anki__list_decks, mcp__plugin_ankimcp_anki__get_deck_description, mcp__plugin_ankimcp_anki__model_names, mcp__plugin_ankimcp_anki__model_field_names, mcp__plugin_ankimcp_anki__model_templates]
---
We're setting up my new AI Engineering deck. You already drafted its charter and I approved it:

## Scope
General AI-engineering knowledge that carries over between projects: concepts, metrics, failure modes, eval techniques, design tradeoffs.

Assumes: working software engineer, basic statistics.

## Out of scope
Anything specific to one project. Commands, flags and config syntax.

## Adding
Automatic.

## Stages
- `01 Classification metrics`: confusion matrix, precision, recall, F1, thresholds.
- `02 Eval basics`: test sets, run-to-run variation, judging outputs.

## Conventions
- Tags: `aie::<area>::<topic>`.

The sample note was Front "Evals: you raise a classifier's threshold. Which goes up: precision or recall?", Back "<b>Precision.</b>"

Second round: Automatic, Basic and Cloze. For the feeling question: I'd like it to feel focused.
