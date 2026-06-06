# Codex Workflow Prompt Template

這是建立新 Codex 工作模式或任務提示時使用的模板。Codex 不依賴 Cursor slash commands，所以本模板要能被直接貼進 Codex 對話中使用。

---

## 0. Invocation

```text
請依 AGENTS.md 的 [MODE NAME] 執行以下任務：

[任務描述]

限制：
- [限制 1]
- [限制 2]

先不要改檔，除非我明確確認。
```

---

## 1. PLAN

### Objective

用一句話說明此模式要達成的結果。

### Prerequisites Check

- [ ] 需要讀哪些檔案？
- [ ] 需要確認哪些環境？
- [ ] 是否會修改超過 3 個檔案？
- [ ] 是否可能破壞向後相容？
- [ ] 是否需要使用者先確認？

### Data Flow

說明資料：

- 從哪裡來。
- 流到哪裡。
- 誰修改。
- 如何驗證。

---

## 2. DO

### Core Process

1. Analyze: 讀取必要上下文與限制。
2. Design: 產生最小可行設計。
3. Implement: 只做 MVP 所需修改。
4. Document: 更新 Memory Bank。

### Inputs

- `memory-bank/current/projectbrief.md`
- `memory-bank/current/tasks.md`
- 任務相關程式碼或文件

### Outputs

- 程式碼或文件變更。
- `memory-bank/current/progress.md` 更新。
- 必要時更新 `docs/decisions.md`。

---

## 3. CHECK

### Verification Checklist

- [ ] 結果符合使用者需求。
- [ ] 沒有引入不必要依賴。
- [ ] 沒有刪除未確認檔案。
- [ ] 可執行測試已執行。
- [ ] 未執行測試時已說明原因。
- [ ] Memory Bank 已更新。

---

## 4. ACT

### Finalization

交付時說明：

- 這次做了什麼。
- 修改哪些檔案。
- 如何執行或使用。
- 如何測試。
- 本版涵蓋什麼。
- 本版不涵蓋什麼。
- 下一步。

### Manual GC

檢查並回報：

- 是否留下暫存檔。
- 是否留下 debug script。
- 是否有不再使用的 import。
- 是否有不必要空資料夾。
- 是否需要後續刪除 legacy 內容。

