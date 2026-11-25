#!/usr/bin/env bash
set -euo pipefail

for f in plugins/*/mise.toml; do
  mise -C "$(dirname "$f")" run ci
done
