#!/usr/bin/env bash
# Nearby libraries — needs lat lng; uses CSDI libraries dataset if available locally via hkdata
set -euo pipefail
LAT="${1:?lat}"; LNG="${2:?lng}"; N="${3:-5}"
echo "source=data.gov.hk/hk-lcsd-csdi-libraries centre=${LAT},${LNG}"
echo "NOTE: resolve library points via hkdata catalog (hk-lcsd-csdi-libraries) then sort by haversine; wire full fetch when endpoint confirmed."
echo "maplink tip: https://www.maplink.hk/ (multi markers) or Google Maps directions"
python3 - << PY
import math
print(f"request nearest n=${N} of lat=${LAT} lng=${LNG} — implement point list from dataset next")
PY
