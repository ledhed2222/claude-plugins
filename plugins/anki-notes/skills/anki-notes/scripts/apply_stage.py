# pyright: basic
"""Plan the Anki calls that apply one stage plan (a bulk restructure of a stage).

Usage:
  python3 -I apply_stage.py plan <plan.json> --server local|remote [--decks <reply.json> --note-types <reply.json>]
  python3 -I apply_stage.py record <plan.json> --server local|remote <new-reply.json>...
  python3 -I apply_stage.py place <plan.json> --server local|remote [--decks <reply.json>] [--cards <reply.json>]... [--sync]

Plan: {"deck": "AI Engineering::02 Eval basics", "tags": ["src::..."],
       "items": [{"new": {"model": "Basic", "fields": {...}, "tags": [...]}},
                 {"keep": <note id>},
                 {"rewrite": <note id>, "fields": {...}, "tags": [...]},
                 {"delete": [<note id>, ...]}]}
Items are in study order. new/keep/rewrite notes are moved into the deck and
their new cards repositioned in that order. Every card of a new/keep/rewrite
note is also unsuspended, including keep notes the user had suspended. delete
only tags the notes "to-delete" for the user to remove. A rewrite's optional
tags are added to the note (say "rescued" for a rewritten leech).

Each command prints numbered calls and then one JSON list of {"tool", "args"}:
make them yourself, in order, saving each reply to its own file.
  plan    the writes: add each new note, rewrite fields and tags, tag deletes.
          Remote needs anki_decks_list and anki_note_types_list replies, and
          the deck to exist (it prints anki_decks_create first if not).
  record  after the plan's calls, with the replies of its new-note calls in
          order: writes their note ids to <plan>.applied.json. A later plan
          skips those items, so a run that failed partway can be planned again
          without adding them twice. Remote calls carry idempotency keys too.
  place   moves every new/keep/rewrite note's cards into the deck, unsuspends
          them and orders the new ones. It needs their card ids: without
          --cards it prints the lookup call (notes_info, or anki_cards_search
          on remote) to save first. On remote, page that search while
          has_more (the next offset is this one plus the reply's limit) and
          pass each page with its own --cards. --sync adds the sync at the end.
"""
import asyncio
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))  # -I leaves this dir off sys.path
from replies import LOCAL, REMOTE, SERVERS, ReplyError, call, card_ids, decks, key, note_type_names, print_plan, read  # noqa: E402

_KINDS = ("new", "keep", "rewrite", "delete")


def _check_items(items):
    for i, item in enumerate(items):
        kinds = [k for k in _KINDS if k in item]
        if len(kinds) != 1 or not set(item) <= {kinds[0], "fields", "tags"}:
            sys.exit(f"item {i}: needs exactly one of {', '.join(_KINDS)}: {item}")
        kind = kinds[0]
        if kind == "new" and not {"model", "fields"} <= set(item["new"]):
            sys.exit(f"item {i}: new needs model and fields")
        if kind == "rewrite" and not item.get("fields"):
            sys.exit(f"item {i}: rewrite needs fields")
        if kind == "delete" and not item["delete"]:
            sys.exit(f"item {i}: delete needs note ids")
        if ("fields" in item or "tags" in item) and kind != "rewrite":
            sys.exit(f"item {i}: fields and tags only go with rewrite")


def writes(plan, server, applied, deck_id=None, type_ids=None):
    """[(item index or None, call)]: index marks the new-note calls that record reads."""
    deck, base, out = plan["deck"], plan.get("tags", []), []
    for i, item in enumerate(plan["items"]):
        if "new" in item and str(i) not in applied:
            n = item["new"]
            tags = base + n.get("tags", [])
            if server == LOCAL:
                out.append((i, call("add_notes", deck_name=deck, model_name=n["model"], notes=[{"fields": n["fields"], "tags": tags}])))
            else:
                out.append((i, call("anki_notes_create", deck_id=deck_id, note_type_id=type_ids[n["model"]], fields=n["fields"],
                                    tags=tags, idempotency_key=key("stage-new", deck, i, n["fields"]))))
        elif "rewrite" in item:
            nid = item["rewrite"]
            if server == LOCAL:
                out.append((None, call("update_note_fields", id=nid, fields=item["fields"])))
                if item.get("tags"):
                    out.append((None, call("tag_add", note_ids=[nid], tags=" ".join(item["tags"]))))
            else:
                out.append((None, call("anki_notes_update_fields", note_id=nid, fields=item["fields"],
                                       idempotency_key=key("rewrite", nid, item["fields"]))))
                if item.get("tags"):
                    out.append((None, call("anki_notes_add_tags", note_ids=[nid], tags=item["tags"],
                                           idempotency_key=key("tags", nid, item["tags"]))))
        elif "delete" in item:
            ids = item["delete"]
            out.append((None, call("tag_add", note_ids=ids, tags="to-delete") if server == LOCAL else
                        call("anki_notes_add_tags", note_ids=ids, tags=["to-delete"], idempotency_key=key("delete", ids))))
    return out


def new_note_id(payload, server):
    if server == LOCAL:
        return payload["results"][0].get("note_id")
    return payload["result"]["note_id"]


def ordered_notes(plan, applied):
    """Note ids of new/keep/rewrite items, in study order; None for a new item not recorded yet."""
    out = []
    for i, item in enumerate(plan["items"]):
        if "new" in item:
            out.append(applied.get(str(i)))
        elif "keep" in item or "rewrite" in item:
            out.append(item.get("keep") or item.get("rewrite"))
    return out


def placing(plan, server, notes, cards_replies, deck_id=None):
    """The lookup call when card ids are missing, else the move, unsuspend and reposition calls."""
    if not cards_replies:
        if server == LOCAL:
            return [dict(call("notes_info", notes=notes, excerpt_chars=1), note="save this reply, then run place again with --cards <it>")]
        return [dict(call("anki_cards_search", query="nid:" + ",".join(map(str, notes)), limit=100),
                     note="page while has_more, save each page, then run place again with --cards <page> for each")]
    known = card_ids(cards_replies)
    missing = [n for n in notes if n not in known]
    if missing:
        sys.exit(f"no cards in the saved reply for notes {missing}")
    cards = [c for n in notes for c in known[n]]
    if server == LOCAL:
        # reposition skips cards that aren't new, so the reviewed ones keep their schedule
        return [call("card_change_deck", card_ids=cards, deck=plan["deck"]), call("card_unsuspend", card_ids=cards),
                call("card_reposition", card_ids=cards, starting_from=0)]
    return [call("anki_cards_change_deck", card_ids=cards, deck_id=deck_id, idempotency_key=key("move", deck_id, cards)),
            call("anki_cards_unsuspend", card_ids=cards, idempotency_key=key("unsuspend", cards)),
            call("anki_cards_reposition", card_ids=cards, starting_from=1, idempotency_key=key("order", cards))]


def _flag(args, name):
    return args[args.index(name) + 1] if name in args else None


def _flags(args, name):
    return [args[i + 1] for i, a in enumerate(args[:-1]) if a == name]


async def _read_text(path, missing):
    def _r():
        try:
            with open(path) as f:
                return json.load(f)
        except FileNotFoundError:
            return missing
    return await asyncio.to_thread(_r)


async def _write_text(path, text):
    def _w():
        with open(path, "w") as f:
            f.write(text)
    await asyncio.to_thread(_w)


async def main():
    args = sys.argv[1:]
    server = _flag(args, "--server")
    if len(args) < 2 or args[0] not in ("plan", "record", "place") or server not in SERVERS:
        sys.exit(__doc__)
    plan_path = args[1]
    applied_path = plan_path + ".applied.json"
    plan, applied = await asyncio.gather(_read_text(plan_path, None), _read_text(applied_path, {}))
    if plan is None:
        sys.exit(f"no plan at {plan_path}")
    _check_items(plan["items"])
    flagged = {a for f in ("--server", "--decks", "--note-types", "--cards") for v in _flags(args, f) for a in (f, v)}
    try:
        deck_ids = decks(await read([_flag(args, "--decks")])) if _flag(args, "--decks") else {}
        if args[0] == "plan":
            deck_id = type_ids = None
            if server == REMOTE:
                if not (_flag(args, "--decks") and _flag(args, "--note-types")):
                    sys.exit("remote needs --decks (anki_decks_list) and --note-types (anki_note_types_list) replies")
                if plan["deck"] not in deck_ids:
                    print_plan([call("anki_decks_create", name=plan["deck"], idempotency_key=key("deck", plan["deck"]))])
                    sys.exit("create the deck first, then save a new anki_decks_list reply and plan again")
                deck_id = deck_ids[plan["deck"]]
                type_ids = {v: k for k, v in note_type_names(await read([_flag(args, "--note-types")])).items()}
                missing = sorted({i["new"]["model"] for i in plan["items"] if "new" in i} - set(type_ids))
                if missing:
                    sys.exit(f"note types not in Anki: {', '.join(missing)}")
            calls = [] if server == REMOTE else [call("create_deck", deck_name=plan["deck"])]
            ws = writes(plan, server, applied, deck_id, type_ids)
            calls += [c for _, c in ws]
            counts = {k: sum(k in i for i in plan["items"]) for k in ("new", "keep", "rewrite")}
            counts["delete"] = sum(len(i.get("delete", [])) for i in plan["items"])
            counts["already added"] = len(applied)
            print(f"{plan['deck']}: {counts}")
            new_calls = [n + 1 for n, (i, _) in enumerate(ws, len(calls) - len(ws)) if i is not None]
            if new_calls:
                print(f"new-note calls (pass their replies to record, in order): {new_calls}")
            print_plan(calls)
            return
        if args[0] == "record":
            pending = [i for i, item in enumerate(plan["items"]) if "new" in item and str(i) not in applied]
            payloads = await read([a for a in args[2:] if a not in flagged])
            if len(payloads) > len(pending):
                sys.exit(f"{len(payloads)} replies for {len(pending)} new notes not yet recorded")
            for i, p in zip(pending, payloads):
                nid = new_note_id(p, server)
                if not nid:
                    sys.exit(f"item {i}: add failed: {p}")
                applied[str(i)] = nid
            await _write_text(applied_path, json.dumps(applied))
            print(f"recorded {len(payloads)} new notes in {applied_path}")
            return
        notes = ordered_notes(plan, applied)
        if None in notes:
            sys.exit("some new notes aren't recorded yet: run plan's calls and record first")
        if not notes:
            print(f"{plan['deck']}: only deletes; nothing to move")
            calls = []
        else:
            if server == REMOTE and plan["deck"] not in deck_ids:
                sys.exit("remote needs --decks (anki_decks_list) with the stage deck in it")
            cards_replies = await read(_flags(args, "--cards"))
            calls = placing(plan, server, notes, cards_replies, deck_ids.get(plan["deck"]))
    except ReplyError as e:
        sys.exit(f"a saved reply is an error: {e}")
    if "--sync" in args and not (calls and calls[0].get("note")):
        calls.append(dict(call("sync"), note="then poll sync(job_id) until it's not running; cancel a conflict")
                     if server == LOCAL else call("anki_sync"))
    print_plan(calls)


if __name__ == "__main__":
    asyncio.run(main())
