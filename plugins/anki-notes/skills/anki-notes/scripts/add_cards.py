# pyright: basic
"""SKETCH, NOT RUN AGAINST ANKI. Add a batch of drafted cards in one call.

Usage: python3 -I add_cards.py <cards.json> [--apply]   (dry run without --apply)

Takes the same JSON list as the Anki inbox (and lint_cards.py):
  {"deck": ..., "stage": ..., "model": ..., "fields": {...}, "tags": [...]}
and does SKILL.md steps 4-6: lint, add per (deck, stage, model), keep the
batch's order within the stage, sync, stop on a sync conflict.

Intent for whoever picks this up:
- Run lint_cards.lint first and refuse to add on any error.
- Cards with "stage": null need a stage chosen by Claude first; refuse them.
- Never delete or overwrite; add_notes only. Duplicates the add-on rejects are
  reported, not forced.
- The same file should empty the inbox: Claude parses the doc's json blocks to a
  list, this script adds them, and Claude deletes the blocks whose notes were
  reported as added.
"""
import asyncio
import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))  # -I leaves this dir off sys.path
from ankimcp_client import AnkiError, Client, read_json  # noqa: E402
from lint_cards import lint  # noqa: E402


async def main():
    cards = await read_json(sys.argv[1])
    apply = "--apply" in sys.argv

    errors = [(i, m) for i, c in enumerate(cards, 1) for s, m in lint(c) if s == "error"]
    errors += [(i, "no stage chosen") for i, c in enumerate(cards, 1) if not c.get("stage")]
    if errors:
        sys.exit("\n".join(f"#{i}: {m}" for i, m in errors))

    groups = defaultdict(list)
    for c in cards:
        groups[(c["deck"], c["stage"], c["model"])].append(c)
    print({f"{d}::{s} ({m})": len(v) for (d, s, m), v in groups.items()})
    if not apply:
        sys.exit("dry run ok; pass --apply")

    try:
        async with Client() as anki:
            # one group at a time: every call writes into the same collection
            for (deck, stage, model), group in groups.items():
                r = await anki.call("add_notes", deck_name=f"{deck}::{stage}", model_name=model,
                                    notes=[{"fields": c["fields"], "tags": c["tags"]} for c in group])
                for c, res in zip(group, r["results"]):
                    print("added" if res.get("note_id") else f"NOT added ({res}):", list(c["fields"].values())[0][:60])
                # TODO: card_reposition for cards that belong before others in the stage.
            s = await anki.sync()
    except AnkiError as e:
        sys.exit(str(e))
    print("sync:", s["status"], s.get("error") or "")
    if s["status"] != "success":
        sys.exit("sync did not succeed; do not pick a direction on a conflict, tell the user")


if __name__ == "__main__":
    asyncio.run(main())
