#!/usr/bin/env bash
# Playwright webcat search (up to 50/page + pagination)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
if [[ ! -x .venv/bin/python ]]; then
  echo "missing .venv — run: python3 -m venv .venv && .venv/bin/pip install playwright && .venv/bin/playwright install chromium" >&2
  exit 1
fi
exec .venv/bin/python scripts/webcat_search.py "$@"
