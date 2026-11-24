# pyright: basic
"""List existing notes that look like each drafted card (SKILL.md step 2).

Usage: python3 -I find_dupes.py <cards.json> <search-reply.json>... [--threshold 0.5]

The replies are the saved pages of a search for the subject deck, every note
type: find_notes with query deck:"<subject>" and include_first_field: true
(local), or anki_notes_search with the same query (remote). Prints, per draft,
the deck's notes worded most like it. It only lists candidates: Claude decides
what is a repeat, a near neighbor or unrelated. A score of 1.00 is the same
first field, which the server refuses as a duplicate. It does not replace the
w:term searches for prerequisites.
"""
import asyncio
import difflib
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))  # -I leaves this dir off sys.path
from lint_cards import read_cards, text  # noqa: E402
from replies import ReplyError, first_field, notes, read  # noqa: E402


def _norm(s):
    s = re.sub(r"\{\{c\d+::(.*?)(?:::.*?)?\}\}", r"\1", s)
    return " ".join(re.findall(r"\w+", text(s).lower()))


def _score(a, b):
    a, b = _norm(a), _norm(b)
    if not a or not b:
        return 0.0
    wa, wb = set(a.split()), set(b.split())
    return max(difflib.SequenceMatcher(None, a, b).ratio(), len(wa & wb) / len(wa | wb))


def close_matches(draft, existing, threshold=0.5, n=3):
    """existing: [(note id, first field)] -> the n best [(score, id, first field)] at or above threshold."""
    scored = sorted(((_score(draft, f), nid, f) for nid, f in existing), reverse=True)
    return [s for s in scored[:n] if s[0] >= threshold]


async def main():
    args = sys.argv[1:]
    threshold = float(args.pop(args.index("--threshold") + 1)) if "--threshold" in args else 0.5
    args = [a for a in args if a != "--threshold"]
    if len(args) < 2:
        sys.exit(__doc__)
    cards = [(n, c) for n, c in await read_cards(args[0]) if "fields" in c]
    try:
        existing = [(n["id"], first_field(n)) for n in notes(await read(args[1:]))]
    except ReplyError as e:
        sys.exit(f"a saved reply is an error: {e}")
    for n, c in cards:
        draft = next(iter(c["fields"].values()), "")
        matches = close_matches(draft, existing, threshold)
        print(f"#{n} {text(draft)[:70]}")
        for s, nid, f in matches:
            print(f"    {s:.2f} note {nid}: {text(f)[:90]}")
        if not matches:
            print("    no close match")


if __name__ == "__main__":
    asyncio.run(main())
