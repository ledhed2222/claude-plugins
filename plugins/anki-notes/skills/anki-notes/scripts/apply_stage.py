# pyright: basic
"""Apply one stage plan to Anki through the AnkiMCP add-on's HTTP server.

Usage:
  python3 -I apply_stage.py <plan.json>                  dry run: checks the plan and that its notes exist
  python3 -I apply_stage.py <plan.json> --apply [--sync]  apply it, then optionally sync to AnkiWeb
  python3 -I apply_stage.py --sync                       sync only

Plan: {"deck": "AI Engineering::02 Eval basics", "tags": ["src::..."],
       "items": [{"new": {"model": "Basic", "fields": {...}, "tags": [...]}},
                 {"keep": <note id>},
                 {"rewrite": <note id>, "fields": {...}},
                 {"delete": [<note id>, ...]}]}
Items are in study order. new/keep/rewrite notes are moved into the deck and
their new cards repositioned in that order. Every card of a new/keep/rewrite
note is also unsuspended, including keep notes the user had suspended. delete
only tags the notes "to-delete" for the user to remove.

Notes created by --apply are recorded in <plan>.applied.json, so a run that
fails partway can be re-run without adding them twice.
"""
import asyncio
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))  # -I leaves this dir off sys.path
from ankimcp_client import AnkiError, Client, read_json, write_text  # noqa: E402

KINDS = ("new", "keep", "rewrite", "delete")


def check_items(items):
    for i, item in enumerate(items):
        kinds = [k for k in KINDS if k in item]
        if len(kinds) != 1 or not set(item) <= {kinds[0], "fields"}:
            sys.exit(f"item {i}: needs exactly one of {', '.join(KINDS)}: {item}")
        kind = kinds[0]
        if kind == "new" and not {"model", "fields"} <= set(item["new"]):
            sys.exit(f"item {i}: new needs model and fields")
        if kind == "rewrite" and not item.get("fields"):
            sys.exit(f"item {i}: rewrite needs fields")
        if kind == "delete" and not item["delete"]:
            sys.exit(f"item {i}: delete needs note ids")
        if "fields" in item and kind != "rewrite":
            sys.exit(f"item {i}: fields only go with rewrite")


async def apply_plan(anki, plan_path, plan):
    deck, base_tags, items = plan["deck"], plan.get("tags", []), plan["items"]
    applied_path = plan_path + ".applied.json"
    applied, _ = await asyncio.gather(read_json(applied_path, missing={}), anki.call("create_deck", deck_name=deck))

    ordered = []
    for i, item in enumerate(items):
        if "new" in item:
            if str(i) in applied:
                ordered.append(applied[str(i)])
                continue
            n = item["new"]
            r = await anki.call("add_notes", deck_name=deck, model_name=n["model"],
                                notes=[{"fields": n["fields"], "tags": base_tags + n.get("tags", [])}])
            res = r["results"][0]
            if not res.get("note_id"):
                sys.exit(f"item {i}: add failed: {res}")
            applied[str(i)] = res["note_id"]
            await write_text(applied_path, json.dumps(applied))
            ordered.append(res["note_id"])
        elif "rewrite" in item:
            await anki.call("update_note_fields", id=item["rewrite"], fields=item["fields"])
            ordered.append(item["rewrite"])
        elif "keep" in item:
            ordered.append(item["keep"])
        else:
            await anki.call("tag_add", note_ids=item["delete"], tags="to-delete")

    if not ordered:
        print(f"{deck}: tagged notes to-delete; nothing to move")
        return
    info = {n["noteId"]: n for n in (await anki.call("notes_info", notes=ordered, excerpt_chars=1))["notes"]}
    cards = [c for nid in ordered for c in sorted(info[nid]["cards"])]
    await anki.call("card_change_deck", card_ids=cards, deck=deck)
    await anki.call("card_unsuspend", card_ids=cards)
    # reposition skips cards that aren't new, so the reviewed ones keep their schedule
    r = await anki.call("card_reposition", card_ids=cards, starting_from=0)
    print(f"{len(ordered)} notes / {len(cards)} cards in {deck}; {r.get('repositioned')} new cards ordered")


async def main(anki, args, flags):
    if not args:
        await anki.sync()
        print("sync: success")
        return

    plan_path = args[0]
    plan = await read_json(plan_path)
    items = plan["items"]
    check_items(items)
    existing = [i.get("keep") or i.get("rewrite") for i in items if "keep" in i or "rewrite" in i]
    existing += [n for i in items for n in i.get("delete", [])]
    found = {n["noteId"] for n in (await anki.call("notes_info", notes=existing, excerpt_chars=1))["notes"]} if existing else set()
    missing = set(existing) - found
    if missing:
        sys.exit(f"notes not found: {sorted(missing)}")
    counts = {k: sum(k in i for i in items) for k in ("new", "keep", "rewrite")}
    counts["delete"] = sum(len(i.get("delete", [])) for i in items)
    print(f"{plan['deck']}: {counts}")
    if "--apply" not in flags:
        sys.exit("dry run ok; pass --apply" + (" (--sync only runs after --apply)" if "--sync" in flags else ""))

    await apply_plan(anki, plan_path, plan)
    if "--sync" in flags:
        await anki.sync()
        print("sync: success")


async def run():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    flags = set(sys.argv[1:]) - set(args)
    if not args and "--sync" not in flags:
        sys.exit(__doc__)
    try:
        async with Client() as anki:
            await main(anki, args, flags)
    except AnkiError as e:
        sys.exit(str(e))


if __name__ == "__main__":
    asyncio.run(run())
