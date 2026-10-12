# hk-library

香港公共圖書館查詢用嘅 **skill 套件＋腳本**：附近分館、電腦空位、新書／電子書、借閱 Top 100，以及邊間分館有架上（HKPL webcat）。

英文版：[README.md](./README.md)

## 呢個係咩
- **可重用 agent skill**（`SKILL.md`）加 **scripts**，唔係獨立 bot。
- 優先用官方開放數據（`data.gov.hk`）；架上狀態用 **webcat + Playwright**。
- 對用戶回覆預設香港粵語，並標明來源。

## 快速開始
```bash
cd /workspace/projects/hk-library   # 或你嘅 clone 路徑

# 新書（中文成人外借 RSS）
bash scripts/new-add.sh chi-adult 15

# 書名搜尋
bash scripts/webcat-search-pw.sh "哈利波特 魔法石" --page-size 50 --max 50
# 後備：bash scripts/webcat-search.sh "哈利波特 魔法石"

# 館藏／架上（Playwright）
python3 -m venv .venv
.venv/bin/pip install playwright
.venv/bin/playwright install chromium
bash scripts/harry-potter-1-holdings.sh
# 或：bash scripts/webcat-item.sh chamo:3668181
```

## 腳本一覽
| 腳本 | 用途 |
|------|------|
| `scripts/new-add.sh` | 新到館 RSS（`chi-adult`／`chi-junior`／`eng-adult`／`eng-junior`） |
| `scripts/ebooks.sh` | 電子書清單（URL 可能要更新） |
| `scripts/top100.sh` | 借閱 Top 100 |
| `scripts/computers.sh` | 電腦室空位 |
| `scripts/libraries-nearby.sh` | 附近分館（暫為 stub，要接 CSDI） |
| `scripts/webcat-search.sh` | 目錄書名搜尋（curl HTML；結果有限） |
| `scripts/webcat_search.py` / `webcat-search-pw.sh` | Playwright 搜尋：每頁最多 50、可翻頁、出版項／索書號／架上提示 |
| `scripts/webcat_holdings.py` | Playwright 讀分館＋狀態 |
| `scripts/webcat-item.sh` | 單一 `chamo:` item 包裝 |
| `scripts/harry-potter-1-holdings.sh` | Demo：中文《神秘的魔法石》 |

## 明確唔做
唔登入讀者帳戶、唔代續借／預約／繳費、唔存借閱證號／密碼。

## 文件
- `SKILL.md` — agent 步驟（英文）
- `PRD.md` — 產品需求（中文草稿）
- `README.md` — 英文總覽
