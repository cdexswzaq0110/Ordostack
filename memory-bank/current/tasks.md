# Tasks

本檔是目前 Codex 協作框架的任務唯一真相來源。

---

## Active Tasks

目前沒有進行中的開發任務。

---

## Completed Tasks

### Task-001: 建立 Codex 主要入口

- 狀態：Completed
- 日期：2026-06-06
- 產出：
  - `AGENTS.md`
  - `README.md`
  - `COMMAND_TEMPLATE.md`

### Task-002: 建立 Codex 命令文件

- 狀態：Completed
- 日期：2026-06-06
- 產出：
  - `codex-workflows/README.md`
  - `codex-workflows/commands/*.md`

### Task-003: 移除 Cursor legacy 檔案

- 狀態：Completed
- 日期：2026-06-06
- 移除：
  - `.cursor/`
  - `.cursorrules`

### Task-004: 更新 Memory Bank

- 狀態：Completed
- 日期：2026-06-06
- 產出：
  - `memory-bank/README.md`
  - `memory-bank/current/projectbrief.md`
  - `memory-bank/current/techContext.md`
  - `memory-bank/current/systemPatterns.md`
  - `memory-bank/current/runbook.md`
  - `memory-bank/current/tasks.md`
  - `memory-bank/current/activeContext.md`
  - `memory-bank/current/progress.md`

### Task-006: 建立學習任務推薦 MVP

- 狀態：Completed
- 日期：2026-06-06
- 產出：
  - `app/index.html`
  - `app/styles.css`
  - `app/core.js`
  - `app/browser.js`
  - `app/manifest.webmanifest`
  - `app/service-worker.js`
  - `docs/product-spec.md`
  - `docs/release-checklist.md`
  - `README.md`
  - `.gitignore`
  - `tests/core.test.js`
- 驗收條件：
  - [x] 可新增自訂大項
  - [x] 可在大項內新增自訂細項
  - [x] 可刪除大項與細項
  - [x] 可依可用時間產生今日 Top 3 推薦
  - [x] 可標記細項完成 / 復原
  - [x] 可計算完成率、大項摘要與預估時間
  - [x] 核心推薦、增刪、migration 與統計邏輯有測試檔
  - [x] 有正式產品規格書
  - [x] 有上市前檢核清單
  - [x] 有英文 GitHub README
  - [x] 有 `.gitignore` 保護常見環境與私密檔案
- 測試方式：
  - 使用可執行 Node runtime 執行 `node tests/core.test.js`
  - 或開啟 `app/index.html` 手動驗證主要流程
- 備註：
  - 使用靜態 HTML / CSS / JavaScript，不導入框架或套件。
  - 資料儲存在瀏覽器 `localStorage`。
  - 已加入 PWA manifest 與 service worker；`file://` 開啟時 service worker 不會啟用。
  - 本機 `node.exe` 目前回報存取被拒；已改用 Node REPL MCP 驗證核心邏輯 7 項測試通過。

---

## Pending Tasks

### Task-005: 後續可選整理

- 狀態：Pending
- 優先級：Low
- 說明：若未來要把此框架發佈成正式模板，可再補：
  - Markdown lint。
  - 範例任務。
  - 壓縮版 quick-start。
  - Codex skill 或 plugin 設計。

---

## Task Template

```markdown
### Task-XXX: [名稱]

- 狀態：Pending | In Progress | Completed | Cancelled
- 優先級：High | Medium | Low
- 說明：
- 驗收條件：
  - [ ] 條件 1
  - [ ] 條件 2
- 修改範圍：
- 測試方式：
- 備註：
```
