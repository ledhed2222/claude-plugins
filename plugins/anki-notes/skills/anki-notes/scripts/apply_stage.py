# pyright: basic
"""Apply one stage plan to Anki through the AnkiMCP add-on's HTTP server.

Usage: python3 -I apply_stage.py <plan.json> [--apply]   (dry run without --apply)

Plan: {"deck": "AI Engineering::02 Eval basics", "tags": ["src::..."],
       "items": [{"new": {"model": "Basic", "fields": {...}, "tags": [...]}},
                 {"keep": <note id>},
                 {"rewrite": <note id>, "fields": {...}},
                 {"delete": [<note id>, ...]}]}
Items are in study order. new/keep/rewrite notes are moved into the deck,
unsuspended, and their new cards repositioned in that order; delete only tags
the notes "to-delete" for the user to remove.
"""
import json
import sys
import time
import urllib.request

URL = "http://127.0.0.1:3141/"
_session = {"id": None, "n": 0}


def _post(body):
    headers = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream"}
    if _session["id"]:
        headers["Mcp-Session-Id"] = _session["id"]
    resp = urllib.request.urlopen(urllib.request.Request(URL, json.dumps(body).encode(), headers), timeout=300)
    _session["id"] = resp.headers.get("Mcp-Session-Id") or _session["id"]
    raw = resp.read().decode()
    for line in raw.splitlines():
        if line.startswith("data:"):
            raw = line[5:]
    return json.loads(raw) if raw.strip() else None


def call(tool, **args):
    if _session["id"] is None:
        _post({"jsonrpc": "2.0", "id": 0, "method": "initialize", "params": {
            "protocolVersion": "2025-06-18", "capabilities": {}, "clientInfo": {"name": "apply_stage", "version": "1"}}})
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


def main():
    plan = json.load(open(sys.argv[1]))
    apply = "--apply" in sys.argv
    deck, base_tags, items = plan["deck"], plan.get("tags", []), plan["items"]

    existing = [i.get("keep") or i.get("rewrite") for i in items if "keep" in i or "rewrite" in i]
    existing += [n for i in items for n in i.get("delete", [])]
    found = {n["noteId"] for n in call("notes_info", notes=existing, excerpt_chars=1)["notes"]} if existing else set()
    missing = set(existing) - found
    if missing:
        sys.exit(f"notes not found: {sorted(missing)}")
    counts = {k: sum(k in i for i in items) for k in ("new", "keep", "rewrite")}
    counts["delete"] = sum(len(i.get("delete", [])) for i in items)
    print(f"{deck}: {counts}")
    if not apply:
        sys.exit("dry run ok; pass --apply")

    call("create_deck", deck_name=deck)
    ordered = []
    for item in items:
        if "new" in item:
            n = item["new"]
            r = call("add_notes", deck_name=deck, model_name=n["model"],
                     notes=[{"fields": n["fields"], "tags": base_tags + n.get("tags", [])}])
            res = r["results"][0]
            if not res.get("note_id"):
                sys.exit(f"add failed: {res}")
            ordered.append(res["note_id"])
        elif "rewrite" in item:
            call("update_note_fields", id=item["rewrite"], fields=item["fields"])
            ordered.append(item["rewrite"])
        elif "keep" in item:
            ordered.append(item["keep"])
        else:
            call("tag_add", note_ids=item["delete"], tags="to-delete")

    info = {n["noteId"]: n for n in call("notes_info", notes=ordered, excerpt_chars=1)["notes"]}
    cards = [c for nid in ordered for c in sorted(info[nid]["cards"])]
    call("card_change_deck", card_ids=cards, deck=deck)
    call("card_unsuspend", card_ids=cards)
    # reposition skips cards that aren't new, so the reviewed ones keep their schedule
    r = call("card_reposition", card_ids=cards, starting_from=0)
    print(f"{len(ordered)} notes / {len(cards)} cards in {deck}; {r.get('repositioned')} new cards ordered")


def sync():
    job = call("sync")["job_id"]
    while True:
        s = call("sync", job_id=job)
        if s["status"] != "running":
            return s
        time.sleep(1)


if __name__ == "__main__":
    if sys.argv[1] == "--sync":
        s = sync()
        print("sync:", s["status"], s.get("error") or "")
    else:
        main()
