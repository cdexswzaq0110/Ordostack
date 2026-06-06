# Codex Command: REFLECT MODE

用途：完成一段工作後記錄教訓與改進。

---

## Trigger Prompt

```text
請依 codex-workflows/commands/reflect.md 針對剛完成的任務復盤。
```

---

## Objective

把開發過程中的問題、原因、解法與下次避免方式寫清楚。

---

## Prerequisites

- 任務已有實作或文件產出。
- 已知道測試或驗證結果。

---

## Process

1. 摘要完成內容。
2. 摘要驗證結果。
3. 記錄遇到的問題。
4. 分析原因。
5. 記錄下次避免方式。
6. 更新 `progress.md`。
7. 必要時更新 `docs/decisions.md`。

---

## Output Format

```markdown
## 完成內容

## 驗證結果

## 遇到的問題

## 原因

## 下次如何避免

## 已更新文件

## 下一步
```

---

## Verification

- 有具體教訓，不是空泛總結。
- 重要決策有落地到文件。
- 下一步清楚。

