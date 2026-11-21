# pyright: basic
"""Check every eval case against the rules in plugins/anki-notes/CLAUDE.md.

Usage: python3 -I check_cases.py

Cases:
- prompt.md has a description, loads exactly ["../..", "../../../ankimcp"]
  and sets EVAL_SKIP_INBOX_HOOK: "1" in env.
- Every allowed ankimcp tool has a mock (the case's or the shared one), so no
  call can reach a real Anki, and every mocked tool is in _tools.json.
- A case tagged charter, note-type or questionnaire allows Read, or the
  skill can't open charters.md or note-types.md.
- An llm grader with focus: trace is paired with a grader that sees every call
  (tool_used, tool_order, or regex on mock_calls).

Mocks: every JSON reply (a whole-file reply, a fixture it loads, or a reply an
agent mock quotes on its own line) has the keys _shapes.json lists for its tool.

Exit 1 on any problem.
"""
import asyncio
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SHARED = HERE / "mocks" / "anki"
PLUGINS = '["../..", "../../../ankimcp"]'
TOOL_PREFIX = "mcp__plugin_ankimcp_anki__"
NEEDS_READ = {"charter", "note-type", "questionnaire"}  # the skill reads charters.md / note-types.md


def frontmatter(text):
    m = re.match(r"---\n(.*?)\n---", text, re.S)
    return m.group(1) if m else ""


def check_case(case, mocked, known):
    out = []
    fm = frontmatter((case / "prompt.md").read_text())
    if not re.search(r"(?m)^description:\s*\S", fm):
        out.append("prompt.md has no description")
    if not re.search(rf"(?m)^plugins:\s*{re.escape(PLUGINS)}\s*$", fm):
        out.append(f"plugins must be {PLUGINS}")
    if not re.search(r"(?m)^env:\s*\n(?:[ \t]+.*\n)*?[ \t]+EVAL_SKIP_INBOX_HOOK:\s*[\"']1[\"']", fm + "\n"):
        out.append('env must set EVAL_SKIP_INBOX_HOOK: "1"')

    tags = re.search(r"(?m)^tags:\s*\[(.*)\]", fm)
    tags = {t.strip() for t in tags.group(1).split(",")} if tags else set()
    allowed_list = re.search(r"(?m)^allowed_tools:\s*\[(.*)\]", fm)
    if tags & NEEDS_READ and not re.search(r"\bRead\b", allowed_list.group(1) if allowed_list else ""):
        out.append(f"tagged {', '.join(sorted(tags & NEEDS_READ))}: allowed_tools must include Read for the skill's guides")

    own = {p.stem for p in (case / "mocks" / "anki").glob("*.md")}
    allowed = re.search(r"(?m)^allowed_tools:\s*\[(.*)\]", fm)
    for tool in re.findall(rf"{TOOL_PREFIX}(\w+)", allowed.group(1) if allowed else ""):
        if tool not in mocked | own:
            out.append(f"{tool} is allowed but has no mock: a call would reach a real Anki")
    for tool in sorted(own - known):
        out.append(f"mocks/anki/{tool}.md: {tool} is not in _tools.json")

    graders = [frontmatter(g.read_text()) for g in sorted((case / "graders").glob("*.md"))]
    sees_calls = any(re.search(r"(?m)^type:\s*(tool_used|tool_order)\b", g)
                     or (re.search(r"(?m)^type:\s*regex\b", g) and re.search(r"(?m)^target:\s*mock_calls\b", g))
                     for g in graders)
    if not sees_calls and any(re.search(r"(?m)^type:\s*llm\b", g) and re.search(r"(?m)^focus:\s*trace\b", g) for g in graders):
        out.append("an llm grader with focus: trace needs a grader that sees every call (tool_used, tool_order or regex on mock_calls)")
    return out


def rel(path):
    return str(path.relative_to(HERE)) if path.is_relative_to(HERE) else str(path)


def replies(mock):
    """(label, parsed JSON) for each JSON reply a mock file can send."""
    text = mock.read_text()
    if text.startswith("---"):  # agent mock: replies are quoted on their own lines
        lines = [l for l in text.splitlines() if l.startswith("{")]
    else:
        lines = [text.strip()]
    out = []
    for line in lines:
        f = re.fullmatch(r"\{\{file:(.+?)\}\}", line)
        if f:
            pattern = re.sub(r"\{input\.\w+\}", "*", f.group(1))
            out += [(rel(p), p.read_text()) for p in sorted(mock.parent.glob(pattern))]
            continue
        out.append((rel(mock), line))
    parsed = []
    for label, raw in out:
        try:
            parsed.append((label, json.loads(re.sub(r"\{\{[^}]*\}\}", "x", raw))))
        except ValueError:
            pass  # an error-text reply, or a template line that isn't a full reply
    return parsed


def check_shape(label, reply, shape):
    out = [f"{label}: reply lacks {k!r}" for k in shape.get("keys", []) if not isinstance(reply, dict) or k not in reply]
    for key, item_keys in shape.get("items", {}).items():
        for i, item in enumerate(reply.get(key, []) if isinstance(reply, dict) else []):
            out += [f"{label}: {key}[{i}] lacks {k!r}" for k in item_keys if k not in item]
    return out


async def main():
    tools_text, shapes_text = await asyncio.gather(*(asyncio.to_thread((SHARED / f).read_text) for f in ("_tools.json", "_shapes.json")))
    tools = json.loads(tools_text)
    known = {t["name"] for t in (tools["tools"] if isinstance(tools, dict) else tools)}
    shapes = json.loads(shapes_text)["tools"]
    mocked = {p.stem for p in SHARED.glob("*.md")}
    problems = [f"mocks/anki/{t}.md: {t} is not in _tools.json" for t in sorted(mocked - known)]

    cases = sorted(p.parent for p in HERE.glob("*/prompt.md"))
    mocks = [m for m in sorted(HERE.glob("**/mocks/anki/*.md")) if m.stem in shapes]
    # every case and mock is read in its own thread; results keep their sorted order
    found = await asyncio.gather(*(asyncio.to_thread(check_case, c, mocked, known) for c in cases),
                                 *(asyncio.to_thread(replies, m) for m in mocks))
    for case, msgs in zip(cases, found):
        problems += [f"{case.name}: {m}" for m in msgs]
    for mock, reps in zip(mocks, found[len(cases):]):
        for label, reply in reps:
            problems += check_shape(label, reply, shapes[mock.stem])

    for p in problems:
        print(p)
    print(f"{len(cases)} cases checked, {len(problems)} problems")
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    asyncio.run(main())
