---
type: regex
pattern: "Front\\\\?\"\\s*:\\s*\\\\?\"((?!Back)[^}])*Precision-Recall"
flags: i
match: not_contains
target: mock_calls
arm: with-only
---
