# pyright: basic
"""Mechanical checks on drafted cards, before they are added.

Usage: python3 -I lint_cards.py <cards.json> [--prefix aie] [--skip yes-no,...] [--strict]

cards.json is a JSON list of cards, numbered from 1 in findings ("#3"):
  {"deck": ..., "stage": ..., "model": "Basic"|"Cloze"|..., "fields": {...}, "tags": [...]}

Every finding starts with a check id. --skip turns checks off, for a charter
whose Conventions has a "Lint skip:" line.

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

_YESNO = re.compile(r"^\s*(is|are|was|were|does|do|did|can|could|should|will|would|has|have|had)\b", re.I)
_LIST_ASK = re.compile(r"\b(name|list|give|state)\s+(all|the\s+(two|three|four|five|six|\d+))\b|\ban example of\b|\bgive an? example\b", re.I)
_STOP = {"which", "their", "about", "there", "these", "those", "would", "could", "other", "where", "while", "being", "after", "before"}


def text(html):
    html = re.sub(r"<br\s*/?>", " ", html or "")
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", html)).strip()


def _words(s):
    return [w for w in re.findall(r"[^\W\d_]{5,}", s.lower()) if w not in _STOP]


def lint(card, prefix=None, skip=()):
    out = []
    f = card.get("fields", {})
    model = card.get("model", "")
    tags = card.get("tags", [])

    def add(sev, check, msg):
        if check not in skip:
            out.append((sev, f"{check}: {msg}"))

    if model == "Cloze" or model.endswith(" · Cloze"):  # a deck theme's copy, see build_theme.py
        body = f.get("Text", "")
        nums = sorted({int(n) for n in re.findall(r"\{\{c(\d+)::", body)})
        if not nums:
            add("error", "cloze", "Cloze has no {{c1::...}} deletion")
        elif nums != list(range(1, len(nums) + 1)):
            add("error", "cloze", f"cloze numbers {nums} are not 1..n")
        for ans in re.findall(r"\{\{c\d+::(.*?)(?:::.*?)?\}\}", body):
            if len(text(ans).split()) > 6:
                add("warn", "long-answer", f"cloze answer is long ({len(text(ans).split())} words): split the note")
        if re.search(r"\{\{c\d+::\s*\}\}", body):
            add("error", "cloze", "empty cloze deletion")
    else:
        front, back = f.get("Front", ""), f.get("Back", "")
        if not text(front) or not text(back):
            add("error", "empty", "empty Front or Back")
        else:
            answer = text(re.split(r"<small>", back)[0])  # the Why/Example line doesn't count
            if len(answer.split()) > 25:
                add("warn", "long-answer", f"back is {len(answer.split())} words: one fact per card")
            if _YESNO.match(text(front)):
                add("warn", "yes-no", "front looks like a yes/no question")
            if _LIST_ASK.search(text(front)):
                add("warn", "whole-set", "asks for a whole set or 'an example of': card one member, or turn it around")
            # a front that names its choices ("A or B?") must contain the answer, so skip it
            leaked = [] if re.search(r"\bor\b", text(front), re.I) else sorted(set(_words(answer)) & set(_words(text(front))))
            if leaked:
                add("warn", "answer-in-question", f"answer word(s) appear in the question: {', '.join(leaked)}")
        for name, val in f.items():
            if re.search(r"<(br|hr)\s*>", val):
                add("warn", "void-tag", f"{name}: close void tags (<br />)")

    types = [t for t in tags if t.startswith("type::")]
    if len(types) != 1:
        add("error", "tags", f"need exactly one type:: tag, found {len(types)}")
    if not any(t.startswith("src::") for t in tags):
        add("error", "tags", "missing src:: tag")
    if prefix and not any(t.startswith(prefix + "::") for t in tags):
        add("error", "tags", f"missing a {prefix}:: tag")
    return out


def parse_cards(raw):
    """[(number, card)] from a JSON list."""
    return list(enumerate(json.loads(raw), 1))


async def read_cards(path):
    def read():
        with open(path) as f:
            return f.read()
    return parse_cards(await asyncio.to_thread(read))


async def main():
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)
    prefix = args[args.index("--prefix") + 1] if "--prefix" in args else None
    skip = args[args.index("--skip") + 1].split(",") if "--skip" in args else ()
    strict = "--strict" in args
    cards = await read_cards(args[0])
    bad = False
    for i, c in cards:
        label = text(c.get("fields", {}).get("Front") or c.get("fields", {}).get("Text") or "")[:50]
        for sev, msg in lint(c, prefix, skip):
            print(f"#{i} [{sev}] {msg}  ({label})")
            bad = bad or sev == "error" or strict
    print(f"{len(cards)} cards checked")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    asyncio.run(main())
