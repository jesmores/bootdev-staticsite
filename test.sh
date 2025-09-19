#!/usr/bin/env bash
set -euo pipefail

if command -v uv >/dev/null 2>&1; then
	uv run --python 3.11 -- python -m unittest discover -s src
else
	python3 -m unittest discover -s src
fi