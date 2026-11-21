# pyright: basic
"""List existing notes that look like each drafted card (SKILL.md step 2).

Usage: python3 -I find_dupes.py <cards.json|inbox.md> [--threshold 0.5]

Reads every note's first field in each draft's subject deck (all note types)
and prints, per draft, the closest ones by wording. It only lists candidates:
Claude reads them and decides what is a repeat, a near neighbor or unrelated.
It does not replace the w:term searches for prerequisites.
"""
import asyncio
import difflib
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))  # -I leaves this dir off sys.path
from ankimcp_client import AnkiError, Client  # noqa: E402
from lint_cards import read_cards, text  # noqa: E402

PAGE = 500


def norm(s):
    s = re.sub(r"\{\{c\d+::(.*?)(?:::.*?)?\}\}", r"\1", s)
    return " ".join(re.findall(r"\w+", text(s).lower()))


def score(a, b):
    a, b = norm(a), norm(b)
    if not a or not b:
        return 0.0
    wa, wb = set(a.split()), set(b.split())
    return max(difflib.SequenceMatcher(None, a, b).ratio(), len(wa & wb) / len(wa | wb))


def close_matches(draft, existing, threshold=0.5, n=3):
    """existing: [(note id, first field)] -> the n best [(score, id, first field)] at or above threshold."""
    scored = sorted(((score(draft, f), nid, f) for nid, f in existing), reverse=True)
    return [s for s in scored[:n] if s[0] >= threshold]


async def first_fields(anki, deck):
    out, offset = [], 0
    while True:
        r = await anki.call("find_notes", query=f'deck:"{deck}"', limit=PAGE, offset=offset, include_first_field=True)
        out += [(n["noteId"], n["firstField"]) for n in r.get("noteLabels", [])]
        if not r.get("hasMore"):
            return out
        offset += PAGE


async def main():
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)
    threshold = float(args[args.index("--threshold") + 1]) if "--threshold" in args else 0.5
    cards = [(n, c) for n, c in await read_cards(args[0]) if "fields" in c]
    try:
        async with Client() as anki:
            names = list(dict.fromkeys(c["deck"] for _, c in cards))
            decks = dict(zip(names, await asyncio.gather(*(first_fields(anki, d) for d in names))))
    except AnkiError as e:
        sys.exit(str(e))
    for n, c in cards:
        draft = next(iter(c["fields"].values()), "")
        matches = close_matches(draft, decks[c["deck"]], threshold)
        print(f"#{n} {text(draft)[:70]}")
        for s, nid, f in matches:
            print(f"    {s:.2f} note {nid}: {text(f)[:90]}")
        if not matches:
            print("    no close match")


if __name__ == "__main__":
    asyncio.run(main())
