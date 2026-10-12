---
name: hk-library
description: >-
  Use when the user asks about Hong Kong public libraries: nearby branches,
  computer availability, new books/ebooks, top borrowed titles, or which
  branch has a title on the shelf (HKPL webcat).
---
# hk-library (Hong Kong Public Libraries skill)

Reusable skill package (not a dedicated bot). Prefer scripts for fetch/filter;
the assistant only judges and writes the user-facing answer (Hong Kong Cantonese)
with source tags.

## When to use
Nearby branches, facilities/computers, new arrivals, ebooks, borrowing Top 100,
shelf/holdings lookups, multi-branch coverage, short visit routes.

**Never** log into a patron account, renew, reserve, or pay fines.

## Layout
Git repo: `/workspace/projects/hk-library/`

- `scripts/` — callable helpers (bash/python)
- `PRD.md` — product scope
- `README.md` / `README.zh-HK.md` — human docs

## Workflow
1. Parse intent: location / facilities / lists / title holdings / multi-book route / wishlist.
2. Prefer **data.gov.hk** via scripts (or `@hkdata` for discovery). Cite dataset id and data date.
3. For shelf status: short-keyword webcat search → item URL → **Playwright** holdings script.
   Do not use brittle curl+regex on HTML as the primary holdings path.
4. Maps: multi-point maplink; single point Google Maps OK. State the centre used for “nearby”.
5. Charts: dark QuickChart (bg `#111827`, text `#e5e7eb`, grid `#374151`, Noto Sans CJK TC).
6. Reply in **Hong Kong Cantonese**. Tag every fact with one of:
   `data.gov.hk` / `webcat holdings` / `LCSD official site` / `unverified assistant knowledge`
   (Cantonese labels OK: `webcat 館藏頁` / `LCSD 官網` / `助手未核實知識`).
7. Cleanup: close browser tabs and idle processes you started.

## Scripts (run from repo root)
```bash
cd /workspace/projects/hk-library

bash scripts/libraries-nearby.sh "<lat>" "<lng>" [n]
bash scripts/computers.sh
bash scripts/new-add.sh [chi-adult|chi-junior|eng-adult|eng-junior] [n]
bash scripts/ebooks.sh [query]
bash scripts/top100.sh
bash scripts/webcat-search.sh "<short title keywords>"

# holdings (Playwright; needs .venv)
bash scripts/webcat-item.sh chamo:<id>
bash scripts/harry-potter-1-holdings.sh
.venv/bin/python scripts/webcat_holdings.py --search "哈利波特 魔法石" --pick 1
```

First-time Playwright setup:
`python3 -m venv .venv && .venv/bin/pip install playwright && .venv/bin/playwright install chromium`

Implement or extend scripts before inventing one-off loops. Filter/compute in script;
assistant writes the answer.

## Webcat rules
- Search with short keywords; PHRASE must match catalogue wording.
- Item URL: `https://webcat.hkpl.gov.hk/lib/item?id=chamo:<id>&theme=WEB`
- All copies: add `&showAll=true`
- Holdings table: `#tabContents-1 table.table` — branch = col 1, status = col 5
- Status examples: `館內架上` (on shelf), `到期日 YYYY-MM-DD` (on loan), `轉移中` (in transit)
- webcat is the catalogue site; Playwright is the automation tool.

## Out of scope
Patron login, renew/reserve/pay, storing card numbers/passwords, unverified claims
without a source tag.
