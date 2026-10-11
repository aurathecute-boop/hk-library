#!/usr/bin/env bash
# Ebooks list — hk-lcsd-lib-lib-ebook ; optional filter arg
set -euo pipefail
Q="${1:-}"
URL="${HKPL_EBOOK_URL:-https://www.lcsd.gov.hk/datagovhk/public_lib/lib_ebook.json}"
curl -fsSL --max-time 60 "$URL" | python3 -c '
import json,sys
q=(sys.argv[1] if len(sys.argv)>1 else "").lower()
data=json.loads(sys.stdin.read())
items=data if isinstance(data,list) else data.get("data") or []
print(f"source=data.gov.hk/hk-lcsd-lib-lib-ebook count={len(items)} filter={q!r}")
n=0
for it in items:
  if not isinstance(it, dict):
    continue
  t=str(it.get("Title") or it.get("title") or "")
  if q and q not in t.lower():
    continue
  print(t); n+=1
  if n>=40: break
' "$Q"
