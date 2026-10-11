#!/usr/bin/env bash
# Placeholder: holdings for one item — prefer Playwright once flow is learned
set -euo pipefail
ID="${1:?usage: webcat-item.sh chamo:ID}"
ID="${ID#chamo:}"
URL="https://webcat.hkpl.gov.hk/lib/item?id=chamo:${ID}&theme=WEB"
echo "source=webcat 館藏頁"
echo "url=$URL"
echo "TODO: Playwright script to scrape branch/copy/status tables; do not rely on brittle curl+regex alone."
