# Codex Command: WRITE TESTS

用途：為既有功能補最小必要測試。

---

## Trigger Prompt

```text
請依 codex-workflows/commands/write-tests.md 為以下功能補測試：

[功能或檔案]
```

---

## Objective

用聚焦測試覆蓋核心行為與回歸風險。

---

## Prerequisites

- 先讀現有測試風格。
- 不導入新測試框架，除非專案完全沒有測試工具且使用者確認。
- 不為了覆蓋率寫無意義測試。

---

## Process

1. 找出現有測試工具與命令。
2. 列出要測的行為。
3. 列出不測的範圍。
4. 建立最小測試資料。
5. 實作測試。
6. 執行測試。
7. 更新 `progress.md`。

---

## Output Format

```markdown
## 測試目標

## 測試範圍

## 不測範圍

## 新增或修改測試

## 測試指令

## 測試結果
```

---

## Verification

- 測試可重複執行。
- 測試名稱描述行為。
- 測試失敗時能指出問題。

