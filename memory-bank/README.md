# Memory Bank

Memory Bank 是 Codex 協作開發框架的長期上下文資料夾。Codex 每次進入專案時，應先讀取 `AGENTS.md`，再讀取 `memory-bank/current/` 中與任務相關的文件。

---

## 目的

Memory Bank 用來解決 AI 協作中的三個問題：

1. 上下文容易遺失。
2. 任務狀態不容易追蹤。
3. 設計決策沒有沉澱。

本資料夾不是程式碼執行依賴，而是人與 Codex 的共享工作記憶。

---

## 結構

```text
memory-bank/
├── current/
│   ├── activeContext.md
│   ├── progress.md
│   ├── projectbrief.md
│   ├── runbook.md
│   ├── systemPatterns.md
│   ├── tasks.md
│   └── techContext.md
├── schemas/
│   └── *.schema.md
├── manifest.json
└── README.md
```

---

## Current 文件說明

| 檔案 | 用途 |
| --- | --- |
| `projectbrief.md` | 專案目標、使用者、MVP、成功標準 |
| `tasks.md` | 任務唯一真相來源 |
| `activeContext.md` | 當前工作焦點、風險、下一步 |
| `progress.md` | 修改紀錄、驗證紀錄、阻礙 |
| `techContext.md` | 實際技術環境與限制 |
| `systemPatterns.md` | 架構與協作模式 |
| `runbook.md` | 操作方式與故障排除 |

---

## Codex 使用規則

Codex 執行任務時：

1. 先讀 `AGENTS.md`。
2. 再讀 `memory-bank/current/tasks.md` 與 `activeContext.md`。
3. 根據任務讀取其他相關文件。
4. 完成一小段工作後更新 `tasks.md` 或 `progress.md`。
5. 重要決策寫入 `docs/decisions.md`。

---

## 工作模式對應

| 模式 | Memory Bank 行為 |
| --- | --- |
| `VAN MODE` | 檢查 current 文件是否完整 |
| `TASK INIT` | 建立或更新 `projectbrief.md` 與 `tasks.md` |
| `PLAN MODE` | 更新任務拆解與驗收條件 |
| `CREATIVE MODE` | 記錄設計決策，必要時更新 `docs/decisions.md` |
| `IMPLEMENT MODE` | 更新 `progress.md` 與任務狀態 |
| `DEBUG MODE` | 記錄根因、修法、回歸測試 |
| `REFLECT MODE` | 記錄教訓與下次避免方式 |
| `ARCHIVE MODE` | 將完成週期歸檔 |

---

## Manual GC

每完成一段工作後檢查：

- 是否有暫存檔。
- 是否有 debug script。
- 是否有未使用文件。
- 是否有過時說明。
- 是否有已不需要的 legacy 檔案。

刪除前要確認：

- 不是正式文件。
- 不是必要設定。
- 不是使用者仍需要的原始資料。

---

## 驗證方式

```text
請依 codex-workflows/commands/van.md 執行 VAN MODE，檢查 Memory Bank 是否完整。
```

