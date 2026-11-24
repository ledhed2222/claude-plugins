# pyright: basic
"""Plan the Anki calls that add a batch of drafted cards (SKILL.md step 5).

Usage:
  python3 -I add_cards.py plan <cards.json> --server local
  python3 -I add_cards.py plan <cards.json> --server remote --decks <reply.json> --note-types <reply.json>
  python3 -I add_cards.py order <cards.json> --server local|remote <add-reply.json>... [--cards <reply.json>]

cards.json is a JSON list of cards:
  {"deck": ..., "stage": ..., "model": ..., "fields": {...}, "tags": [...], "first": true?}

plan refuses the whole batch on any lint error or card without a stage, then
prints the add calls in order, as numbered lines and then one JSON list of
{"tool", "args"}. Make each call yourself, in order, and save each reply to
its own file.
  local   one add_notes per (deck, stage, model), in batch order
  remote  one anki_notes_create_batch per 50 cards (the server's default
          ANKI_MAX_BATCH_SIZE), with skip_duplicates, so a card the deck already
          holds is reported rather than failing the batch. Deck and note-type ids
          come from saved anki_decks_list and anki_note_types_list replies. Each
          call has an idempotency_key derived from its cards, so a re-planned call
          after a failure applies at most once.

order reads the add replies, in the order the calls were made, and prints one
line per card (added, duplicate or failed), then the calls left: placing
"first": true cards ahead of every new card already queued, and the sync (on
remote, only when a receipt says "remote_synced": false: the server syncs each
write itself by default). On
local, placing needs the new notes' card ids: it asks for a notes_info call
first; save that reply and run order again with --cards <it>.

The last line of order is JSON: {"added": [...], "duplicate": [...], "failed": {...},
"duplicate_of": {...}, "calls": [...]}, by card number. duplicate_of (remote only) names
the note each duplicate repeats, so a card added by an earlier, interrupted run can be told
apart from one the deck already had.
"""
import asyncio
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))  # -I leaves this dir off sys.path
from lint_cards import lint, read_cards, text  # noqa: E402
from replies import LOCAL, REMOTE, SERVERS, ReplyError, call, card_ids, decks, key, note_type_names, print_plan, read  # noqa: E402

def check(cards):
    errors = [f"#{n}: {m}" for n, c in cards for s, m in lint(c) if s == "error"]
    errors += [f"#{n}: no stage chosen" for n, c in cards if not c.get("stage")]
    return errors


def _groups(cards):
    out = {}
    for n, c in cards:
        out.setdefault((c["deck"], c["stage"], c["model"]), []).append((n, c))
    return out


_BATCH = 50  # anki-sync-mcp's default ANKI_MAX_BATCH_SIZE


def _chunks(cards):
    return [cards[i:i + _BATCH] for i in range(0, len(cards), _BATCH)]


def plan(cards, server, deck_ids=None, type_ids=None):
    """The add calls, in batch order. remote: ([calls], [missing deck names], [missing note types])."""
    if server == LOCAL:
        return [call("add_notes", deck_name=f"{d}::{s}", model_name=m,
                     notes=[{"fields": c["fields"], "tags": c["tags"]} for _, c in g])
                for (d, s, m), g in _groups(cards).items()], [], []
    missing_decks, missing_types = [], []
    for _, c in cards:
        deck = f"{c['deck']}::{c['stage']}"
        if deck not in deck_ids and deck not in missing_decks:
            missing_decks.append(deck)
        if c["model"] not in type_ids and c["model"] not in missing_types:
            missing_types.append(c["model"])
    calls = []
    for chunk in _chunks(cards):
        notes = [{"deck_id": deck_ids.get(f"{c['deck']}::{c['stage']}"), "note_type_id": type_ids.get(c["model"]),
                  "fields": c["fields"], "tags": c["tags"]} for _, c in chunk]
        calls.append(call("anki_notes_create_batch", notes=notes, skip_duplicates=True, idempotency_key=key("batch", notes)))
    return calls, missing_decks, missing_types


def outcomes(cards, server, payloads):
    """Per card number: ("added", note id) | ("duplicate", note id it repeats or None) | ("failed", reason); payloads in call order."""
    out = {}
    if server == LOCAL:
        for group, p in zip(_groups(cards).values(), payloads):
            if isinstance(p, ReplyError):
                out.update({n: ("failed", str(p)) for n, _ in group})
                continue
            for res in p["results"]:
                n = group[res["index"]][0]
                if res["status"] == "created":
                    out[n] = ("added", res["note_id"])
                elif res.get("reason") == "duplicate":
                    out[n] = ("duplicate", None)
                else:
                    out[n] = ("failed", res.get("error") or res["status"])
        return out
    for chunk, p in zip(_chunks(cards), payloads):
        if isinstance(p, ReplyError):
            out.update({n: ("failed", str(p)) for n, _ in chunk})
            continue
        results = p["result"]["notes"]
        if len(results) != len(chunk):
            out.update({n: ("failed", f"the reply has {len(results)} results for {len(chunk)} cards") for n, _ in chunk})
            continue
        for (n, _), res in zip(chunk, results):
            if res.get("status") == "created":
                out[n] = ("added", res["note_id"])
            elif res.get("status") == "duplicate":
                out[n] = ("duplicate", res.get("duplicate_of"))
            else:
                out[n] = ("failed", str(res))
    return out


def follow_up(cards, server, results, payloads, cards_reply=None):
    """The calls left after adding: placing "first" cards, then the sync."""
    first = [results[n][1] for n, c in cards if c.get("first") and results.get(n, ("",))[0] == "added"]
    calls = []
    if first:
        known = card_ids([p for p in payloads if not isinstance(p, ReplyError)] + ([cards_reply] if cards_reply else []))
        if all(nid in known for nid in first):
            ids = [cid for nid in first for cid in known[nid]]
            if server == LOCAL:
                calls.append(call("card_reposition", card_ids=ids, starting_from=0, shift_existing=True))
            else:
                calls.append(call("anki_cards_reposition", card_ids=ids, starting_from=1, shift_existing=True,
                                  idempotency_key=key("first", ids)))
        else:
            return [dict(call("notes_info", notes=first, excerpt_chars=1),
                         note="save this reply, then run order again with --cards <it>")]
    if any(r[0] == "added" for r in results.values()):
        if server == LOCAL:
            calls.append(dict(call("sync"), note="then poll sync(job_id) until it's not running; cancel a conflict"))
        elif any(not p.get("remote_synced", True) for p in payloads if isinstance(p, dict)):
            # anki-sync-mcp syncs each write itself (ANKI_SYNC_ON_WRITE); only a receipt saying it didn't needs one
            calls.append(call("anki_sync"))
    return calls


def _flag(args, name):
    return args[args.index(name) + 1] if name in args else None


async def main():
    args = sys.argv[1:]
    server = _flag(args, "--server")
    if len(args) < 2 or args[0] not in ("plan", "order") or server not in SERVERS:
        sys.exit(__doc__)
    cards = await read_cards(args[1])
    errors = check(cards)
    if errors:
        sys.exit("\n".join(errors))
    flagged = {a for f in ("--server", "--decks", "--note-types", "--cards") if f in args for a in (f, _flag(args, f))}
    try:
        if args[0] == "plan":
            deck_ids = type_ids = None
            if server == REMOTE:
                if not (_flag(args, "--decks") and _flag(args, "--note-types")):
                    sys.exit("remote needs --decks (anki_decks_list) and --note-types (anki_note_types_list) replies")
                deck_ids = decks(await read([_flag(args, "--decks")]))
                type_ids = {v: k for k, v in note_type_names(await read([_flag(args, "--note-types")])).items()}
            calls, missing_decks, missing_types = plan(cards, server, deck_ids, type_ids)
            if missing_types:
                sys.exit(f"note types not in Anki: {', '.join(missing_types)}")
            if missing_decks:
                print_plan([call("anki_decks_create", name=d, idempotency_key=key("deck", d)) for d in missing_decks])
                sys.exit("create these stage decks first, then save a new anki_decks_list reply and plan again")
            print({f"{d}::{s} ({m})": len(v) for (d, s, m), v in _groups(cards).items()})
            print_plan(calls)
            return
        replies = [a for a in args[2:] if a not in flagged]
        payloads = await read(replies, errors=True)
        cards_reply = (await read([_flag(args, "--cards")]))[0] if _flag(args, "--cards") else None
    except ReplyError as e:
        sys.exit(f"a saved reply is an error: {e}")
    results = outcomes(cards, server, payloads)
    report = {"added": [], "duplicate": [], "failed": {}, "duplicate_of": {}}
    for n, c in cards:
        label = text(next(iter(c["fields"].values()), ""))[:60]
        status, detail = results.get(n, ("failed", "no reply saved for this card's call"))
        if status == "failed":
            report["failed"][n] = detail
            print(f"#{n} FAILED ({detail}): {label}")
        else:
            report[status].append(n)
            if status == "duplicate" and detail:
                report["duplicate_of"][n] = detail
            print(f"#{n} {'added to ' + c['deck'] + '::' + c['stage'] if status == 'added' else 'duplicate, not added'}: {label}")
    report["calls"] = follow_up(cards, server, results, payloads, cards_reply)
    print(json.dumps(report))
    if report["failed"]:
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
