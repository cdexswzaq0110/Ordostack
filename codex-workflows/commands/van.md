# Codex Command: VAN MODE

用途：檢查專案狀態，確認 Memory Bank 是否可用。必要時提出初始化或修復計畫。

---

## Trigger Prompt

```text
請依 codex-workflows/commands/van.md 執行 VAN MODE。
先不要改檔，只檢查狀態並回報缺口。
```

---

## Objective

確認 Codex 有足夠上下文可以安全協作，並找出缺失文件、矛盾資訊或下一步阻礙。

---

## Prerequisites

無。這是所有工作流的起點。

---

## Process

1. 讀取 `AGENTS.md` 與 `README.md`。
2. 檢查 `memory-bank/current/` 是否存在。
3. 檢查核心檔案：
   - `projectbrief.md`
   - `tasks.md`
   - `activeContext.md`
   - `progress.md`
   - `techContext.md`
   - `systemPatterns.md`
   - `runbook.md`
4. 摘要目前專案目標、狀態、限制。
5. 找出缺口與風險。
6. 若需要改檔，先列出修改範圍並等使用者確認。

---

## Output Format

```markdown
## VAN 檢查結果

## 已存在的上下文

## 缺口與風險

## 建議下一步

## 是否需要修改檔案
```

---

## Verification

- 已讀必要上下文。
- 沒有直接修改檔案。
- 明確列出缺口。
- 下一步可執行。

