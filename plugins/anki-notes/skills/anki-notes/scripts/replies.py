# pyright: basic
"""Read saved Anki tool replies from either server, and build tool calls for it.

The scripts never reach Anki themselves: Claude makes every call through the
connected `anki` MCP server and saves each reply's JSON to a scratch file. Two
servers are supported, told apart by their tool names:

  local   the AnkiMCP add-on inside Anki Desktop (list_decks, find_notes, ...)
  remote  anki-sync-mcp (anki_decks_list, anki_notes_search, ...)

Standard library only (Python 3.9+), so it runs in any sandbox.
"""
import asyncio
import hashlib
import json

LOCAL, REMOTE = "local", "remote"
SERVERS = (LOCAL, REMOTE)


class ReplyError(Exception):
    pass


def error_code(error):
    """The remote server's error code ("DUPLICATE_NOTE", "MEDIA_SYNC_IN_PROGRESS", ...) and details, or (None, {})."""
    text = str(error)
    start = text.find("{")
    try:
        body = json.loads(text[start:]) if start >= 0 else {}
    except ValueError:
        return None, {}
    return (body.get("code"), body.get("details") or {}) if isinstance(body, dict) else (None, {})


def unwrap(obj):
    """The payload of a saved reply: the bare JSON, an MCP tool result, or a JSON-RPC response."""
    if isinstance(obj, dict) and "result" in obj and "jsonrpc" in obj:
        obj = obj["result"]
    if isinstance(obj, dict) and ("content" in obj or "structuredContent" in obj) and set(obj) <= {
            "content", "structuredContent", "isError", "_meta"}:
        text = (obj.get("content") or [{}])[0].get("text", "")
        if obj.get("isError"):
            raise ReplyError(text)
        if obj.get("structuredContent") is not None:
            return obj["structuredContent"]
        return json.loads(text)
    return obj


async def read(paths, errors=False):
    """The payload of each saved reply file, in order. errors: return a tool error as a ReplyError instead of raising it."""
    def _read(path):
        with open(path) as f:
            raw = json.load(f)
        try:
            return unwrap(raw)
        except ReplyError as e:
            if errors:
                return e
            raise
    return list(await asyncio.gather(*(asyncio.to_thread(_read, p) for p in paths)))


def server_of(payload):
    """Which server wrote a reply, from its shape."""
    return REMOTE if isinstance(payload, dict) and ("items" in payload or "note_type_id" in payload) else LOCAL


def note_type_names(payloads):
    """{note type id: name} from anki_note_types_list pages, for search replies from servers that name types only by id."""
    return {t["id"]: t["name"] for p in payloads for t in p.get("items", []) if "note_count" in t}


def notes(payloads, type_names=None):
    """Note rows {"id", "model", "tags", "fields": {name: value}} from search or note-info replies.

    Summary search replies give only the first field, under the name "", and no model on local;
    a remote search with include_fields: true gives every field and the note type's name.
    """
    type_names = type_names or {}
    out = []
    for p in payloads:
        if "noteLabels" in p:  # local find_notes with include_first_field
            out += [{"id": n["noteId"], "model": "", "tags": [], "fields": {"": n["firstField"]}} for n in p["noteLabels"]]
        elif "notes" in p:  # local notes_info
            for n in p["notes"]:
                fields = sorted((n.get("fields") or {}).items(), key=lambda kv: kv[1].get("order", 0))
                out.append({"id": n["noteId"], "model": n.get("modelName", ""), "tags": n.get("tags", []),
                            "fields": {k: v.get("value", "") for k, v in fields}})
        elif "items" in p:  # remote anki_notes_search
            for n in p["items"]:
                if isinstance(n.get("fields"), list):  # include_fields: true, each item as anki_notes_get returns it
                    out.append({"id": n["id"], "model": n.get("note_type_name", ""), "tags": n.get("tags", []),
                                "fields": {f["name"]: f["value"] for f in n["fields"]}})
                elif "note_type_id" in n:  # a summary: the first field only; servers before 47c5699 name the type only by id
                    out.append({"id": n["id"], "model": n.get("note_type_name") or type_names.get(n["note_type_id"], ""), "tags": n.get("tags", []),
                                "fields": {"": n.get("first_field", "")}})
        elif "note_type_id" in p:  # remote anki_notes_get
            out.append({"id": p["id"], "model": p.get("note_type_name", ""), "tags": p.get("tags", []),
                        "fields": {f["name"]: f["value"] for f in p.get("fields", [])}})
    return out


def first_field(note):
    return next(iter(note["fields"].values()), "")


def decks(payloads):
    """{deck name: id} from list_decks or anki_decks_list pages (local ids may be absent)."""
    out = {}
    for p in payloads:
        for d in p.get("decks", p.get("items", [])):
            out[d["name"]] = d.get("id", d.get("deck_id"))
    return out


def description(payload):
    """(deck name, description) from get_deck_description or anki_decks_get."""
    return payload.get("name", ""), payload.get("description") or ""


def templates(payload):
    """{card name: {"Front", "Back"}} from model_templates or anki_note_types_get."""
    t = payload["templates"]
    if isinstance(t, dict):
        return t
    return {x["name"]: {"Front": x["question_format"], "Back": x["answer_format"]} for x in t}


def card_ids(payloads):
    """{note id: sorted card ids} from notes_info, anki_cards_search pages or remote create and batch receipts."""
    out = {}
    for p in payloads:
        if "notes" in p and isinstance(p["notes"], list):  # local notes_info
            for n in p["notes"]:
                out[n["noteId"]] = sorted(n.get("cards", []))
        for c in p.get("items", []):  # remote anki_cards_search
            if "note_id" in c and "deck_id" in c:
                out.setdefault(c["note_id"], []).append(c["id"])
        r = p.get("result") if isinstance(p.get("result"), dict) else {}
        for n in r.get("notes", []) if "notes" in r else ([r] if "card_ids" in r and "note_id" in r else []):
            if "note_id" in n:  # a batch's skipped duplicates have no note of their own
                out[n["note_id"]] = sorted(n.get("card_ids", []))
    return {k: sorted(v) for k, v in out.items()}


def key(*parts):
    """A stable idempotency key: the same write re-planned gets the same key, so the server applies it once."""
    return "anki-notes-" + hashlib.sha256(json.dumps(parts, sort_keys=True).encode()).hexdigest()[:40]


def call(tool, **args):
    return {"tool": tool, "args": args}


def print_plan(steps):
    """One call per line, numbered, then the plan as JSON for Claude to follow in order."""
    for i, s in enumerate(steps, 1):
        print(f"{i}. {s['tool']}" + (f"  ({s['note']})" if s.get("note") else ""))
    print(json.dumps(steps))
