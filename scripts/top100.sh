#!/usr/bin/env bash
# Top 100 borrowed — hk-lcsd-lib-lib-top100
set -euo pipefail
URL="${HKPL_TOP100_URL:-https://www.lcsd.gov.hk/datagovhk/public_lib/lib_top100.json}"
curl -fsSL --max-time 45 "$URL" | python3 -c '
import json,sys
data=json.loads(sys.stdin.read())
items=data if isinstance(data,list) else data.get("data") or []
print(f"source=data.gov.hk/hk-lcsd-lib-lib-top100 count={len(items)}")
for i,it in enumerate(items[:100],1):
  if isinstance(it, dict):
    t=it.get("Title") or it.get("title") or it
    print(f"{i}. {t}")
'
