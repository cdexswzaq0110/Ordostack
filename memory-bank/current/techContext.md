# Technical Context

## 專案類型

文件型 Codex 協作開發框架。

本專案目前不是可執行應用程式，沒有前端、後端、資料庫、Docker 或 CI/CD 執行需求。

## 實際技術組成

| 類型 | 內容 |
| --- | --- |
| Codex 規則入口 | `AGENTS.md` |
| Codex 命令文件 | `codex-workflows/commands/*.md` |
| 使用說明 | `README.md` |
| 工作記憶 | `memory-bank/current/*.md` |
| 決策紀錄 | `docs/decisions.md` |
| 文件格式 | Markdown |

## 開發環境

- OS：Windows
- Shell：PowerShell
- Workspace：`C:\Users\student\Desktop\OrdoStack_Draft_Edition`

## Codex 使用方式

Codex 進入專案後：

1. 讀 `AGENTS.md`。
2. 讀 `README.md`。
3. 依任務讀 `memory-bank/current/*`。
4. 需要特定工作模式時讀 `codex-workflows/commands/[command].md`。

## 相依套件

無。

## 測試方式

本專案是文件框架，主要驗證方式：

- 檢查 Markdown 檔案是否存在。
- 搜尋是否仍有不應保留的 Cursor legacy 路徑。
- 確認命令文件可被自然語言引用。

## 限制

- Codex 不支援 Cursor 的 `.cursor/commands` 自訂 slash command。
- 本框架提供的是文件型工作流，不是 Codex 外掛。
- 若需要真正的 Codex 外掛或 skill，需要另開任務設計。

