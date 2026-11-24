# pyright: basic
"""How much of a deck shares one card format (SKILL.md step 1, "Vary the shape").

Usage: python3 -I format_mix.py <reply.json>... [--target 0.85]

The replies are the deck's notes, saved by Claude:
  local   notes_info pages for every note id find_notes returns for deck:"<deck>"
  remote  anki_notes_search pages for deck:"<deck>" with include_fields: true

A format is coarse on purpose: note type, the type:: tag, and whether a field
holds an image or sound. A deck theme's copies ("<Deck> · Basic") count as the
type they copy. (A remote search without include_fields carries only the first
field, so media in other fields isn't seen; from a server older than 47c5699,
also pass an anki_note_types_list reply so the note types get their names.) Prints each format's share, most common first, and a last line
saying whether the top one is over the target. It only measures: Claude decides
whether a new card can take another shape that teaches equally well.
"""
import asyncio
import os
import re
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))  # -I leaves this dir off sys.path
from replies import ReplyError, note_type_names, notes, read  # noqa: E402

_MEDIA = re.compile(r"<img\b|\[sound:", re.I)


def note_format(note):
    model = note["model"].split(" · ")[-1]
    kind = next((t for t in note["tags"] if t.startswith("type::")), "type::-")
    media = any(_MEDIA.search(v) for v in note["fields"].values())
    return f"{model} {kind}" + (" +media" if media else "")


def mix(notes):
    """[(format, share)] most common first."""
    counts = Counter(note_format(n) for n in notes)
    return [(f, c / len(notes)) for f, c in counts.most_common()]


async def main():
    args = sys.argv[1:]
    target = float(args.pop(args.index("--target") + 1)) if "--target" in args else 0.85
    args = [a for a in args if a != "--target"]
    if not args:
        sys.exit(__doc__)
    try:
        payloads = await read(args)
    except ReplyError as e:
        sys.exit(f"a saved reply is an error: {e}")
    found = notes(payloads, note_type_names(payloads))
    if not found:
        sys.exit("no notes in the saved replies")
    shares = mix(found)
    for f, s in shares:
        print(f"{s:5.0%}  {f}")
    top, share = shares[0]
    verdict = "over" if share > target else "within"
    print(f"{len(found)} notes; most common is {top} at {share:.0%}, {verdict} the {target:.0%} target")


if __name__ == "__main__":
    asyncio.run(main())
