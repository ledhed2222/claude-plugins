---
type: llm
focus: trace
arm: with-only
---
The batch has one structural topic (the solera's tiers) and three abstract facts (the grape, fortification levels, sun-drying PX grapes). Look at every add_notes call.

PASS if any card carrying an <img> is about the solera, and no card about the grape, the fortification percentages or PX sun-drying has an image. A solera diagram is expected but not required.

FAIL if an image is put on any card that isn't about the solera, or an image is spread across the batch.
