# Decisions

本檔記錄此 Codex 協作框架的重要決策。只記錄會影響後續使用方式的事項。

---

## ADR-001: 從 Cursor-first 遷移為 Codex-first

- 日期：2026-06-06
- 狀態：已採用

### 背景

原專案以 Cursor IDE 為核心，依賴 `.cursor/commands`、`.cursor/rules` 和 `.cursorrules`。Codex 不使用 Cursor 的自訂 slash command 機制，因此需要改成 Codex 可讀、可執行的文件型工作流。

### 決策

採用以下 Codex-first 結構：

- `AGENTS.md` 作為 Codex 主要專案規則入口。
- `codex-workflows/README.md` 保存可直接貼給 Codex 的工作模式提示。
- `memory-bank/` 保留為長期上下文與任務狀態。
- 原 `.cursor/` 指令轉成 `codex-workflows/commands/`。
- Codex 不再需要的 `.cursor/` 與 `.cursorrules` 刪除。

### 原因

- Codex 會讀取專案中的 `AGENTS.md` 作為協作指令。
- 自然語言模式提示比假造 slash command 更符合 Codex 的實際使用方式。
- 逐一命令文件比保留 Cursor 專用資料夾更適合 Codex 後續使用。

### 後果

- 使用 Codex 時，以 `AGENTS.md` 為唯一主要規則來源。
- 使用者需用自然語言觸發 VAN / PLAN / IMPLEMENT 等模式。
- 原 Cursor persona 類指令未遷移，因為它們不是 MVP 開發協作流程的必要部分。
