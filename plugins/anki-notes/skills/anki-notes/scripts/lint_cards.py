# pyright: basic
"""Mechanical checks on drafted cards, before they are added or queued.

Usage: python3 -I lint_cards.py <cards.json> [--prefix aie] [--strict]

cards.json is a list of cards in the Anki inbox's format:
  {"deck": ..., "stage": ..., "model": "Basic"|"Cloze"|..., "fields": {...}, "tags": [...]}

Standard library only, so it also runs in the claude.ai sandbox.
Findings are "error" (empty fields, broken cloze, missing tags) or "warn"
(heuristics: they misfire on other languages and on the paired-relationship
cloze exception, so Claude fixes or explains them, never silently ignores).
Exit 1 on any error, or on any warning with --strict.
"""
import asyncio
import json
import re
import sys

YESNO = re.compile(r"^\s*(is|are|was|were|does|do|did|can|could|should|will|would|has|have|had)\b", re.I)
LIST_ASK = re.compile(r"\b(name|list|give|state)\s+(all|the\s+(two|three|four|five|six|\d+))\b|\ban example of\b|\bgive an? example\b", re.I)
STOP = {"which", "their", "about", "there", "these", "those", "would", "could", "other", "where", "while", "being", "after", "before"}


def text(html):
    html = re.sub(r"<br\s*/?>", " ", html or "")
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", html)).strip()


def words(s):
    return [w for w in re.findall(r"[^\W\d_]{5,}", s.lower()) if w not in STOP]


def lint(card, prefix=None):
    out = []
    f = card.get("fields", {})
    model = card.get("model", "")
    tags = card.get("tags", [])

    def add(sev, msg):
        out.append((sev, msg))

    if model == "Cloze":
        body = f.get("Text", "")
        nums = sorted({int(n) for n in re.findall(r"\{\{c(\d+)::", body)})
        if not nums:
            add("error", "Cloze has no {{c1::...}} deletion")
        elif nums != list(range(1, len(nums) + 1)):
            add("error", f"cloze numbers {nums} are not 1..n")
        for ans in re.findall(r"\{\{c\d+::(.*?)(?:::.*?)?\}\}", body):
            if len(text(ans).split()) > 6:
                add("warn", f"cloze answer is long ({len(text(ans).split())} words): split the note")
        if re.search(r"\{\{c\d+::\s*\}\}", body):
            add("error", "empty cloze deletion")
    else:
        front, back = f.get("Front", ""), f.get("Back", "")
        if not text(front) or not text(back):
            add("error", "empty Front or Back")
        else:
            answer = text(re.split(r"<small>", back)[0])  # the Why/Example line doesn't count
            if len(answer.split()) > 25:
                add("warn", f"back is {len(answer.split())} words: one fact per card")
            if YESNO.match(text(front)):
                add("warn", "front looks like a yes/no question")
            if LIST_ASK.search(text(front)):
                add("warn", "asks for a whole set or 'an example of': card one member, or turn it around")
            # a front that names its choices ("A or B?") must contain the answer, so skip it
            leaked = [] if re.search(r"\bor\b", text(front), re.I) else sorted(set(words(answer)) & set(words(text(front))))
            if leaked:
                add("warn", f"answer word(s) appear in the question: {', '.join(leaked)}")
        for name, val in f.items():
            if re.search(r"<(br|hr)\s*>", val):
                add("warn", f"{name}: close void tags (<br />)")

    types = [t for t in tags if t.startswith("type::")]
    if len(types) != 1:
        add("error", f"need exactly one type:: tag, found {len(types)}")
    if not any(t.startswith("src::") for t in tags):
        add("error", "missing src:: tag")
    if prefix and not any(t.startswith(prefix + "::") for t in tags):
        add("error", f"missing a {prefix}:: tag")
    return out


async def main():
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)
    prefix = args[args.index("--prefix") + 1] if "--prefix" in args else None
    strict = "--strict" in args
    def read():
        with open(args[0]) as f:
            return json.load(f)
    cards = await asyncio.to_thread(read)
    bad = False
    for i, c in enumerate(cards, 1):
        label = text(c.get("fields", {}).get("Front") or c.get("fields", {}).get("Text") or "")[:50]
        for sev, msg in lint(c, prefix):
            print(f"#{i} [{sev}] {msg}  ({label})")
            bad = bad or sev == "error" or strict
    print(f"{len(cards)} cards checked")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    asyncio.run(main())
