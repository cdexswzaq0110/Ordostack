# Codex Command: PLAN MODE

用途：把需求拆成可執行的 MVP 計畫。

---

## Trigger Prompt

```text
請依 codex-workflows/commands/plan.md 執行 PLAN MODE：

[需求]

先不要改檔。
```

---

## Objective

產出清楚、可測試、可分階段實作的計畫，避免 Codex 直接暴衝改檔。

---

## Prerequisites

- 讀 `AGENTS.md`。
- 讀 `memory-bank/current/projectbrief.md`。
- 讀 `memory-bank/current/tasks.md`。
- 若需求矛盾或缺少關鍵資訊，先問問題。

---

## Process

1. 說明我理解的需求。
2. 做啟動前檢查：
   - 這是真問題嗎？
   - 有更簡單做法嗎？
   - 會破壞什麼嗎？
3. 分析資料與流程。
4. 產出 PRD / SA / SD 摘要。
5. 切分 MVP 與延後項目。
6. 列出會修改或新增的檔案。
7. 列出實作步驟。
8. 定義測試方式。
9. 列出風險與回滾方式。

---

## Output Format

```markdown
## 我理解的需求

## 啟動前檢查

## 資料與流程分析

## MVP 功能切分

## 開發策略

## 本次修改範圍

## 實作步驟

## 測試方式

## 風險與注意事項

## 本次涵蓋 / 不涵蓋

## 下一步
```

---

## Verification

- 沒有直接改檔。
- 修改範圍清楚。
- 測試方式可執行。
- MVP 與非 MVP 有明確界線。

