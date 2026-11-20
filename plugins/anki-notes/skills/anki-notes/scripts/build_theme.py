# pyright: basic
"""Turn a deck theme spec into note types, CSS and a preview, and check legibility.

Usage: python3 -I build_theme.py <theme.json> <out dir>

theme.json:
{
  "deck": "Spanish",
  "mood": "warm, unhurried",                  // the user's words, kept as a CSS comment
  "fonts": {                                  // null = the system font
    "body":   {"family": "Source Sans 3"},   // any Google Fonts family (OFL); fetched from npm
    "accent": {"family": "Fraunces", "weight": 400}
  },
  "light": {"bg": "#FBF3E8", "text": "#3B2316", "accent": "#A24A26", "rule": "#E8CDB4"},
  "night": {"bg": "#221A15", "text": "#F3E6D8", "accent": "#F0A07A", "rule": "#4A3A30"},
  "motion": false                             // opt-in: 120 ms answer fade, rescued shimmer
}

Writes to <out dir>:
  models.json   create_model arguments for "<deck> · Basic" and "<deck> · Cloze",
                with exactly the stock fields (Front/Back, Text/Extra), so the skill
                fills them as before and Change Note Type keeps review history
  theme.css     the stylesheet (also inside models.json)
  preview.html  a sample note, front and back, in light and night mode
  _<family>.woff2  each font, fetched from npm by fetch_font.py (next to preview.html, so
                the preview shows it); media.json lists them for store_media_file(path=...)

Exits 1 if any text color is below WCAG AA contrast (4.5:1) against its
background in either mode, or the spec is malformed. Standard library only.
"""
import asyncio
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))  # -I leaves this dir off sys.path
from fetch_font import fetch_font, slug  # noqa: E402

MIN_CONTRAST = 4.5
SYSTEM = '-apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif'
MODES = ("light", "night")
KEYS = ("bg", "text", "accent", "rule")


def luminance(hex_color):
    h = hex_color.lstrip("#")
    if len(h) != 6:
        raise ValueError(f"bad color {hex_color}")
    out = []
    for i in (0, 2, 4):
        c = int(h[i:i + 2], 16) / 255
        out.append(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4)
    r, g, b = out
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a, b):
    la, lb = sorted((luminance(a), luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def check(theme):
    problems = []
    for mode in MODES:
        pal = theme.get(mode) or {}
        missing = [k for k in KEYS if k not in pal]
        if missing:
            problems.append(f"{mode}: missing {', '.join(missing)}")
            continue
        for k in ("text", "accent"):
            r = contrast(pal[k], pal["bg"])
            if r < MIN_CONTRAST:
                problems.append(f"{mode}: {k} on bg is {r:.2f}:1, needs {MIN_CONTRAST}:1")
    return problems


def font_stack(font, fallback):
    return f'"{font["family"]}", {fallback}' if font else fallback


def font_file(font):
    return f"_{slug(font['family'])}.woff2"  # leading _ keeps Anki's Check Media from deleting it


def used_fonts(theme):
    fonts = theme.get("fonts") or {}
    return [f for f in (fonts.get("body"), fonts.get("accent")) if f and f.get("family")]


def css(theme):
    fonts = theme.get("fonts") or {}
    body, accent = fonts.get("body"), fonts.get("accent")
    lt, nt = theme["light"], theme["night"]
    faces = "".join(
        f'@font-face {{ font-family: "{f["family"]}"; src: url("{font_file(f)}"); font-weight: {f.get("weight", 400)}; font-display: swap; }}\n'
        for f in (body, accent) if f)
    stages = "".join(
        f'.deck-label[data-deck*="::{n:02d} "]::before {{ content: "{"●" * n}{"○" * max(0, 3 - n)} "; }}\n'
        for n in range(1, 10))
    motion = ""
    if theme.get("motion"):
        motion = """@media (prefers-reduced-motion: no-preference) {
  .answer { animation: fade-in 120ms ease-out; }
  .answer[data-tags~="rescued"]::before { animation: shimmer 900ms ease-out 1; }
}
@keyframes fade-in { from { opacity: 0; } to { opacity: 1; } }
@keyframes shimmer { 0% { opacity: .3; } 50% { opacity: 1; } 100% { opacity: .85; } }
"""
    return f"""/* {theme["deck"]} theme. Mood: {theme.get("mood") or "(none given)"}. Built by build_theme.py; edit theme.json, not this. */
{faces}.card {{
  --bg: {lt["bg"]}; --text: {lt["text"]}; --accent: {lt["accent"]}; --rule: {lt["rule"]};
  background: var(--bg); color: var(--text);
  font-family: {font_stack(body, SYSTEM)};
  font-size: 20px; line-height: 1.6; text-align: left;
  max-width: 38em; margin: 0 auto; padding: 1.25em;
}}
.card.nightMode, .card.night_mode, .night_mode .card {{
  --bg: {nt["bg"]}; --text: {nt["text"]}; --accent: {nt["accent"]}; --rule: {nt["rule"]};
}}
.deck-label {{ font-family: {font_stack(accent, "inherit")}; font-size: 14px; color: var(--accent); margin-bottom: 1em; }}
{stages}hr#answer {{ border: 0; border-top: 1px solid var(--rule); margin: 1em 0; }}
.answer b, .answer strong, .cloze {{ color: var(--accent); font-weight: 600; }}
.answer[data-tags~="rescued"]::before {{
  content: "rescued"; display: table; font-family: {font_stack(accent, "inherit")};
  font-size: 12px; color: var(--accent); border: 1px solid var(--accent);
  border-radius: 999px; padding: 0 .6em; margin-bottom: .6em;
}}
{motion}"""


LABEL = '<div class="deck-label" data-deck="{{Deck}}">{{Subdeck}}</div>'


def models(theme, stylesheet):
    deck = theme["deck"]
    return [
        {"model_name": f"{deck} · Basic", "in_order_fields": ["Front", "Back"], "is_cloze": False, "css": stylesheet,
         "card_templates": [{"Name": "Card 1",
                             "Front": LABEL + "\n<div class=\"question\">{{Front}}</div>",
                             "Back": "{{FrontSide}}\n<hr id=\"answer\" />\n<div class=\"answer\" data-tags=\"{{Tags}}\">{{Back}}</div>"}]},
        {"model_name": f"{deck} · Cloze", "in_order_fields": ["Text", "Extra"], "is_cloze": True, "css": stylesheet,
         "card_templates": [{"Name": "Cloze",
                             "Front": LABEL + "\n<div class=\"question\">{{cloze:Text}}</div>",
                             "Back": LABEL + "\n<div class=\"question\">{{cloze:Text}}</div>\n<hr id=\"answer\" />\n<div class=\"answer\" data-tags=\"{{Tags}}\">{{Extra}}</div>"}]},
    ]


def preview(theme, stylesheet, sample):
    def render(mode, side):
        cls = "card" + (" nightMode" if mode == "night" else "")
        label = f'<div class="deck-label" data-deck="{theme["deck"]}::{sample["stage"]}">{sample["stage"]}</div>'
        body = label + f'<div class="question">{sample["front"]}</div>'
        if side == "back":
            body += f'<hr id="answer" /><div class="answer" data-tags="{" ".join(sample.get("tags", []))}">{sample["back"]}</div>'
        return f'<div class="{cls}" style="border-radius:12px;margin:8px">{body}</div>'
    cells = "".join(f"<div>{render(m, s)}</div>" for m in MODES for s in ("front", "back"))
    # url("_x.woff2") resolves next to preview.html; copy the font files there to see them
    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8" /><title>{theme["deck"]} theme</title>
<style>{stylesheet}
body {{ margin: 0; background: #888; }} .grid {{ display: grid; grid-template-columns: 1fr 1fr; }}</style></head>
<body><div class="grid">{cells}</div></body></html>
"""


def _read_json(path):
    with open(path) as f:
        return json.load(f)


def _write(path, text):
    with open(path, "w") as f:
        f.write(text)


async def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    theme = await asyncio.to_thread(_read_json, sys.argv[1])
    problems = check(theme)
    if problems:
        sys.exit("not legible enough:\n  " + "\n  ".join(problems))
    out = sys.argv[2]
    await asyncio.to_thread(os.makedirs, out, exist_ok=True)
    stylesheet = css(theme)
    sample = theme.get("sample") or {"stage": "01 Basics", "front": "Which eval step costs more: inference or scoring?",
                                      "back": "<b>Inference.</b>", "tags": ["rescued"]}
    media = []

    async def get(font):
        dest = os.path.join(out, font_file(font))
        try:
            await fetch_font(font["family"], dest, font.get("weight", 400))
            media.append({"filename": font_file(font), "path": os.path.abspath(dest)})
        except (RuntimeError, ValueError, OSError, asyncio.TimeoutError) as e:
            print(f"warning: no font file for {font['family']} ({e}); the theme falls back to the system font")

    await asyncio.gather(*(get(f) for f in used_fonts(theme)))
    await asyncio.gather(
        asyncio.to_thread(_write, os.path.join(out, "media.json"), json.dumps(media, indent=1)),
        asyncio.to_thread(_write, os.path.join(out, "theme.css"), stylesheet),
        asyncio.to_thread(_write, os.path.join(out, "models.json"),
                          json.dumps(models(theme, stylesheet), ensure_ascii=False, indent=1)),
        asyncio.to_thread(_write, os.path.join(out, "preview.html"), preview(theme, stylesheet, sample)),
    )
    for mode in MODES:
        p = theme[mode]
        print(f"{mode}: text {contrast(p['text'], p['bg']):.1f}:1, accent {contrast(p['accent'], p['bg']):.1f}:1")
    print(f"wrote theme.css, models.json, preview.html, media.json and {len(media)} font file(s) to {out}")


if __name__ == "__main__":
    asyncio.run(main())
