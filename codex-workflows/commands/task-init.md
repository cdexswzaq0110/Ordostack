# Codex Command: TASK INIT

用途：把使用者的新想法整理成可規劃的高層任務或 PRD 草案。

---

## Trigger Prompt

```text
請依 codex-workflows/commands/task-init.md 執行 TASK INIT：

[貼上想法]

先不要改檔。
```

---

## Objective

將模糊需求整理成清楚的問題、使用者、範圍、MVP、成功標準與待澄清問題。

---

## Prerequisites

- 需求來源明確。
- 若需求不足，先問關鍵問題。
- 不要先做技術方案。

---

## Process

1. 摘要使用者想解決的問題。
2. 定義目標使用者與核心場景。
3. 切分 MVP 與非 MVP。
4. 定義成功標準。
5. 列出不做什麼。
6. 找出關鍵缺口。
7. 若使用者確認，可更新 `memory-bank/current/projectbrief.md` 與 `tasks.md`。

---

## Output Format

```markdown
## 我理解的需求

## PRD 草案

## 使用者與情境

## MVP / 非 MVP

## 成功標準

## 不做什麼

## 待澄清問題

## 建議下一步
```

---

## Memory Bank Updates

需要使用者確認後才更新：

- `memory-bank/current/projectbrief.md`
- `memory-bank/current/tasks.md`
- `memory-bank/current/activeContext.md`

