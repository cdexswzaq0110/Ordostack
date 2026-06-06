# Active Context

## Current Phase

IMPLEMENTED / VERIFY

## Current Focus

目前除了 Codex-first 文件型協作框架外，已新增一個靜態 Web MVP：

- `app/index.html`: 學習任務推薦入口。
- `app/core.js`: 任務建立、推薦、完成率與分類摘要邏輯。
- `app/browser.js`: 表單、渲染與 `localStorage` 互動。
- `tests/core.test.js`: 核心邏輯測試。
- UI 已從 Newsprint 報紙風格收斂成更可讀的手機 App / 記事本行程規劃工具風格。
- 已支援自訂大項、細項、增刪、完成狀態、Top 3 推薦與大項進度摘要。
- 已完成上市前產品化文案調整，產品名稱改為 `OrdoStack Draft Edition`。
- 已新增正式產品規格書與 release checklist。

## Recent Changes

- 新增 `AGENTS.md`。
- 改寫 `README.md`。
- 改寫 `COMMAND_TEMPLATE.md`。
- 新增 `codex-workflows/README.md`。
- 新增 `codex-workflows/commands/*.md`。
- 新增 `docs/decisions.md`。
- 刪除 `.cursor/`。
- 刪除 `.cursorrules`。
- 更新 Memory Bank 目前狀態。
- 新增學習任務推薦 MVP。
- 完成 Newsprint UI redesign。
- 依使用者回饋完成 Notebook planner readability pass。
- 新增自訂大項 / 細項任務管理與 PWA 外殼。
- 完成上市前產品化文案與正式文件補齊。
- 整理成英文 GitHub 專案：更新 README、產品規格、release checklist、`.gitignore` 與 App 命名。

## Open Risks

- 本框架是文件型工作流，不是 Codex 外掛。
- Codex 不會自動出現 slash command，需要使用者用自然語言引用命令文件。
- 若未來要支援外掛或 skill，需要另開設計任務。
- 本機 `node.exe` 目前回報存取被拒；核心邏輯已改用 Node REPL MCP 測試通過。
- `project-brie.md` 仍只是 baseline，信心等級為 `[L]`。
- 目前環境沒有可用 Playwright，因此尚未做自動瀏覽器截圖驗證。
- PWA service worker 需要 http/https；直接用 `file://` 開啟時不會註冊。

## Next Recommended Step

使用者可先手動驗證 MVP：

```text
開啟 app/index.html，新增任務，設定今日可用時間，檢查 Top 3 推薦與完成率。
```

## Last Updated

2026-06-06
