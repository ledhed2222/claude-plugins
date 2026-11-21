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
import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

URL = "http://127.0.0.1:3141/"
KINDS = ("new", "keep", "rewrite", "delete")
SYNC_POLLS = 120
_session = {"id": None, "n": 0}


def _post(body):
    headers = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream"}
    if _session["id"]:
        headers["Mcp-Session-Id"] = _session["id"]
    try:
        resp = urllib.request.urlopen(urllib.request.Request(URL, json.dumps(body).encode(), headers), timeout=300)
    except urllib.error.URLError as e:
        sys.exit(f"AnkiMCP add-on unreachable at {URL} (is Anki open with the add-on installed?): {e.reason}")
    _session["id"] = resp.headers.get("Mcp-Session-Id") or _session["id"]
    raw = resp.read().decode()
    for line in raw.splitlines():
        if line.startswith("data:"):
            raw = line[5:]
    return json.loads(raw) if raw.strip() else None


def call(tool, **args):
    if _session["id"] is None:
        r = _post({"jsonrpc": "2.0", "id": 0, "method": "initialize", "params": {
            "protocolVersion": "2025-06-18", "capabilities": {}, "clientInfo": {"name": "apply_stage", "version": "1"}}})
        if r is None or "error" in r:
            sys.exit(f"MCP initialize failed: {r and r.get('error')}")
        _post({"jsonrpc": "2.0", "method": "notifications/initialized"})
    _session["n"] += 1
    r = _post({"jsonrpc": "2.0", "id": _session["n"], "method": "tools/call", "params": {"name": tool, "arguments": args}})
    if r is None:
        sys.exit(f"{tool}: empty response")
    if "error" in r:
        sys.exit(f"{tool}: {r['error']}")
    res = r["result"]
    if res.get("isError"):
        sys.exit(f"{tool}: {res['content'][0]['text']}")
    return res.get("structuredContent") or json.loads(res["content"][0]["text"])


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


def apply_plan(plan_path, plan):
    deck, base_tags, items = plan["deck"], plan.get("tags", []), plan["items"]
    applied_path = plan_path.with_name(plan_path.name + ".applied.json")
    applied = json.loads(applied_path.read_text()) if applied_path.exists() else {}

    call("create_deck", deck_name=deck)
    ordered = []
    for i, item in enumerate(items):
        if "new" in item:
            if str(i) in applied:
                ordered.append(applied[str(i)])
                continue
            n = item["new"]
            r = call("add_notes", deck_name=deck, model_name=n["model"],
                     notes=[{"fields": n["fields"], "tags": base_tags + n.get("tags", [])}])
            res = r["results"][0]
            if not res.get("note_id"):
                sys.exit(f"item {i}: add failed: {res}")
            applied[str(i)] = res["note_id"]
            applied_path.write_text(json.dumps(applied))
            ordered.append(res["note_id"])
        elif "rewrite" in item:
            call("update_note_fields", id=item["rewrite"], fields=item["fields"])
            ordered.append(item["rewrite"])
        elif "keep" in item:
            ordered.append(item["keep"])
        else:
            call("tag_add", note_ids=item["delete"], tags="to-delete")

    if not ordered:
        print(f"{deck}: tagged notes to-delete; nothing to move")
        return
    info = {n["noteId"]: n for n in call("notes_info", notes=ordered, excerpt_chars=1)["notes"]}
    cards = [c for nid in ordered for c in sorted(info[nid]["cards"])]
    call("card_change_deck", card_ids=cards, deck=deck)
    call("card_unsuspend", card_ids=cards)
    # reposition skips cards that aren't new, so the reviewed ones keep their schedule
    r = call("card_reposition", card_ids=cards, starting_from=0)
    print(f"{len(ordered)} notes / {len(cards)} cards in {deck}; {r.get('repositioned')} new cards ordered")


def sync():
    job = call("sync")["job_id"]
    for _ in range(SYNC_POLLS):
        s = call("sync", job_id=job)
        if s["status"] == "conflict":
            # never pick a side: the wrong direction discards one side's changes
            call("sync", job_id=job, resolve="cancel")
            sys.exit("sync: AnkiWeb needs a full sync; cancelled. Resolve it in Anki, choosing which side to keep.")
        if s["status"] != "running":
            if s["status"] != "success":
                sys.exit(f"sync: {s['status']} {s.get('error') or ''}")
            print("sync: success")
            return
        time.sleep(1)
    sys.exit(f"sync: still running after {SYNC_POLLS} s; check Anki")


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    flags = set(sys.argv[1:]) - set(args)
    if not args:
        if "--sync" in flags:
            return sync()
        sys.exit(__doc__)

    plan_path = Path(args[0])
    plan = json.loads(plan_path.read_text())
    items = plan["items"]
    check_items(items)
    existing = [i.get("keep") or i.get("rewrite") for i in items if "keep" in i or "rewrite" in i]
    existing += [n for i in items for n in i.get("delete", [])]
    found = {n["noteId"] for n in call("notes_info", notes=existing, excerpt_chars=1)["notes"]} if existing else set()
    missing = set(existing) - found
    if missing:
        sys.exit(f"notes not found: {sorted(missing)}")
    counts = {k: sum(k in i for i in items) for k in ("new", "keep", "rewrite")}
    counts["delete"] = sum(len(i.get("delete", [])) for i in items)
    print(f"{plan['deck']}: {counts}")
    if "--apply" not in flags:
        sys.exit("dry run ok; pass --apply" + (" (--sync only runs after --apply)" if "--sync" in flags else ""))

    apply_plan(plan_path, plan)
    if "--sync" in flags:
        sync()


if __name__ == "__main__":
    main()
