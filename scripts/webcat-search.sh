#!/usr/bin/env bash
# HKPL webcat RSS search — short keywords only
set -euo pipefail
Q="${1:?usage: webcat-search.sh \"short keywords\"}"
ENC=$(python3 -c 'import urllib.parse,sys; print(urllib.parse.quote(sys.argv[1]))' "$Q")
# syndication search; adjust if LCSD changes path
URL="https://webcat.hkpl.gov.hk/search/syndication?q=${ENC}&searchType=everything&sort=relevance"
curl -fsSL -A "hk-library-skill/1.0" --max-time 45 "$URL" | python3 -c '
import sys,re
xml=sys.stdin.read()
print("source=webcat RSS")
# crude item extraction
for m in re.finditer(r"<item>(.*?)</item>", xml, re.S|re.I):
  block=m.group(1)
  title=re.search(r"<title>(.*?)</title>", block, re.S|re.I)
  link=re.search(r"<link>(.*?)</link>", block, re.S|re.I)
  t=(title.group(1) if title else "").strip()
  l=(link.group(1) if link else "").strip()
  t=re.sub(r"<!\[CDATA\[|\]\]>","",t)
  print(f"{t}\n  {l}")
'
