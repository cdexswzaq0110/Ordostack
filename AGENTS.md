# AGENTS.md - Codex 協作開發框架

本檔是 Codex 進入此專案後的主要協作規則。作用範圍是整個 repository。

核心目標：讓 Codex 以可追蹤、可測試、可回滾的方式協助開發；先理解資料與需求，再規劃，最後才實作。

---

## 1. Codex 入口規則

Codex 開始任何任務前，先讀：

1. `AGENTS.md`
2. `README.md`
3. `memory-bank/current/projectbrief.md`
4. `memory-bank/current/activeContext.md`
5. `memory-bank/current/tasks.md`
6. 其他與任務直接相關的檔案

如果 `memory-bank/current/` 不存在或核心檔案缺失，先進入 `VAN MODE` 檢查，不要直接開發。

---

## 2. 不可退讓的底線

### Accuracy First

- 能確定才下結論。
- 不確定就說「不知道」。
- 不編造不存在的檔案、指令、API、套件或部署狀態。
- 若發現前面判斷錯了，直接指出錯誤並給正確版本。

### Do Exactly What Was Asked

- 不擴題。
- 不加入未要求的功能。
- 不自行導入大型框架、Docker、CI/CD、OOP 或雲端部署。
- 不刪除使用者原始碼。
- 不做大規模重構，除非使用者明確要求。

### MVP First

開發優先順序：

1. 功能能跑。
2. 邏輯能看懂。
3. 有基本驗證方式。
4. 後續能重構。

第一階段避免：

- 太早 Docker 化。
- 太早 CI/CD。
- 太早寫複雜自動化腳本。
- 太早大量 logging。
- 太早強行 OOP。

---

## 3. 啟動前檢查

在設計或改程式前，Codex 必須先回答自己：

1. 這是真問題，還是臆想？
2. 有沒有更簡單的做法？
3. 會破壞既有使用方式嗎？

若任務有關鍵缺口，先問清楚。若缺口不影響 MVP，可以列出假設後做最小版本。

---

## 4. Plan First 規則

除非任務非常小，或使用者明確說「直接改」、「直接給程式碼」，否則先給計畫再實作。

需要先停下來列計畫的情況：

- 會修改超過 3 個檔案。
- 涉及架構、資料結構、API、資料庫或部署。
- 可能破壞向後相容。
- 需要刪除、搬移或大量重命名檔案。

計畫至少包含：

- 我理解的需求。
- 資料與流程分析。
- MVP 功能切分。
- 會修改或新增哪些檔案。
- 實作步驟。
- 測試方式。
- 風險與回滾方式。

---

## 5. Top-down 規劃順序

正式開發前，依序釐清：

```text
PRD -> SA -> SD -> Folder Structure -> API Design Doc
```

### PRD

- 專案解決什麼問題。
- 使用者是誰。
- 核心使用情境。
- MVP 必須完成的功能。
- 非 MVP 延伸功能。
- 成功標準。
- 不做什麼。

### SA

- 系統主要模組。
- 模組責任。
- 資料如何流動。
- 使用者操作流程。
- 外部服務或資料來源。
- 風險與限制。

### SD

- 系統架構。
- 模組關係。
- 資料結構。
- API 邊界。
- 錯誤處理。
- 設定管理。
- 測試策略。
- 部署邊界。

---

## 6. Bottom-up 開發順序

實作時由小到大：

```text
小功能 -> 小模組 -> 大模組 -> 系統整合 -> 部署
```

每完成一小段：

1. 執行最小驗證。
2. 更新 `memory-bank/current/progress.md` 或 `tasks.md`。
3. 做 Manual GC。
4. 說明本版涵蓋與不涵蓋。

---

## 7. 資料結構優先

寫程式前先釐清：

- 資料是什麼？
- 資料從哪裡來？
- 資料流到哪裡？
- 誰擁有資料？
- 誰修改資料？
- 資料生命週期是什麼？
- 有沒有狀態轉換？
- 有沒有重複資料？
- 有沒有可消除的特殊情況？

原則：

- 先資料結構，再寫程式。
- 用好的資料結構消掉特殊情況。
- 超過三層縮排，通常要重想。
- 10 行能解決，不寫 50 行。

---

## 8. Codex 工作模式

Codex 沒有 Cursor 的 `.cursor/commands` slash command 機制。本框架用自然語言觸發工作模式。

常用提示：

```text
請依 AGENTS.md 的 VAN MODE 檢查專案狀態。
請依 AGENTS.md 的 PLAN MODE 幫我規劃這個功能，先不要改檔。
請依 AGENTS.md 的 IMPLEMENT MODE 實作 Task-001。
請依 AGENTS.md 的 DEBUG MODE 修復這個錯誤。
請依 AGENTS.md 的 REVIEW CODE 格式審查這段變更。
```

模式定義：

| 模式 | 目的 | 主要輸入 | 主要輸出 |
| --- | --- | --- | --- |
| `VAN MODE` | 檢查或初始化 Memory Bank | 專案結構 | `memory-bank/current/*` 狀態 |
| `TASK INIT` | 建立高層任務 | 使用者目標 | `projectbrief.md`, `tasks.md` |
| `PLAN MODE` | 拆解任務與 WBS | PRD, tasks | 更新 `tasks.md` |
| `CREATIVE MODE` | 技術設計與決策 | tasks, constraints | 設計紀錄或 ADR |
| `IMPLEMENT MODE` | 實作 MVP | task, design | 程式碼、測試、progress |
| `DEBUG MODE` | 系統化除錯 | 錯誤訊息、重現步驟 | 修正與根因紀錄 |
| `WRITE TESTS` | 補測試 | 既有功能 | 單元或整合測試 |
| `REVIEW CODE` | 審查風險 | diff 或檔案 | findings |
| `REFLECT MODE` | 復盤 | progress, tasks | lessons learned |
| `ARCHIVE MODE` | 歸檔週期 | current memory | archive/docs |

詳細工作流提示放在 `codex-workflows/README.md` 與 `codex-workflows/commands/`。

---

## 9. Memory Bank 規則

`memory-bank/current/` 是目前週期的共享上下文。

核心檔案：

- `projectbrief.md`: 專案目標、範圍、成功標準。
- `tasks.md`: 任務唯一真相來源。
- `activeContext.md`: 當前焦點、風險、下一步。
- `progress.md`: 實作進度與驗證紀錄。
- `techContext.md`: 實際技術環境與限制。
- `systemPatterns.md`: 架構與協作模式。
- `runbook.md`: 操作與故障排除方式。

規則：

- 不要憑空覆寫 Memory Bank。
- 大修改前先說明會改哪些 Memory Bank 檔案。
- 每完成一個小功能後更新進度。
- 重要決策寫到 `docs/decisions.md` 或相關 Memory Bank 檔案。

---

## 10. 編碼規範

- 可讀性優先於聰明技巧。
- 命名要描述性。
- Early return 優先，減少巢狀。
- 函式短小，一個函式只做一件事。
- 不硬編碼 secret、token、API key。
- 不引入不必要依賴。
- 不新增 placeholder、半成品或無法執行的範例。

前端需求：

- 表單要有 label。
- 按鈕語意清楚。
- 基礎鍵盤操作不能失效。
- UI 不要為了展示而犧牲實際使用流程。

---

## 11. 測試規則

開發時依風險選擇測試層級：

1. 單元測試：小功能。
2. API 測試：endpoint。
3. 功能測試：主要使用流程。
4. 整合測試：跨模組流程。
5. 部署測試：後期才做。

每次交付要說明：

- 測試指令。
- 預期結果。
- 測試涵蓋什麼。
- 測試不涵蓋什麼。
- 如果未測，明確說原因。

---

## 12. Git 與檔案操作

如果此資料夾是 Git repo，改檔前先看：

```bash
git status
```

禁止在未確認時執行：

- `git reset --hard`
- `git clean`
- `git push --force`
- 刪除 branch
- 大量刪檔

刪除或大幅重構前，先列出項目與原因，等使用者確認。

---

## 13. Manual GC

每完成一段工作後檢查：

- 是否留下暫存檔。
- 是否留下 debug script。
- 是否有無用測試檔。
- 是否有不再使用的 import。
- 是否有過時註解。
- 是否有不必要空資料夾。
- 是否引入未使用依賴。

不要刪除：

- 正式測試。
- 正式文件。
- 必要設定檔。
- 使用者原本的程式碼。
- 尚未確認用途的檔案。

---

## 14. 回覆格式

除非任務很小，規劃或交付時使用：

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

## 15. Code Review 固定格式

使用者要求 review code 時，使用：

```markdown
## 【品味評分】

綠 / 黃 / 紅

## 【致命問題】

直接指出最糟的地方。

## 【為什麼這是問題】

說明後果。

## 【改進方向】

- 消除特殊情況
- 簡化資料結構
- 10 行變 3 行
- 降低縮排層數
- 保持向後相容

## 【建議修改版本】

給出可執行、可理解的版本。
```

---

## 16. Definition of Done

任務完成至少符合：

- 功能可以執行或文件可以直接使用。
- 有基本測試或驗證方式。
- 沒有 debug 垃圾檔。
- 沒有不必要大型重構。
- 有說明修改哪些檔案。
- 有說明如何執行或使用。
- 有說明本版涵蓋與不涵蓋。
- 重要決策已記錄。
- 沒有破壞既有使用方式。
- 沒有引入不必要依賴。
