#!/usr/bin/env bash
set -euo pipefail

# Prefer using uv if installed; fall back to system python
if command -v uv >/dev/null 2>&1; then
	# Ensure the environment is ready; this is fast and idempotent
	uv run --python 3.11 -- src/main.py "$@"
else
	python3 src/main.py "$@"
fi