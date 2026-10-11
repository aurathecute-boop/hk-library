#!/usr/bin/env bash
# New additions — hk-lcsd-lib-lib-newadd
set -euo pipefail
URL="${HKPL_NEWADD_URL:-https://www.lcsd.gov.hk/datagovhk/public_lib/lib_newadd.json}"
curl -fsSL --max-time 45 "$URL" | python3 -c '
import json,sys
data=json.loads(sys.stdin.read())
items=data if isinstance(data,list) else data.get("data") or []
print(f"source=data.gov.hk/hk-lcsd-lib-lib-newadd count={len(items)}")
for it in items[:40]:
  if isinstance(it, dict):
    t=it.get("Title") or it.get("title") or it
    print(t if not isinstance(t,dict) else json.dumps(t,ensure_ascii=False))
'
