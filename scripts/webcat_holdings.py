#!/usr/bin/env python3
"""Fetch HKPL webcat holdings (branch + status) via Playwright.

Usage:
  .venv/bin/python scripts/webcat_holdings.py --item chamo:3668181
  .venv/bin/python scripts/webcat_holdings.py --search "哈利波特 魔法石" [--pick 1]
  .venv/bin/python scripts/webcat_holdings.py --harry-potter-1
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from urllib.parse import quote

from playwright.sync_api import sync_playwright


DEFAULT_HP1_ITEM = "chamo:3668181"  # 哈利波特. 神秘的魔法石 / 彭倩文譯 / 2020 皇冠


def cell_text(td) -> str:
    div = td.query_selector("div")
    if div:
        return (div.inner_text() or "").strip()
    return (td.inner_text() or "").strip()


def parse_item_id(raw: str) -> str:
    raw = raw.strip()
    m = re.search(r"chamo:(\d+)", raw)
    if m:
        return m.group(1)
    if raw.isdigit():
        return raw
    raise SystemExit(f"bad item id: {raw!r}")


def item_url(item_id: str, show_all: bool = True) -> str:
    q = f"id=chamo:{item_id}&fromLocationLink=false&theme=WEB"
    if show_all:
        q += "&showAll=true"
    return f"https://webcat.hkpl.gov.hk/lib/item?{q}"


def scrape_holdings(page, item_id: str) -> dict:
    url = item_url(item_id, show_all=True)
    page.goto(url, wait_until="domcontentloaded", timeout=60000)
    page.wait_for_selector("#tabContents-1 table.table", timeout=30000)
    title_el = page.query_selector("h1.title")
    title = (title_el.inner_text() if title_el else "").strip()
    rows_out = []
    for tr in page.query_selector_all("#tabContents-1 table.table tbody tr"):
        tds = tr.query_selector_all("td")
        if len(tds) < 5:
            continue
        branch = cell_text(tds[0])
        call_no = cell_text(tds[1]) if len(tds) > 1 else ""
        status = cell_text(tds[4])
        collection = cell_text(tds[5]) if len(tds) > 5 else ""
        if not branch and not status:
            continue
        rows_out.append(
            {
                "branch": branch,
                "call_no": call_no,
                "status": status,
                "collection": collection,
            }
        )
    on_shelf = [r for r in rows_out if "館內架上" in r["status"]]
    on_loan = [r for r in rows_out if r["status"].startswith("到期日")]
    in_transit = [r for r in rows_out if "轉移中" in r["status"]]
    return {
        "source": "webcat 館藏頁",
        "item_id": f"chamo:{item_id}",
        "url": url,
        "title": title,
        "count": len(rows_out),
        "on_shelf_count": len(on_shelf),
        "on_loan_count": len(on_loan),
        "in_transit_count": len(in_transit),
        "on_shelf": on_shelf,
        "holdings": rows_out,
    }


def search_titles(page, query: str) -> list[dict]:
    # Prefer syndication-style query page; fall back to UI search
    enc = quote(query)
    url = (
        "https://webcat.hkpl.gov.hk/search/query?"
        f"match_1=MUST&field_1=title&term_1={enc}&sort=relevance&theme=WEB"
    )
    page.goto(url, wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(1500)
    hits = []
    # result links often point to /lib/item?id=chamo:...
    for a in page.query_selector_all("a[href*='chamo:']"):
        href = a.get_attribute("href") or ""
        text = (a.inner_text() or "").strip()
        m = re.search(r"chamo:(\d+)", href)
        if not m:
            continue
        iid = m.group(1)
        if any(h["item_id"] == f"chamo:{iid}" for h in hits):
            continue
        if not text or text in ("English", "中文"):
            continue
        hits.append({"item_id": f"chamo:{iid}", "title": text, "href": href})
        if len(hits) >= 20:
            break
    return hits


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--item", help="chamo:ID or numeric id")
    ap.add_argument("--search", help="title keywords")
    ap.add_argument("--pick", type=int, default=1, help="1-based hit to open after --search")
    ap.add_argument("--harry-potter-1", action="store_true", help="use known HP1 Chinese item")
    ap.add_argument("--json", action="store_true", help="print JSON only")
    ap.add_argument("--shelf-only", action="store_true", help="list on-shelf branches only")
    args = ap.parse_args()

    if args.harry_potter_1:
        item_id = parse_item_id(DEFAULT_HP1_ITEM)
    elif args.item:
        item_id = parse_item_id(args.item)
    elif args.search:
        item_id = None
    else:
        ap.error("need --item, --search, or --harry-potter-1")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            if item_id is None:
                hits = search_titles(page, args.search)
                if not hits:
                    print("no search hits", file=sys.stderr)
                    sys.exit(2)
                if not args.json:
                    print(f"source=webcat search hits={len(hits)} q={args.search!r}")
                    for i, h in enumerate(hits, 1):
                        print(f"{i}. {h['item_id']}  {h['title']}")
                idx = max(1, args.pick) - 1
                if idx >= len(hits):
                    sys.exit(f"--pick {args.pick} out of range ({len(hits)} hits)")
                item_id = parse_item_id(hits[idx]["item_id"])
            data = scrape_holdings(page, item_id)
        finally:
            browser.close()

    if args.json:
        out = data
        if args.shelf_only:
            out = {**data, "holdings": data["on_shelf"]}
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return

    print(f"source={data['source']}")
    print(f"title={data['title']}")
    print(f"item={data['item_id']}")
    print(f"url={data['url']}")
    print(
        f"copies={data['count']} on_shelf={data['on_shelf_count']} "
        f"on_loan={data['on_loan_count']} in_transit={data['in_transit_count']}"
    )
    rows = data["on_shelf"] if args.shelf_only else data["holdings"]
    for r in rows:
        print(f"{r['branch']}\t{r['status']}\t{r['collection']}")


if __name__ == "__main__":
    main()
