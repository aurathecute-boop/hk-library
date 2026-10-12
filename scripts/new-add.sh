#!/usr/bin/env bash
# New additions via data.gov.hk dataset feeds (webcat RSS)
set -euo pipefail
CATEGORY="${1:-chi-adult}"  # chi-adult | chi-junior | eng-adult | eng-junior
N="${2:-15}"
case "$CATEGORY" in
  chi-adult) URL="https://webcat.hkpl.gov.hk/search/syndication?facet_format=book&facet_item_class=3&facet_lang=chi&sort=dateNewest&syndication=true&theme=WEB"; LABEL="成人外借（中文）";;
  chi-junior) URL="https://webcat.hkpl.gov.hk/search/syndication?facet_format=book&facet_item_class=11&facet_lang=chi&sort=dateNewest&syndication=true&theme=WEB"; LABEL="兒童及青少年外借（中文）";;
  eng-adult) URL="https://webcat.hkpl.gov.hk/search/syndication?facet_format=book&facet_item_class=3&facet_lang=eng&sort=dateNewest&syndication=true&theme=WEB"; LABEL="Adult lending (EN)";;
  eng-junior) URL="https://webcat.hkpl.gov.hk/search/syndication?facet_format=book&facet_item_class=11&facet_lang=eng&sort=dateNewest&syndication=true&theme=WEB"; LABEL="Junior lending (EN)";;
  *) echo "usage: new-add.sh [chi-adult|chi-junior|eng-adult|eng-junior] [n]"; exit 1;;
esac
echo "source=data.gov.hk/hk-lcsd-lib-lib-newadd category=$LABEL"
curl -fsSL -A "hk-library-skill/1.0" --max-time 45 "$URL" | python3 -c '
import sys,re,html
n=int(sys.argv[1]); xml=sys.stdin.read()
items=re.findall(r"<item>(.*?)</item>", xml, re.S|re.I)
print(f"count={len(items)} showing={min(n,len(items))}")
for block in items[:n]:
  t=re.search(r"<title>(.*?)</title>", block, re.S|re.I)
  d=re.search(r"<description>(.*?)</description>", block, re.S|re.I)
  title=html.unescape(re.sub(r"<!\[CDATA\[|\]\]>","",(t.group(1) if t else "")).strip())
  author=html.unescape(re.sub(r"<!\[CDATA\[|\]\]>","",(d.group(1) if d else "")).strip())
  print(f"- {title}" + (f"／{author}" if author else ""))
' "$N"
