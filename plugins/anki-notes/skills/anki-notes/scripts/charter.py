# pyright: basic
"""Mechanical checks and edits for deck charters (see charters.md).

Usage:
  python3 -I charter.py lint <charter.md> [--deck <name>]
  python3 -I charter.py lint --deck <name>
  python3 -I charter.py edit <charter.md> <section> <new-body.md> <out.md>

lint checks the required sections, the Assumes: line, that Adding is Automatic
or Ask, stage numbering and one-line descriptions, the ~250-word cap and the
tag prefix. With --deck it also reads Anki: the saved charter when no file is
given, the other top-level decks' tag prefixes (must differ) and the deck's
subdecks (must match the stages). Without --deck it needs no Anki, so it runs
in the claude.ai sandbox. Exit 1 on any error.

edit replaces one section's body, writes the full new text to out.md and
prints the diff: every other line stays byte for byte.
"""
import asyncio
import difflib
import os
import re
import sys

REQUIRED = ("Scope", "Out of scope", "Adding", "Stages", "Conventions")
MAX_WORDS = 250
STAGE = re.compile(r"`(\d{2}) ([^`]+)`")


def split_sections(text):
    """[(heading or None, chunk)]: chunks concatenate back to text exactly."""
    parts = re.split(r"(?m)^(?=## )", text)
    return [(re.match(r"## (.*)", p).group(1).strip() if p.startswith("## ") else None, p) for p in parts if p]


def sections(text):
    return {h: chunk.split("\n", 1)[1] if "\n" in chunk else "" for h, chunk in split_sections(text) if h}


def stages(text):
    return [(n, name.strip()) for n, name in STAGE.findall(sections(text).get("Stages", ""))]


def prefix(text):
    m = re.search(r"`([a-z0-9-]+)::", sections(text).get("Conventions", ""))
    return m.group(1) if m else None


def lint(text, other_prefixes=(), subdecks=None):
    out = []
    secs = sections(text)
    for name in REQUIRED:
        if name not in secs:
            out.append(("error", f"missing section: ## {name}"))
    if not re.search(r"(?m)^Assumes:", text):
        out.append(("error", "no 'Assumes:' line"))
    adding = secs.get("Adding", "").strip()
    if "Adding" in secs and not re.match(r"(Automatic|Ask)\b", adding):
        out.append(("error", "Adding must start with Automatic or Ask"))

    st = stages(text)
    if "Stages" in secs and not st:
        out.append(("error", "no stages: list them as - `01 <name>`: what it covers"))
    nums = [int(n) for n, _ in st]
    if nums and (min(nums) > 1 or sorted(nums) != list(range(min(nums), min(nums) + len(nums)))):
        out.append(("error", f"stage numbers {nums} are not 01..n (or 00..n)"))
    for line in secs.get("Stages", "").splitlines():
        for n, name in STAGE.findall(line):
            # "`01 X`: covers ..." or "`01 X` — covers ...", one stage per line
            if not re.search(rf"`{n} {re.escape(name)}`\s*[:—–-]\s*\w", line) or len(STAGE.findall(line)) > 1:
                out.append(("warn", f"stage {n} {name.strip()} has no one-line description"))

    words = len(re.findall(r"\S+", text))
    if words > MAX_WORDS:
        out.append(("warn", f"{words} words; keep it under about {MAX_WORDS}"))

    p = prefix(text)
    if not p:
        out.append(("error", "Conventions names no tag prefix (`<prefix>::<area>::<topic>`)"))
    elif p in other_prefixes:
        out.append(("error", f"tag prefix {p}:: is already used by another deck"))

    if subdecks is not None:
        named = {f"{n} {name}" for n, name in st}
        for s in sorted(named - set(subdecks)):
            out.append(("warn", f"stage {s} has no subdeck"))
        for s in sorted(set(subdecks) - named):
            out.append(("warn", f"subdeck {s} is not a stage"))
    return out


def edit(text, section, body):
    chunks = split_sections(text)
    if section not in [h for h, _ in chunks]:
        sys.exit(f"no section ## {section}")
    body = body.strip("\n") + "\n"
    out = []
    for i, (h, chunk) in enumerate(chunks):
        if h == section:
            # keep the blank line that separated it from the next section
            sep = "\n" if i < len(chunks) - 1 and chunk.endswith("\n\n") else ""
            chunk = f"## {h}\n{body}{sep}"
        out.append(chunk)
    return "".join(out)


async def from_anki(deck, want_text):
    sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))  # -I leaves this dir off sys.path
    from ankimcp_client import AnkiError, Client
    try:
        async with Client() as anki:
            names = [d["name"] for d in (await anki.call("list_decks"))["decks"]]
            others = []
            for top in (n for n in names if "::" not in n and n != deck):
                d = await anki.call("get_deck_description", deck_name=top)
                if prefix(d.get("description") or ""):
                    others.append(prefix(d["description"]))
            text = (await anki.call("get_deck_description", deck_name=deck)).get("description") if want_text else None
    except AnkiError as e:
        sys.exit(str(e))
    subs = [n[len(deck) + 2:] for n in names if n.startswith(deck + "::") and "::" not in n[len(deck) + 2:]]
    return text, others, subs


async def read(path):
    def _read():
        with open(path) as f:
            return f.read()
    return await asyncio.to_thread(_read)


async def main():
    args = sys.argv[1:]
    if not args or args[0] not in ("lint", "edit"):
        sys.exit(__doc__)
    if args[0] == "edit":
        if len(args) != 5:
            sys.exit(__doc__)
        old, body = await read(args[1]), await read(args[3])
        new = edit(old, args[2], body)

        def write():
            with open(args[4], "w") as f:
                f.write(new)
        await asyncio.to_thread(write)
        sys.stdout.writelines(difflib.unified_diff(old.splitlines(True), new.splitlines(True), "old", "new"))
        return

    deck = args[args.index("--deck") + 1] if "--deck" in args else None
    files = [a for a in args[1:] if a != "--deck" and a != deck]
    others, subs, text = (), None, None
    if deck:
        text, others, subs = await from_anki(deck, not files)
    if files:
        text = await read(files[0])
    if not text:
        sys.exit("no charter text")
    findings = lint(text, others, subs)
    for sev, msg in findings:
        print(f"[{sev}] {msg}")
    print(f"{len(findings)} findings")
    sys.exit(1 if any(s == "error" for s, _ in findings) else 0)


if __name__ == "__main__":
    asyncio.run(main())
