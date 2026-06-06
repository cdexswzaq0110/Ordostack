# Codex Command: TASK NEXT

用途：從 Memory Bank 中選出下一個最小可做任務。

---

## Trigger Prompt

```text
請依 codex-workflows/commands/task-next.md 分析下一步。
先不要改檔。
```

---

## Objective

用「使用者價值 / 實作成本」排序，選出下一個最值得做的 MVP 任務。

---

## Prerequisites

- 讀 `memory-bank/current/tasks.md`。
- 讀 `memory-bank/current/activeContext.md`。
- 讀 `memory-bank/current/progress.md`。

---

## Process

1. 列出目前任務狀態。
2. 找出阻礙與依賴。
3. 依使用者價值與實作成本排序。
4. 選出下一個最小任務。
5. 列出完成定義。
6. 建議應使用 PLAN、CREATIVE、IMPLEMENT 或 DEBUG。

---

## Output Format

```markdown
## 目前狀態

## 可做任務

## 排序理由

## 建議下一個任務

## 完成定義

## 建議使用的模式
```

---

## Verification

- 不選被依賴阻塞的任務。
- 不把大型重構當成下一個 MVP。
- 排序理由明確。

