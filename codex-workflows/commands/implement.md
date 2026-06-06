# Codex Command: IMPLEMENT MODE

用途：依已確認的計畫實作 MVP。

---

## Trigger Prompt

```text
請依 codex-workflows/commands/implement.md 實作 Task-XXX。
只做 MVP，修改前先列出會動哪些檔案。
```

---

## Objective

完成最小可用功能，並提供可驗證的結果。

---

## Prerequisites

- 任務已明確。
- 修改範圍已確認。
- 已讀相關程式碼與 Memory Bank。
- 若會刪檔或大重構，先取得使用者確認。

---

## Process

1. 列出會修改或新增的檔案。
2. 實作最小功能。
3. 補必要測試。
4. 執行可行的測試或驗證。
5. 更新 `memory-bank/current/tasks.md`。
6. 更新 `memory-bank/current/progress.md`。
7. Manual GC。
8. 回報涵蓋與不涵蓋。

---

## Output Format

```markdown
## 完成內容

## 修改檔案

## 驗證方式

## 測試結果

## Manual GC

## 本版涵蓋 / 不涵蓋

## 下一步
```

---

## Verification

- 功能可以跑或文件可直接使用。
- 沒有 placeholder。
- 沒有引入不必要依賴。
- 未測項目有說明原因。

