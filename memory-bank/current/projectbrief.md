# Project Brief

## 專案名稱

Codex Agentic Coding Framework

## 要解決的問題

原專案是為 Cursor IDE 設計的 AI 協作開發框架，依賴 `.cursor/commands`、`.cursor/rules` 與 `.cursorrules`。Codex 不使用這些 Cursor 專用機制，因此需要改成 Codex 可以直接讀取與執行的文件型協作框架。

## 目標使用者

- 想用 Codex 協助開發的個人開發者。
- 想讓 Codex 先規劃、再實作、再驗證的專案維護者。
- 需要保存 AI 協作上下文的開發者。

## 核心使用情境

1. 使用者把資料夾交給 Codex。
2. Codex 先讀 `AGENTS.md` 與 Memory Bank。
3. 使用者用自然語言指定 VAN / PLAN / IMPLEMENT 等模式。
4. Codex 依命令文件執行，並在完成後更新 Memory Bank。

## MVP 必須完成

- `AGENTS.md` 作為 Codex 主要規則入口。
- `codex-workflows/commands/` 作為 Codex 可引用的命令文件。
- `README.md` 說明 Codex 使用方式。
- `memory-bank/current/` 改成符合 Codex 專案現況。
- 移除 Codex 後續不需要的 Cursor legacy 檔案。

## 非 MVP

- 不實作任何 IDE 外掛。
- 不假裝 Codex 支援 Cursor slash commands。
- 不建立 Docker、CI/CD 或雲端部署流程。
- 不導入新的程式框架。

## 成功標準

- 使用者能直接要求 Codex 讀 `AGENTS.md` 開始協作。
- 每個核心工作模式都有可引用的命令文件。
- 專案中不再保留 Codex 用不到的 Cursor 專用資料夾。
- Memory Bank 不再描述不存在的應用程式技術棧。

## 不做什麼

- 不保留 `.cursor/`。
- 不保留 `.cursorrules`。
- 不遷移非必要 persona 類指令。
- 不把文件框架改成可執行程式。

## 更新紀錄

- 2026-06-06: 從 Cursor-first 文件框架遷移為 Codex-first 文件框架。

