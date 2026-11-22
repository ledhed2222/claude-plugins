# pyright: basic
"""How much of a deck shares one card format (SKILL.md step 1, "Vary the shape").

Usage: python3 -I format_mix.py <deck or deck::stage> [--target 0.85]

A format is coarse on purpose: note type, the type:: tag, and whether a field
holds an image or sound. A deck theme's copies ("<Deck> · Basic") count as the
type they copy. Prints each format's share, most common first, and a last line
saying whether the top one is over the target. It only measures: Claude decides
whether a new card can take another shape that teaches equally well.
"""
import asyncio
import os
import re
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))  # -I leaves this dir off sys.path
from ankimcp_client import AnkiError, Client  # noqa: E402

_PAGE = 500
_BATCH = 100  # the add-on's default max_notes_per_batch
_MEDIA = re.compile(r"<img\b|\[sound:", re.I)


def note_format(note):
    model = note.get("modelName", "").split(" · ")[-1]
    kind = next((t for t in note.get("tags", []) if t.startswith("type::")), "type::-")
    media = any(_MEDIA.search(f.get("value", "")) for f in note.get("fields", {}).values())
    return f"{model} {kind}" + (" +media" if media else "")


def mix(notes):
    """[(format, share)] most common first."""
    counts = Counter(note_format(n) for n in notes)
    return [(f, c / len(notes)) for f, c in counts.most_common()]


async def _notes(anki, deck):
    ids, offset = [], 0
    while True:
        r = await anki.call("find_notes", query=f'deck:"{deck}"', limit=_PAGE, offset=offset)
        ids += r.get("noteIds", [])
        if not r.get("hasMore"):
            break
        offset += _PAGE
    pages = await asyncio.gather(*(anki.call("notes_info", notes=ids[i:i + _BATCH]) for i in range(0, len(ids), _BATCH)))
    return [n for p in pages for n in p.get("notes", [])]


async def main():
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)
    target = float(args[args.index("--target") + 1]) if "--target" in args else 0.85
    try:
        async with Client() as anki:
            notes = await _notes(anki, args[0])
    except AnkiError as e:
        sys.exit(str(e))
    if not notes:
        sys.exit(f"no notes in {args[0]}")
    shares = mix(notes)
    for f, s in shares:
        print(f"{s:5.0%}  {f}")
    top, share = shares[0]
    verdict = "over" if share > target else "within"
    print(f"{len(notes)} notes; most common is {top} at {share:.0%}, {verdict} the {target:.0%} target")


if __name__ == "__main__":
    asyncio.run(main())
