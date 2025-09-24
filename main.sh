#!/usr/bin/env bash
set -euo pipefail

# Prefer using uv if installed; fall back to system python
if command -v uv >/dev/null 2>&1; then
	# Ensure the environment is ready; this is fast and idempotent
	uv run --python 3.11 -- src/main.py "$@"
	cd public
	uv run --python 3.11 -m http.server 8888
else
	echo "uv command not installed in this system, exiting"
fi