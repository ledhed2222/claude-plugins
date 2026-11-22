---
type: llm
focus: trace
arm: with-only
---
Look at the stage plan Claude wrote. Notes 1001 and 1002 are leeches; 1003 is not.

PASS if every leech the plan rewrites carries the `rescued` tag in the plan, and a leech the plan keeps unchanged apart from a new mnemonic is not required to have it.

FAIL if a rewritten leech lacks the `rescued` tag, or the plan applies changes instead of only writing them for review.
