# Runbook

## 目的

本 Runbook 說明如何使用與維護 Codex Agentic Coding Framework。

---

## 快速啟動

在 Codex 對話中輸入：

```text
請先閱讀 AGENTS.md、README.md、memory-bank/current/*，然後依 codex-workflows/commands/van.md 執行 VAN MODE。先不要改檔，只回報狀態。
```

---

## 開始新任務

```text
請依 codex-workflows/commands/task-init.md 整理以下想法，先不要改檔：

[你的想法]
```

確認後再要求 Codex 更新 Memory Bank。

---

## 規劃功能

```text
請依 codex-workflows/commands/plan.md 規劃以下需求，先不要改檔：

[需求]
```

大型任務必須先規劃，確認後再實作。

---

## 實作功能

```text
請依 codex-workflows/commands/implement.md 實作 Task-XXX。
只做 MVP，修改前先列出會動哪些檔案。
```

完成後要求：

- 執行可行的測試或驗證。
- 更新 `memory-bank/current/progress.md`。
- 更新 `memory-bank/current/tasks.md`。
- 做 Manual GC。

---

## 除錯

```text
請依 codex-workflows/commands/debug.md 修復以下問題：

[錯誤訊息]
[重現步驟]
[預期行為]
[實際行為]
```

如果 Codex 連續 2 次仍無法解決，要求它停止修改並回報目前證據與下一步選項。

---

## Code Review

```text
請依 codex-workflows/commands/review-code.md 審查以下變更：

[diff 或檔案路徑]
```

審查重點順序：

1. bug。
2. 安全問題。
3. 相容性破壞。
4. 缺少測試。
5. 過度設計。

---

## 維護檢查

定期檢查：

```text
請依 VAN MODE 檢查：
1. 是否有缺失的 Memory Bank 文件。
2. 是否有過時的 Cursor legacy 路徑。
3. 是否有未使用文件。
4. 是否需要更新 docs/decisions.md。
```

---

## 常見問題

### Codex 會自動識別 slash commands 嗎？

不會。本框架使用 Markdown 命令文件與自然語言提示。

### 為什麼刪除 `.cursor/`？

因為使用者已確認 Codex 後續不需要的檔案可以刪除，而且 `.cursor/` 是 Cursor 專用入口。

### 是否需要 Docker 或 CI/CD？

目前不需要。本專案是文件型協作框架。

