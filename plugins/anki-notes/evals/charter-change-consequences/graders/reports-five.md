---
type: llm
focus: last_message
arm: with-only
---
The deck holds five vocabulary cards (madrugar, la sobremesa, aprovechar, el atasco, empeñarse en).

PASS if the reply says five existing cards fall outside the narrowed scope (or lists those five), offers to tag them `to-delete`, and asks before saving the charter or tagging anything.

FAIL if it doesn't report the affected cards, gives the wrong count, or says it already tagged or saved anything.
