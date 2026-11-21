# pyright: basic
"""Render a note type's templates with a sample note and check for leaks.

Usage:
  python3 -I render_note.py <spec.json>
  python3 -I render_note.py <note.json> --model <note type>   (templates read from Anki)

spec.json: {"templates": {"<card name>": {"Front": ..., "Back": ...}}, "note": {"<field>": ...}}
(templates in the shape model_templates returns). note.json is just the note.

A card's answer is what its back shows that its front doesn't: the fields the
back template uses and the front doesn't, or the cloze being tested. Errors:
a front shows its answer (skipped when the front names its choices, "A or B?"),
or a back reuses {{FrontSide}} although its scripted front has to hide the
answer inside another field. Template JavaScript is not run: a front with
<script> is warned about instead of checked, so preview it in Anki.
Prints every card's front and back as text, for showing the user.
"""
import asyncio
import json
import os
import re
import sys

TAG = re.compile(r"\{\{([#^/]?)\s*([^}]*?)\s*\}\}")


def plain(html):
    html = re.sub(r"(?is)<(script|style)\b.*?</\1>", " ", html)
    html = re.sub(r"<br\s*/?>|<[^>]+>", " ", html)
    return re.sub(r"\s+", " ", html.replace("&nbsp;", " ")).strip()


def has(haystack, needle):
    return re.search(rf"(?<!\w){re.escape(needle)}(?!\w)", haystack, re.I) is not None


def refs(template):
    """Field names a template uses, any filter stripped."""
    return {name.split(":")[-1] for kind, name in TAG.findall(template) if name != "FrontSide"}


def cloze(value, n, side):
    def sub(m):
        num, body, hint = int(m.group(1)), m.group(2), m.group(3)
        if num != n:
            return body
        return f"<b>{body}</b>" if side == "back" else f"[{hint or '...'}]"
    return re.sub(r"\{\{c(\d+)::(.*?)(?:::(.*?))?\}\}", sub, value)


def render(template, note, n=None, side="front", front_side=""):
    def section(m):
        kind, name, inner = m.group(1), m.group(2), m.group(3)
        filled = bool(plain(note.get(name, "")))
        return inner if filled == (kind == "#") else ""
    out = template
    while True:  # sections can nest; resolve innermost first
        new = re.sub(r"\{\{([#^])\s*([^}]+?)\s*\}\}((?:(?!\{\{[#^]).)*?)\{\{/\s*\2\s*\}\}", section, out, flags=re.S)
        if new == out:
            break
        out = new

    def field(m):
        kind, name = m.group(1), m.group(2)
        if name == "FrontSide":
            return front_side
        *filters, fname = name.split(":")
        value = note.get(fname, "")
        if "cloze" in filters:
            return cloze(value, n, side)
        if "type" in filters:
            return ""
        return plain(value) if "text" in filters else value
    return TAG.sub(field, out)


def cards(templates, note):
    """[(label, n, front template, back template)]: one per cloze number for cloze types."""
    out = []
    for name, t in templates.items():
        if re.search(r"\{\{[^}]*cloze:", t["Front"]):
            fields = [f for f in refs(t["Front"]) if re.search(r"\{\{c\d+::", note.get(f, ""))]
            nums = sorted({int(x) for f in fields for x in re.findall(r"\{\{c(\d+)::", note[f])})
            out += [(f"{name} c{n}", n, t["Front"], t["Back"]) for n in nums]
        else:
            out.append((name, None, t["Front"], t["Back"]))
    return out


def check(templates, note):
    findings, shown = [], []
    for label, n, ft, bt in cards(templates, note):
        front = render(ft, note, n, "front")
        back = render(bt, note, n, "back", front_side=front)
        shown.append((label, plain(front), plain(back)))
        if not plain(front):
            findings.append(("warn", f"{label}: front is empty, so Anki makes no card"))
            continue
        if n is not None:
            answers = [plain(a) for f in refs(ft) for num, a in re.findall(r"\{\{c(\d+)::(.*?)(?:::.*?)?\}\}", note.get(f, "")) if int(num) == n]
        else:
            answers = [plain(note.get(f, "")) for f in refs(bt) - refs(ft)]
        answers = [a for a in answers if len(a) > 1]
        scripted = "<script" in ft.lower()
        # a front that names its choices ("A or B?") must contain the answer, as in lint_cards
        choices = re.search(r"\bor\b", plain(front), re.I)
        if not scripted and not choices:
            for a in answers:
                if has(plain(front), a):
                    findings.append(("error", f"{label}: front shows its answer '{a}'"))
        if scripted:
            findings.append(("warn", f"{label}: front has JavaScript, which this check can't run; preview it in Anki"))
        # a scripted front that shows a field containing the answer has to hide it there
        hiding = [f for f in refs(ft) for a in answers if has(plain(note.get(f, "")), a)] if n is None else []
        if scripted and hiding and "{{FrontSide}}" in bt.replace(" ", ""):
            findings.append(("error", f"{label}: back reuses {{{{FrontSide}}}} but the front has to hide the answer in "
                                      f"{', '.join(sorted(set(hiding)))}; render the fields fresh"))
    return findings, shown


async def main():
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)

    def read():
        with open(args[0]) as f:
            return json.load(f)
    data = await asyncio.to_thread(read)
    if "--model" in args:
        sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))  # -I leaves this dir off sys.path
        from ankimcp_client import AnkiError, Client
        try:
            async with Client() as anki:
                templates = (await anki.call("model_templates", model_name=args[args.index("--model") + 1]))["templates"]
        except AnkiError as e:
            sys.exit(str(e))
        note = data
    else:
        templates, note = data["templates"], data["note"]
    findings, shown = check(templates, note)
    for label, front, back in shown:
        print(f"{label}\n  front: {front}\n  back:  {back}")
    for sev, msg in findings:
        print(f"[{sev}] {msg}")
    sys.exit(1 if any(s == "error" for s, _ in findings) else 0)


if __name__ == "__main__":
    asyncio.run(main())
