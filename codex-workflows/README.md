# Codex Workflows

本資料夾提供可直接貼給 Codex 的工作模式提示。真正的行為規則仍以根目錄 `AGENTS.md` 為準。

逐一命令文件放在 `codex-workflows/commands/`。當你想讓 Codex 嚴格依某個模式執行時，優先引用該文件。

---

## 使用方式

在 Codex 對話中輸入：

```text
請依 AGENTS.md 的 [MODE] 執行：

[你的任務]
```

或指定單一命令文件：

```text
請依 codex-workflows/commands/implement.md 實作 Task-XXX。
修改前先列出會動哪些檔案。
```

如果是大型修改，先要求：

```text
先不要改檔，只給計畫、風險、測試方式與會修改的檔案。
```

---

## VAN MODE

用途：檢查專案狀態與 Memory Bank 完整性。

提示：

```text
請依 AGENTS.md 的 VAN MODE 檢查專案狀態。

請做：
1. 讀 AGENTS.md、README.md、memory-bank/current/*。
2. 檢查 Memory Bank 是否完整。
3. 摘要目前專案目標、任務、技術限制。
4. 找出缺口與風險。
5. 先不要改檔，只回報下一步。
```

---

## TASK INIT

用途：把新想法整理成專案簡報或 Epic。

提示：

```text
請依 TASK INIT 模式整理以下想法：

[貼上想法]

請輸出：
1. PRD 草案。
2. 使用者與使用情境。
3. MVP 必做與非 MVP。
4. 成功標準。
5. 不做什麼。
6. 需要我澄清的問題。

先不要改檔。
```

---

## PLAN MODE

用途：把需求拆成可執行計畫。

提示：

```text
請依 PLAN MODE 規劃這個需求：

[需求]

請包含：
1. 我理解的需求。
2. 啟動前檢查。
3. 資料與流程分析。
4. PRD / SA / SD。
5. MVP 功能切分與優先順序。
6. 本次修改範圍。
7. 實作步驟。
8. 測試方式。
9. 風險與回滾方式。
10. 本次涵蓋與不涵蓋。

先不要改檔。
```

---

## CREATIVE MODE

用途：在寫程式前做技術設計與決策。

提示：

```text
請依 CREATIVE MODE 為 Task-XXX 做技術設計。

請輸出：
1. 問題定義。
2. 資料結構。
3. 模組邊界。
4. API 邊界，如果需要。
5. 替代方案比較。
6. 建議方案。
7. 風險。
8. 是否需要寫入 docs/decisions.md。

先不要改檔。
```

---

## IMPLEMENT MODE

用途：依計畫實作 MVP。

提示：

```text
請依 IMPLEMENT MODE 實作 Task-XXX。

限制：
1. 只做 MVP。
2. 不加入未要求功能。
3. 不刪除未確認檔案。
4. 修改前先列出會動哪些檔案。
5. 完成後執行可行的測試。
6. 更新 memory-bank/current/progress.md 與 tasks.md。
7. 做 Manual GC。
```

---

## DEBUG MODE

用途：系統化修 bug。

提示：

```text
請依 DEBUG MODE 修復以下問題：

[錯誤訊息]
[重現步驟]
[預期行為]
[實際行為]

請先：
1. 找最小重現路徑。
2. 提出 1 到 3 個假設。
3. 驗證假設。
4. 修改最小範圍。
5. 補測試或說明無法補測原因。
```

---

## WRITE TESTS

用途：補單元、API 或整合測試。

提示：

```text
請依 WRITE TESTS 模式為以下功能補測試：

[功能或檔案]

請先列出：
1. 要測的行為。
2. 不測的範圍。
3. 測試資料。
4. 測試指令。

再實作最小必要測試。
```

---

## REVIEW CODE

用途：以 code review 角度找風險。

提示：

```text
請依 AGENTS.md 的 Code Review 固定格式審查以下變更：

[貼 diff 或指定檔案]

請優先找：
1. bug。
2. 行為回歸。
3. 相容性問題。
4. 缺少測試。
5. 過度設計。
```

---

## REFLECT MODE

用途：完成一段工作後記錄教訓。

提示：

```text
請依 REFLECT MODE 針對剛完成的任務復盤。

請輸出：
1. 完成了什麼。
2. 驗證了什麼。
3. 遇到什麼問題。
4. 原因是什麼。
5. 下次如何避免。
6. 是否需要更新 docs/decisions.md 或 memory-bank/current/*。
```

---

## ARCHIVE MODE

用途：里程碑完成後整理文件。

提示：

```text
請依 ARCHIVE MODE 整理目前週期。

請先列出：
1. 要歸檔的內容。
2. 要更新的文件。
3. 不會碰的範圍。
4. 風險。

等我確認後再改檔。
```
