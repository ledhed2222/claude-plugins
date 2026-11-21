---
type: llm
focus: trace
arm: with-only
---
Look at every font pairing Claude planned. Judge the font families Claude planned: the ones it wrote into theme.json drafts, checked with `fetch_font.py --info` or named in its reply, whether or not the fetch then worked. If a fetch error made it fall back to the system font, judge the pairing it planned before that.

PASS if every planned body font is a sans-serif (for example IBM Plex Sans, Inter) and at least one pairing uses a monospace font for the label (for example IBM Plex Mono, JetBrains Mono).

FAIL if any planned pairing names a serif or display face for the body, or none has a monospace label.
