# Progress

## 2026-06-06

### 完成內容

將原 Cursor IDE 協作框架改成 Codex-first 協作框架。

### 新增

- `AGENTS.md`
- `codex-workflows/README.md`
- `codex-workflows/commands/README.md`
- `codex-workflows/commands/van.md`
- `codex-workflows/commands/task-init.md`
- `codex-workflows/commands/plan.md`
- `codex-workflows/commands/creative.md`
- `codex-workflows/commands/implement.md`
- `codex-workflows/commands/debug.md`
- `codex-workflows/commands/write-tests.md`
- `codex-workflows/commands/review-code.md`
- `codex-workflows/commands/api-design.md`
- `codex-workflows/commands/task-next.md`
- `codex-workflows/commands/optimize-performance.md`
- `codex-workflows/commands/reflect.md`
- `codex-workflows/commands/archive.md`
- `docs/decisions.md`

### 修改

- `README.md`
- `COMMAND_TEMPLATE.md`
- `memory-bank/README.md`
- `memory-bank/current/projectbrief.md`
- `memory-bank/current/techContext.md`
- `memory-bank/current/systemPatterns.md`
- `memory-bank/current/runbook.md`
- `memory-bank/current/tasks.md`
- `memory-bank/current/activeContext.md`
- `memory-bank/current/progress.md`

### 刪除

- `.cursor/`
- `.cursorrules`
- `.codegraph/` local index folder

### 驗證

- 已確認 `.cursor/` 不存在。
- 已確認 `.cursorrules` 不存在。
- 已清理非交付用 `.codegraph/` local index folder。
- 已用關鍵字搜尋確認實體 legacy 檔案不存在；剩餘 `.cursor` / `.cursorrules` 字樣僅作為遷移說明與刪除紀錄。
- 已確認 Codex 命令文件位於 `codex-workflows/commands/`。

### 不涵蓋

- 不建立 Codex 外掛。
- 不建立 Codex skill。
- 不建立 Docker、CI/CD 或可執行應用。

### 後續新增：學習任務推薦 MVP

依 `project-brie.md` 的 baseline，新增一個可直接用瀏覽器開啟的靜態 MVP。

### 新增

- `app/index.html`
- `app/styles.css`
- `app/core.js`
- `app/browser.js`
- `tests/core.test.js`

### 功能

- 新增學習任務。
- 設定分類、預估分鐘與優先級。
- 依今日可用時間推薦最多 3 個未完成任務。
- 標記任務完成或復原。
- 顯示完成率與分類摘要。
- 使用 `localStorage` 保留任務資料。

### 驗證

- 已新增 `tests/core.test.js`，覆蓋推薦、完成率與分類摘要邏輯。
- 本機 `node.exe` 執行時回報存取被拒。
- 已改用 Node REPL MCP 載入 `app/core.js`，完成 6 項核心邏輯測試並全數通過。
- 可用瀏覽器開啟 `app/index.html` 進行手動流程驗證。

### 不涵蓋

- 不做登入。
- 不做資料庫。
- 不做 AI 自動規劃。
- 不做行事曆整合。
- 不做 Docker / CI/CD。

### 後續修改：Newsprint UI redesign

依使用者提供的 Newsprint design system，將靜態 Web MVP 改成報紙版面風格。

### 修改

- `app/index.html`
- `app/styles.css`

### 視覺調整

- 新增 masthead、edition metadata、黑底 ticker 與 footer note。
- 改成高對比 off-white / ink black / editorial red 色系。
- 使用 sharp 90-degree borders，全域移除圓角。
- 使用 12 欄感的 editorial grid，加入明確直線與橫線分隔。
- 新增黑底 inverted progress section。
- 新增 drop cap、newsprint texture 與 hard offset shadow hover。
- 保留表單 label、語意區塊與鍵盤 focus 狀態。

### 驗證

- 已搜尋確認舊色票與 TODO/FIXME 未殘留於 `app/`。
- 已確認 CSS 內沒有 viewport-based font scaling，letter-spacing 保持 `0`。
- 已用 Node REPL MCP 重跑 6 項核心邏輯測試並全數通過。

### 不涵蓋

- 未加入外部 icon library。
- 未做自動瀏覽器截圖驗證，因目前環境沒有可用 Playwright。

### 後續修改：Notebook planner readability pass

依使用者回饋，將介面從報紙頭版感收斂成更像記事本 / 行程規劃工具。

### 修改

- `app/index.html`
- `app/styles.css`

### 視覺調整

- 移除大型報紙 masthead、黑底 ticker 與 footer note。
- 中文標題、label、任務文字改回系統中文字體。
- 英文短標籤與數字資料使用 Consolas / monospace 風格。
- 改成工具型 header、筆記本線條背景、清楚的表單與任務欄位。
- 降低標題尺寸與視覺戲劇性，提高掃描性與可讀性。

### 驗證

- 已用 Node REPL MCP 重跑 6 項核心邏輯測試並全數通過。

### 後續新增：自訂大項 / 細項與 PWA 外殼

依使用者需求，新增大項與細項任務層級，並調整手機 App 風格。

### 修改

- `app/index.html`
- `app/styles.css`
- `app/core.js`
- `app/browser.js`
- `tests/core.test.js`

### 新增

- `app/manifest.webmanifest`
- `app/service-worker.js`

### 功能

- 可用大 `+` 新增自訂大項，例如「研究所考試」。
- 可在每個大項內用小 `+` 新增細項，例如「線性代數」。
- 可刪除大項；刪除前會提醒該大項底下細項也會刪除。
- 可刪除單一細項。
- Top 3 推薦改為從所有未完成細項中挑選，並顯示所屬大項。
- 進度摘要改為依大項顯示完成數與總預估時間。
- 舊版 flat task localStorage 可 migration 成大項 / 細項結構。
- 加入 PWA manifest 與 service worker，讓 http/https 環境可作為輕量手機 App 安裝基礎。

### PM 參考方向

- 參考 Todoist 的 projects / subtasks / priority。
- 參考 TickTick 的 folder / list / section / task / subtask 階層與統計。
- 參考 Amazing Marvin 的大任務拆 checklist / subtasks 思路。

### 驗證

- 已用 Node REPL MCP 跑新版 7 項核心測試，全數通過。
- 本機 `node.exe` 仍因 WindowsApps 權限回報存取被拒。

### 不涵蓋

- 不做原生 iOS / Android 專案。
- 不做推播提醒、日曆同步、拖曳排序、雲端同步或 AI 排程。

### 後續修改：上市前產品化與正式文件

依使用者要求，將 UI 文案與文件調整成可與客戶對接的上市前版本。

### 修改

- `app/index.html`
- `app/browser.js`
- `memory-bank/current/progress.md`
- `memory-bank/current/activeContext.md`
- `memory-bank/current/tasks.md`

### 新增

- `docs/product-spec.md`
- `docs/release-checklist.md`

### 產品化調整

- 移除畫面上的內部實作提示，例如 `LocalStorage`、`No Login`。
- 將產品名稱調整為 `OrdoStack Draft Edition`。
- UI 文案改成產品使用者看得懂的正式語氣。
- Empty state 文案改成中性、簡短、客戶可見的版本。
- 補正式產品規格書與上市檢核清單。

### 驗證

- 已用 Node REPL MCP 重跑 7 項核心測試，全數通過。
- 已確認核心功能未因文案與文件更新受影響。

### 後續修正：移除資料結構文案與推薦清單對齊

依使用者回饋，修正正式產品 UI 中不應出現的資料結構詞與清單對齊問題。

### 修改

- `app/index.html`
- `app/browser.js`
- `app/styles.css`

### 修正內容

- 將畫面文案中的「大項 / 細項」改為正式產品語言「目標 / 任務」。
- 將 `Plan / Recommendation / Progress / Notebook` 等欄位標籤改成中文產品標籤。
- 推薦清單改用自訂 counter，不再使用瀏覽器預設 `ol` 編號，避免 `1.` 與任務內容不對齊。
- 更新 CSS / JS query version 為 `20260606-ui2`，降低 in-app browser 讀到舊檔的機率。

### 驗證

- 已掃描 `app/index.html`、`app/browser.js`、`app/styles.css`，使用者可見文案不再出現「大項 / 細項」。
- 已用 Node REPL MCP 重跑 7 項核心測試，全數通過。

### 後續修改：OrdoStack Draft Edition GitHub packaging

依使用者要求，將專案整理成英文 GitHub 專案。

### 修改

- `README.md`
- `.gitignore`
- `app/index.html`
- `app/manifest.webmanifest`
- `docs/product-spec.md`
- `docs/release-checklist.md`
- `memory-bank/current/activeContext.md`
- `memory-bank/current/progress.md`

### 內容

- 產品名稱統一為 `OrdoStack Draft Edition`。
- `初稿版` 英文定名為 `Draft Edition`。
- README 改為英文 GitHub 專案格式，包含 features、structure、usage、tests、privacy and secrets。
- `.gitignore` 新增環境檔、API key、token、credential、logs、cache、build output、local Codex/codegraph state 等忽略規則。
- 檢查目前 repo 沒有 `.env`、key、token、credential 類私密檔案。

### 驗證

- 已搜尋確認舊產品名稱已從 App、README 與正式文件中替換。
- 已搜尋確認目前未發現 `.env`、secret、token、key、credential 類檔案。

### 後續修改：Draft Edition README rewrite

依使用者貼上的 OrdoStack 長期願景 README，重寫根目錄 `README.md`。

### 修改

- `README.md`
- `memory-bank/current/progress.md`

### 內容

- 將 README 定位為 `OrdoStack Draft Edition`。
- 明確區分目前已完成的靜態 HTML / CSS / JavaScript Draft MVP 與未來 roadmap。
- 保留長期方向：React Native、FastAPI、MySQL、Scheduler、ML/DL、ClearML、Docker、AWS。
- 避免 README 誤導成上述長期技術已經實作。
- 補 Current Draft Scope、How to Run、Planned Architecture、Planned API Endpoints、Roadmap、Privacy and Secrets。

### 驗證

- 已檢查 README 內 roadmap 技術均標示為 planned / future / not implemented。
