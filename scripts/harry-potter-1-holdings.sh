#!/usr/bin/env bash
# Convenience: Chinese Harry Potter 1 (神秘的魔法石) branch + status
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
exec bash "$ROOT/scripts/webcat-item.sh" --harry-potter-1 "$@"
