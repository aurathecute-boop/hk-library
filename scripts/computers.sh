#!/usr/bin/env bash
# Computer room availability — dataset hk-lcsd-lib-lib-computers
set -euo pipefail
# data.gov.hk resource often JSON; resolve via CKAN if URL changes
URL="${HKPL_COMPUTERS_URL:-https://api.data.gov.hk/v1/historical-archive/get-file?url=https%3A%2F%2Fwww.lcsd.gov.hk%2Fdatagovhk%2Fpublic_lib%2Flib_computers.json&time=latest}"
# fallback: try common path
if ! curl -fsSL --max-time 30 "$URL" 2>/dev/null | head -c 20 | grep -q .; then
  URL="https://www.lcsd.gov.hk/datagovhk/public_lib/lib_computers.json"
fi
curl -fsSL --max-time 45 "$URL" | python3 -c '
import json,sys
raw=sys.stdin.read()
try:
  data=json.loads(raw)
except Exception as e:
  print("FAIL parse:", e); sys.exit(1)
items=data if isinstance(data,list) else data.get("data") or data.get("results") or []
print(f"source=data.gov.hk/hk-lcsd-lib-lib-computers count={len(items)}")
for it in items[:50]:
  if isinstance(it, dict):
    name=it.get("Library_name") or it.get("library_name") or it.get("name") or "?"
    avail=it.get("Available") or it.get("available") or it.get("Computer_available") or it
    print(f"{name}\t{avail}")
'
