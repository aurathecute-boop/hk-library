#!/usr/bin/env bash
# Holdings for one webcat item (Playwright)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ID="${1:?usage: webcat-item.sh chamo:ID|--harry-potter-1}"
PY="$ROOT/.venv/bin/python"
if [[ ! -x "$PY" ]]; then
  echo "missing $PY — run: python3 -m venv .venv && .venv/bin/pip install playwright && .venv/bin/playwright install chromium" >&2
  exit 1
fi
if [[ "$ID" == "--harry-potter-1" || "$ID" == "harry-potter-1" ]]; then
  exec "$PY" "$ROOT/scripts/webcat_holdings.py" --harry-potter-1 "${@:2}"
fi
exec "$PY" "$ROOT/scripts/webcat_holdings.py" --item "$ID" "${@:2}"
