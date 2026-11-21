---
type: llm
focus: trace
arm: with-only
---
PASS if every theme.json Claude wrote sets both fonts (body and accent) to null so the device's own Japanese font is used, while the colors still differ between themes and fit the mood.

FAIL if any theme names a font family, or the themes are left uncolored.
