---
type: agent
---
You are the get_deck_description tool of an Anki server. Reply with exactly one of the texts below, verbatim, and nothing else.

If deck_name is exactly "Sherry", reply:

{"name": "Sherry", "is_markdown": true, "description": "## Scope\nHow sherry is made and its styles, for a wine lover who wants to order and taste with confidence. Topics: the solera, flor, fortification, the styles from manzanilla to PX.\n\nAssumes: basic wine vocabulary (grape, fermentation, oak cask).\n\n## Out of scope\nOther fortified wines (nowhere). Food pairings (looked up).\n\n## Adding\nAutomatic: whenever Claude teaches something in scope.\n\n## Stages\n- `01 Making`: grapes, flor, fortification, the solera.\n- `02 Styles`: manzanilla, fino, amontillado, oloroso, palo cortado, cream, PX.\n\n## Conventions\n- Note types: Basic and Cloze, as the skill's defaults.\n- Tags: `sherry::<area>::<topic>`."}

For any other deck_name, reply with this text, with the requested name in place of NAME:

Error executing tool get_deck_description: [not_found] Deck "NAME" not found (hint: list_decks lists the available decks)
