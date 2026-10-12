#!/usr/bin/env python3
"""HKPL webcat title search via Playwright (page size up to 50 + pagination).

Usage:
  .venv/bin/python scripts/webcat_search.py "債券" [--page-size 50] [--max 100] [--json]
  .venv/bin/python scripts/webcat_search.py --query "bond investing" --pages 2
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from urllib.parse import quote

from playwright.sync_api import sync_playwright


BASE = "https://webcat.hkpl.gov.hk"


def search_url(query: str, page_number: int = 1) -> str:
    q = quote(query)
    return (
        f"{BASE}/search/query?match_1=MUST&field_1=title&term_1={q}"
        f"&sort=relevance&pageNumber={page_number}&theme=WEB"
    )


def item_url(chamo_id: str) -> str:
    return f"{BASE}/lib/item?id=chamo:{chamo_id}&theme=WEB"


def parse_result_count(text: str) -> dict:
    # e.g. 結果總數：110項，顯示 1 至 50項
    m = re.search(r"結果總數[：:]\s*(\d+)\s*項.*?顯示\s*(\d+)\s*至\s*(\d+)\s*項", text)
    if m:
        return {
            "total": int(m.group(1)),
            "from": int(m.group(2)),
            "to": int(m.group(3)),
        }
    m = re.search(r"Results?\s*[:：]?\s*(\d+)", text, re.I)
    if m:
        return {"total": int(m.group(1))}
    return {}


def shelf_hint(block_text: str) -> str | None:
    for line in block_text.splitlines():
        s = line.strip()
        if not s:
            continue
        if "館內架上" in s or "可供外借" in s or "on the shelf" in s.lower():
            return s
    return None


def scrape_page(page) -> tuple[list[dict], dict]:
    page.wait_for_selector("a.title[href*='chamo:']", timeout=45000)
    count_el = page.query_selector(".resultCount")
    count_info = parse_result_count(count_el.inner_text() if count_el else "")

    results: list[dict] = []
    seen: set[str] = set()
    # Each hit: climb from title link to a stable card ancestor
    for a in page.query_selector_all("a.title[href*='chamo:']"):
        href = a.get_attribute("href") or ""
        m = re.search(r"chamo:(\d+)", href)
        if not m:
            continue
        cid = m.group(1)
        if cid in seen:
            continue
        seen.add(cid)
        title = (a.inner_text() or "").strip()
        card = a.evaluate(
            """el => {
              let n = el;
              for (let i = 0; i < 8 && n; i++) {
                const c = (n.className || '').toString();
                if (c.includes('searchRecord') || c.includes('resultItem') || n.id === 'searchResults') return n.outerHTML ? n : n;
                n = n.parentElement;
              }
              return el.closest('.recordHighlight')?.parentElement || el.parentElement;
            }"""
        )
        # Prefer locating via JS handle on parent of recordHighlight
        rh = a.evaluate_handle(
            "el => el.closest('.recordHighlight') || el.parentElement"
        )
        fields: dict[str, str] = {}
        try:
            for tr in rh.query_selector_all("table tr"):
                lab = tr.query_selector("td.label")
                cells = tr.query_selector_all("td")
                if not lab or len(cells) < 2:
                    continue
                key = (lab.inner_text() or "").strip()
                val = (cells[1].inner_text() or "").strip()
                if key and val:
                    fields[key] = val
        except Exception:
            pass

        block_text = ""
        try:
            parent = a.evaluate_handle(
                """el => {
                  let n = el.closest('.recordHighlight');
                  return (n && n.parentElement) || el.parentElement;
                }"""
            )
            block_text = parent.inner_text() or ""
        except Exception:
            block_text = a.evaluate(
                "el => (el.closest('.recordHighlight')?.parentElement || el.parentElement)?.innerText || ''"
            ) or ""

        # Author often appears as a bare line under title before 出版項
        author = None
        lines = [ln.strip() for ln in block_text.splitlines() if ln.strip()]
        if lines:
            for ln in lines[1:6]:
                if ln in fields.values() or ln.startswith(tuple(fields.keys())):
                    break
                if ln in ("預約", "加到館藏選單") or "館內架上" in ln or "可供外借" in ln:
                    break
                if ln.startswith("出版") or ln.startswith("索書"):
                    break
                if len(ln) < 80 and not ln.startswith("http"):
                    author = ln
                    break

        results.append(
            {
                "item_id": f"chamo:{cid}",
                "title": title,
                "url": item_url(cid),
                "author": author,
                "publication": fields.get("出版項") or fields.get("Publication"),
                "call_no": fields.get("索書號") or fields.get("Call Number"),
                "series": fields.get("叢書名") or fields.get("Series"),
                "fields": fields,
                "shelf_hint": shelf_hint(block_text),
            }
        )
    return results, count_info


def ensure_page_size(page, size: int) -> None:
    sel = page.query_selector("#search-pagesize")
    if not sel:
        return
    cur = sel.input_value()
    if cur == str(size):
        return
    # Only values the OPAC offers
    allowed = {"5", "10", "20", "30", "40", "50"}
    if str(size) not in allowed:
        raise SystemExit(f"page-size must be one of {sorted(allowed)}")
    with page.expect_navigation(wait_until="domcontentloaded", timeout=60000):
        page.select_option("#search-pagesize", str(size))


def run(query: str, page_size: int, max_results: int, max_pages: int | None) -> dict:
    all_rows: list[dict] = []
    meta: dict = {"query": query, "page_size": page_size, "pages_fetched": 0}
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page_num = 1
        total = None
        while True:
            if max_pages is not None and page_num > max_pages:
                break
            if len(all_rows) >= max_results:
                break
            page.goto(search_url(query, page_num), wait_until="domcontentloaded", timeout=60000)
            ensure_page_size(page, page_size)
            rows, count_info = scrape_page(page)
            if page_num == 1:
                meta["result_count"] = count_info
                total = count_info.get("total")
            if not rows:
                break
            all_rows.extend(rows)
            meta["pages_fetched"] = page_num
            # stop if last page
            if total is not None and len(all_rows) >= total:
                break
            if count_info.get("to") and total and count_info["to"] >= total:
                break
            # no next page link
            if not page.query_selector("a[href*='pageNumber=']"):
                break
            page_num += 1
        browser.close()
    all_rows = all_rows[:max_results]
    meta["returned"] = len(all_rows)
    meta["source"] = "webcat 搜尋頁 (Playwright)"
    return {"meta": meta, "results": all_rows}


def main() -> None:
    ap = argparse.ArgumentParser(description="HKPL webcat search (Playwright)")
    ap.add_argument("query_pos", nargs="?", help="title keywords")
    ap.add_argument("--query", "-q", help="title keywords")
    ap.add_argument("--page-size", type=int, default=50, help="5–50 (OPAC max 50)")
    ap.add_argument("--max", type=int, default=50, help="max results to return")
    ap.add_argument("--pages", type=int, default=None, help="max pages to fetch")
    ap.add_argument("--json", action="store_true", help="JSON output")
    args = ap.parse_args()
    query = args.query or args.query_pos
    if not query:
        ap.error("query required")
    data = run(query, args.page_size, args.max, args.pages)
    if args.json:
        json.dump(data, sys.stdout, ensure_ascii=False, indent=2)
        print()
        return
    m = data["meta"]
    rc = m.get("result_count") or {}
    print(f"source={m['source']}")
    print(f"query={m['query']!r} page_size={m['page_size']} pages={m['pages_fetched']} returned={m['returned']}"
          + (f" total={rc.get('total')}" if rc.get("total") is not None else ""))
    for i, r in enumerate(data["results"], 1):
        extra = []
        if r.get("publication"):
            extra.append(r["publication"])
        if r.get("call_no"):
            extra.append(f"索書號 {r['call_no']}")
        if r.get("shelf_hint"):
            extra.append(r["shelf_hint"])
        line = f"{i}. {r['title']}  [{r['item_id']}]"
        print(line)
        print(f"   {r['url']}")
        if extra:
            print(f"   {' | '.join(extra)}")


if __name__ == "__main__":
    main()
