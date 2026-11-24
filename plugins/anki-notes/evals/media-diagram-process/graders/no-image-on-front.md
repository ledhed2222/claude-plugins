---
type: regex
pattern: "\"(Front|Text)\\\\?\"\\s*:\\s*\\\\?\"([^\"\\\\]|\\\\[^\"])*<img"
match: not_contains
target: mock_calls
arm: with-only
---
