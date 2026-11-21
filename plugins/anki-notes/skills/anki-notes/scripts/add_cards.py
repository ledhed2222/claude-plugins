# pyright: basic
"""Add a batch of drafted cards, then sync: SKILL.md steps 4-5 in one call.

Usage: python3 -I add_cards.py <cards.json|inbox.md> [--apply]   (dry run without --apply)

Takes what lint_cards.py takes: a JSON list of cards in the Anki inbox's format
  {"deck": ..., "stage": ..., "model": ..., "fields": {...}, "tags": [...], "first": true?}
or the inbox doc as Markdown, whose ```json blocks are numbered from 1.

Refuses the whole batch on any lint error, unparsed block or card without a
stage. Adds one add_notes call per (deck, stage, model), in batch order, so new
cards are studied in that order. "first": true moves a card ahead of every new
card already queued (a prerequisite for cards the user hasn't reached yet).
Never deletes or overwrites; duplicates the add-on rejects are reported.

The last line is JSON: {"added": [...], "duplicate": [...], "failed": {...}},
by card number. Delete from the inbox exactly the added and duplicate blocks.
"""
import asyncio
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))  # -I leaves this dir off sys.path
from ankimcp_client import AnkiError, Client  # noqa: E402
from lint_cards import lint, read_cards, text  # noqa: E402


def check(cards):
    errors = [f"#{n}: not valid JSON" for n, c in cards if "unparsed" in c]
    errors += [f"#{n}: {m}" for n, c in cards if "unparsed" not in c for s, m in lint(c) if s == "error"]
    errors += [f"#{n}: no stage chosen" for n, c in cards if "unparsed" not in c and not c.get("stage")]
    return errors


def groups(cards):
    out = {}
    for n, c in cards:
        out.setdefault((c["deck"], c["stage"], c["model"]), []).append((n, c))
    return out


async def add_cards(anki, cards, report):
    first = []
    # one group at a time: every call writes into the same collection
    for (deck, stage, model), group in groups(cards).items():
        r = await anki.call("add_notes", deck_name=f"{deck}::{stage}", model_name=model,
                            notes=[{"fields": c["fields"], "tags": c["tags"]} for _, c in group])
        for res in r["results"]:
            n, c = group[res["index"]]
            label = text(next(iter(c["fields"].values()), ""))[:60]
            if res["status"] == "created":
                report["added"].append(n)
                if c.get("first"):
                    first.append(res["note_id"])
                print(f"#{n} added to {deck}::{stage}: {label}")
            elif res.get("reason") == "duplicate":
                report["duplicate"].append(n)
                print(f"#{n} duplicate, not added: {label}")
            else:
                report["failed"][n] = res.get("error") or res["status"]
                print(f"#{n} FAILED ({report['failed'][n]}): {label}")
    if first:
        info = await anki.call("notes_info", notes=first, excerpt_chars=1)
        cards_first = [cid for nid in first for n in info["notes"] if n["noteId"] == nid for cid in sorted(n["cards"])]
        await anki.call("card_reposition", card_ids=cards_first, starting_from=0, shift_existing=True)


async def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    cards = await read_cards(sys.argv[1])
    errors = check(cards)
    if errors:
        sys.exit("\n".join(errors))
    print({f"{d}::{s} ({m})": len(v) for (d, s, m), v in groups(cards).items()})
    if "--apply" not in sys.argv:
        sys.exit("dry run ok; pass --apply")

    # filled as cards go in, so a failure partway still says which blocks were added
    report = {"added": [], "duplicate": [], "failed": {}}
    try:
        async with Client() as anki:
            await add_cards(anki, cards, report)
            if report["added"]:
                await anki.sync()
                print("sync: success")
    except AnkiError as e:
        sys.exit(str(e))
    finally:
        print(json.dumps(report))
    if report["failed"]:
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
