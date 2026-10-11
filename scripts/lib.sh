#!/usr/bin/env bash
# shared helpers for hk-library scripts
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CACHE="${ROOT}/.cache"
mkdir -p "$CACHE"
