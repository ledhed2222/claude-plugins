# pyright: basic
"""Regenerate the case list in SPEC.md from the eval case files.

Usage: python3 -I gen_spec.py [--check]

Only the text between the generated markers in SPEC.md is rewritten; the rest
is hand-written. --check exits 1 instead of writing when SPEC.md is stale (CI).
"""
import asyncio
import re
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_SPEC = _HERE / "SPEC.md"
_START, _END = "<!-- generated:start -->", "<!-- generated:end -->"


def _split_frontmatter(text):
    m = re.match(r"---\n(.*?)\n---\n?(.*)", text, re.S)
    if not m:
        return {}, text.strip()
    meta = {}
    for line in m.group(1).splitlines():
        # top-level `key: value` only; nested blocks (env:) are skipped
        km = re.match(r"([A-Za-z_]+):\s*(.*)$", line)
        if km:
            meta[km.group(1)] = km.group(2).strip().strip('"').strip("'")
    return meta, m.group(2).strip()


def _tool_name(full):
    return full.rsplit("__", 1)[-1]


def _describe(meta, body):
    kind = meta.get("type", "?")
    if kind == "tool_used":
        tool = f"`{_tool_name(meta.get('tool', '?'))}`"
        if meta.get("max") == "0":
            return "tool check", f"{tool} is never called"
        n = meta.get("min", "1")
        return "tool check", f"{tool} is called at least {'once' if n == '1' else n + ' times'}"
    if kind == "regex":
        where = {"mock_calls": "the inputs sent to the mocked Anki tools",
                 "last_message": "the final reply", "trace": "the whole transcript"}.get(meta.get("target", "last_message"), meta.get("target"))
        case = " (case-insensitive)" if "i" in meta.get("flags", "") else ""
        verb = "never contain" if meta.get("match") == "not_contains" else "contain"
        return "text search", f"{where} {verb} `{meta.get('pattern', '')}`{case}"
    if kind == "llm":
        seen = "the final reply" if meta.get("focus", "last_message") == "last_message" else "the transcript"
        rule = " ".join(line.strip() for line in body.splitlines() if line.strip())
        return f"LLM judge, reads {seen}", rule
    return kind, body.replace("\n", " ")


def _render_case(c):
    out = []
    meta, prompt = _split_frontmatter((c / "prompt.md").read_text())
    out.append(f"\n### {c.name}\n\n{meta.get('description', '')}\n")
    out.append("**User message:**\n\n" + "\n".join(f"> {line}" if line else ">" for line in prompt.splitlines()))
    overrides = sorted(p.stem for p in (c / "mocks" / "anki").glob("*.md")) if (c / "mocks" / "anki").is_dir() else []
    deck = "the shared mock deck" + (f", with this case's own {', '.join(f'`{o}`' for o in overrides)}" if overrides else "")
    out.append(f"\n**Deck:** {deck}.\n")
    out.append("| grader | kind | passes when |\n|---|---|---|")
    for g in sorted((c / "graders").glob("*.md")):
        gmeta, gbody = _split_frontmatter(g.read_text())
        kind, rule = _describe(gmeta, gbody)
        # a | ends a table cell even inside backticks
        rule = rule.replace("|", "\\|")
        out.append(f"| `{g.stem}` | {kind} | {rule} |")
    return meta.get("description", ""), out


async def _render():
    cases = sorted(p for p in _HERE.iterdir() if (p / "prompt.md").is_file())
    rendered = await asyncio.gather(*(asyncio.to_thread(_render_case, c) for c in cases))  # one thread per case, order kept
    out = ["| case | what it checks |\n|---|---|"]
    out += [f"| [`{c.name}`](#{c.name}) | {desc} |" for c, (desc, _) in zip(cases, rendered)]
    out += [line for _, lines in rendered for line in lines]
    return "\n".join(out) + "\n"


async def main():
    spec, body = await asyncio.gather(asyncio.to_thread(_SPEC.read_text), _render())
    head, rest = spec.split(_START, 1)
    _, tail = rest.split(_END, 1)
    new = f"{head}{_START}\n{body}{_END}{tail}"
    if "--check" in sys.argv:
        if new != spec:
            sys.exit("SPEC.md is out of date with the eval cases: run python3 -I plugins/anki-notes/evals/gen_spec.py and commit the result")
        return
    await asyncio.to_thread(_SPEC.write_text, new)


if __name__ == "__main__":
    asyncio.run(main())
