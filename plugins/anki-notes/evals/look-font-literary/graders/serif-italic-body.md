---
type: llm
focus: trace
arm: with-only
---
Look at the body font of every font pairing Claude planned. Judge the font families Claude planned: the ones it wrote into theme.json drafts, checked with `fetch_font.py --info` or named in its reply, whether or not the fetch then worked. If a fetch error made it fall back to the system font, judge the pairing it planned before that.

PASS if every planned body font is a serif made for reading text (for example Literata, Source Serif 4, Lora, EB Garamond, PT Serif) with italics on.

FAIL if any planned pairing names a sans-serif, monospace or display face for the body, or leaves italics off.
