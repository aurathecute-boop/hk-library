#!/usr/bin/env bash
# HKPL webcat title search (HTML results via curl); short keywords
set -euo pipefail
Q="${1:?usage: webcat-search.sh \"short keywords\"}"
ENC=$(python3 -c 'import urllib.parse,sys; print(urllib.parse.quote(sys.argv[1]))' "$Q")
URL="https://webcat.hkpl.gov.hk/search/query?match_1=MUST&field_1=title&term_1=${ENC}&sort=relevance&theme=WEB"
echo "source=webcat search"
echo "url=$URL"
curl -fsSL -A "hk-library-skill/1.0" --max-time 45 "$URL" | python3 -c '
import sys,re
html=sys.stdin.read()
seen=set()
for m in re.finditer(r"href=\"([^\"]*chamo:(\d+)[^\"]*)\"[^>]*>(.*?)</a>", html, re.S|re.I):
  href, iid, text = m.group(1), m.group(2), re.sub(r"<[^>]+>","",m.group(3)).strip()
  if iid in seen or not text or len(text)<4: continue
  seen.add(iid)
  print(f"chamo:{iid}\t{text}")
  if len(seen)>=20: break
if not seen:
  print("(no chamo links parsed — try Playwright search)", file=sys.stderr)
'
