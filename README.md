# hk-library

Skill package and scripts for Hong Kong Public Libraries questions: nearby branches,
computer availability, new arrivals / ebooks, Top 100 borrowed titles, and which
branch has a title on the shelf (HKPL webcat).

Chinese (Hong Kong) edition: [README.zh-HK.md](./README.zh-HK.md)

## What this is
- A **reusable agent skill** (`SKILL.md`) plus **scripts**, not a standalone bot.
- Official open data first (`data.gov.hk`); shelf status via **webcat + Playwright**.
- User-facing replies are meant to be in Hong Kong Cantonese, with source tags.

## Quick start
```bash
cd /workspace/projects/hk-library   # or your clone path

# New books (Chinese adult lending RSS)
bash scripts/new-add.sh chi-adult 15

# Title search
bash scripts/webcat-search.sh "哈利波特 魔法石"

# Holdings (Playwright)
python3 -m venv .venv
.venv/bin/pip install playwright
.venv/bin/playwright install chromium
bash scripts/harry-potter-1-holdings.sh
# or: bash scripts/webcat-item.sh chamo:3668181
```

## Scripts
| Script | Purpose |
|--------|---------|
| `scripts/new-add.sh` | New additions RSS (`chi-adult`, `chi-junior`, `eng-adult`, `eng-junior`) |
| `scripts/ebooks.sh` | Ebooks list (dataset URL; may need endpoint refresh) |
| `scripts/top100.sh` | Top 100 borrowed |
| `scripts/computers.sh` | Computer room availability |
| `scripts/libraries-nearby.sh` | Nearby branches (stub — wire CSDI points) |
| `scripts/webcat-search.sh` | Catalogue title search |
| `scripts/webcat_holdings.py` | Playwright holdings scrape |
| `scripts/webcat-item.sh` | Wrapper for one `chamo:` item |
| `scripts/harry-potter-1-holdings.sh` | Demo: Chinese HP1 (`chamo:3668181`) |

## Out of scope
No patron login, renew, reserve, pay fines, or storing library card credentials.

## Docs
- `SKILL.md` — agent recipe (English)
- `PRD.md` — product requirements (Chinese draft)
- `README.zh-HK.md` — this overview in Hong Kong Chinese
