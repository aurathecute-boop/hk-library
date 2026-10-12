---
name: hk-library
description: >-
  Use when the user asks about Hong Kong public libraries: nearby branches,
  computer availability, new books/ebooks, top borrowed titles, or which branch
  has a title on the shelf (HKPL webcat).
---
# hk-library (Hong Kong Public Libraries skill)

Reusable skill (not a dedicated bot). Automate with scripts; the assistant only judges and writes the Cantonese answer with source tags.

## When to use
Nearby branches, facilities/computers, new arrivals, ebooks, borrowing Top 100, shelf/holdings lookups, multi-branch coverage, short visit routes. **Never** log into a patron account, renew, reserve, or pay fines.

## Layout
Skill folder: `/workspace/projects/hk-library/`
- `scripts/` — callable helpers (bash/python)
- `PRD.md` — product scope (optional copy from `/workspace/hk-library-assistant/PRD.md`)

## Workflow
1. Parse intent: location / facilities / lists / title holdings / multi-book route / wishlist.
2. Prefer **data.gov.hk** via scripts (or `@hkdata` for discovery). Cite dataset id + data date.
3. For shelf status: short-keyword **webcat RSS** → item URL → **Playwright script** (after page is learned). Do not fragile-curl HTML as the primary path.
4. Maps: multi-point **maplink**; single point Google Maps OK. State the centre used for “nearby”.
5. Charts: dark QuickChart (bg `#111827`, text `#e5e7eb`, grid `#374151`, Noto Sans CJK TC).
6. Reply in **Hong Kong Cantonese**. Tag every fact: `data.gov.hk` / `webcat 館藏頁` / `LCSD 官網` / `助手未核實知識`.
7. Cleanup: close browser tabs and idle processes you started.

## Scripts (run from skill folder)
```bash
cd /workspace/projects/hk-library
bash scripts/libraries-nearby.sh "<lat>" "<lng>" [n]
bash scripts/computers.sh
bash scripts/new-add.sh
bash scripts/ebooks.sh [query]
bash scripts/top100.sh
bash scripts/webcat-search.sh "<short title keywords>"
# holdings (Playwright; needs .venv)
bash scripts/webcat-item.sh chamo:<id>
bash scripts/harry-potter-1-holdings.sh          # demo: HP1 神秘的魔法石
.venv/bin/python scripts/webcat_holdings.py --search "哈利波特 魔法石" --pick 1
```
First-time Playwright setup: `python3 -m venv .venv && .venv/bin/pip install playwright && .venv/bin/playwright install chromium`
Implement missing scripts before inventing one-off loops. Cross-bot rule: filter/compute in script; assistant writes the answer.

## Webcat rules
- RSS: short keywords; PHRASE must match catalogue wording.
- Item: `https://webcat.hkpl.gov.hk/lib/item?id=chamo:<id>&theme=WEB`
- webcat is the catalogue site; Playwright is the automation tool.

## Out of scope
Patron login, renew/reserve/pay, storing card numbers/passwords, unverified claims (e.g. “closure wave”) without a source tag.
