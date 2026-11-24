"""Test support for running every Anki-facing test against both servers.

The skill works with two MCP servers (see replies.py): the AnkiMCP add-on
(local) and anki-sync-mcp (remote). plugins/anki-notes/CLAUDE.md requires that
any test touching an Anki reply or call is written once, as a *Contract mixin
that reads self.server, and runs as two classes:

    class SearchContract:
        def test_reads_first_fields(self):
            rows = notes([load(self.server, "search")])
            ...

    class LocalSearch(SearchContract, unittest.TestCase): server = LOCAL
    class RemoteSearch(SearchContract, unittest.TestCase): server = REMOTE

test_both_servers.py fails when a Contract lacks either class, when an
operation's fixture is missing for one server, or when a script emits a call
that the server's real tool schema rejects.
"""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from replies import LOCAL, REMOTE, unwrap

SERVERS = (LOCAL, REMOTE)
HERE = Path(__file__).resolve().parent
DATA = HERE / "testdata"
_PLUGIN = HERE.parents[2]
# each eval suite's _tools.json is a saved tools/list from that real server
_TOOLS_FILES = {LOCAL: _PLUGIN / "evals" / "mocks" / "anki" / "_tools.json",
                REMOTE: _PLUGIN / "evals-remote" / "mocks" / "anki" / "_tools.json"}
# shortcut: no saved schema for these add-on tools, so their args aren't checked; save them from a running add-on's tools/list
UNVERIFIED = {LOCAL: {"card_change_deck", "card_unsuspend"}, REMOTE: set()}

OPERATIONS = json.loads((DATA / "operations.json").read_text())


def path(server, op):
    return DATA / server / f"{op}.json"


def raw(server, op):
    return json.loads(path(server, op).read_text())


def load(server, op):
    """A fixture's payload; a tool-error fixture raises ReplyError."""
    return unwrap(raw(server, op))


def deck_notes(server):
    """The fixture deck's notes, read the way format_mix.py reads them on each server."""
    from replies import notes
    return notes([load(server, "deck_notes")])


def tools(server):
    return {t["name"]: t for t in json.loads(_TOOLS_FILES[server].read_text())["tools"]}


_JSON_TYPES = {"string": str, "integer": int, "number": (int, float), "boolean": bool, "array": list, "object": dict, "null": type(None)}


def _bounds_ok(value, schema):
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if "minimum" in schema and value < schema["minimum"]:
            return False
        if "maximum" in schema and value > schema["maximum"]:
            return False
        if "exclusiveMinimum" in schema and value <= schema["exclusiveMinimum"]:
            return False
        if "exclusiveMaximum" in schema and value >= schema["exclusiveMaximum"]:
            return False
    if isinstance(value, (str, list)):
        low, high = ("minLength", "maxLength") if isinstance(value, str) else ("minItems", "maxItems")
        if low in schema and len(value) < schema[low]:
            return False
        if high in schema and len(value) > schema[high]:
            return False
    return True


def _type_ok(value, schema, defs):
    if "$ref" in schema:
        schema = defs[schema["$ref"].split("/")[-1]]
    options = schema.get("anyOf") or [schema]
    for opt in options:
        if "$ref" in opt:
            opt = defs[opt["$ref"].split("/")[-1]]
        t = opt.get("type")
        if t is None:
            return True
        if isinstance(value, bool) and t in ("integer", "number"):
            continue
        if isinstance(value, _JSON_TYPES[t]):
            if not _bounds_ok(value, opt):
                continue
            if t == "array" and "items" in opt:
                return all(_type_ok(v, opt["items"], defs) for v in value)
            if t == "object" and "properties" in opt:
                return not check_args(value, opt, defs)
            return True
    return False


def check_args(args, schema, defs=None):
    """Problems with args against a JSON schema: missing required, unknown or mistyped properties."""
    defs = defs if defs is not None else schema.get("$defs", {})
    props = schema.get("properties", {})
    out = [f"missing required {k!r}" for k in schema.get("required", []) if k not in args]
    for k, v in args.items():
        if k not in props:
            if schema.get("additionalProperties") is False or props:
                out.append(f"unknown argument {k!r}")
        elif not _type_ok(v, props[k], defs):
            out.append(f"{k!r}={v!r} doesn't match its schema")
    return out


def check_call(server, call):
    """Problems with one planned {"tool", "args"} call against that server's real tool list."""
    known = tools(server)
    if call["tool"] in UNVERIFIED[server]:
        return []
    if call["tool"] not in known:
        return [f"{call['tool']} is not a {server} tool"]
    return [f"{call['tool']}: {p}" for p in check_args(call["args"], known[call["tool"]]["inputSchema"])]


def run_script(name, *args, files=None):
    """Run a script as the skill does (python3 -I), with fixture files copied into a temp dir; names in args are replaced by their paths."""
    with tempfile.TemporaryDirectory() as tmp:
        paths = {}
        for fname, content in (files or {}).items():
            paths[fname] = os.path.join(tmp, fname)
            with open(paths[fname], "w") as f:
                f.write(content if isinstance(content, str) else json.dumps(content))
        argv = [sys.executable, "-I", str(HERE / name)] + [paths.get(a, a) for a in args]
        return subprocess.run(argv, capture_output=True, text=True, cwd=tmp)


def plan_lines(stdout):
    """The JSON call list a planner prints last."""
    return json.loads(stdout.strip().splitlines()[-1])
