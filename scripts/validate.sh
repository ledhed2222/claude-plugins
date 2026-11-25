#!/usr/bin/env bash
set -euo pipefail

claude plugin validate .
for p in plugins/*/; do
  claude plugin validate "$p"
done

for f in plugins/*/skills/*/SKILL.md; do
  if [[ "$(yq --front-matter=extract '.description | type' "$f")" != "!!str" ]]; then
    echo "$f: frontmatter has no string description" >&2
    exit 1
  fi
done
