# Codex Command: ARCHIVE MODE

用途：里程碑完成後歸檔 Memory Bank 與決策資料。

---

## Trigger Prompt

```text
請依 codex-workflows/commands/archive.md 規劃歸檔目前週期。
先列出要動的檔案，等我確認後再改。
```

---

## Objective

把已完成週期的上下文保存起來，並讓下一個週期能乾淨開始。

---

## Prerequisites

- 已完成主要任務。
- `tasks.md` 與 `progress.md` 已更新。
- 使用者確認可以歸檔。

---

## Process

1. 列出要歸檔的文件。
2. 列出會新增的 archive 目錄。
3. 列出不會碰的範圍。
4. 等使用者確認。
5. 建立歸檔摘要。
6. 更新 `activeContext.md` 指向下一週期。
7. Manual GC。

---

## Output Format

```markdown
## 歸檔範圍

## 將新增或修改的檔案

## 不會碰的範圍

## 風險

## 需要確認
```

---

## Verification

- 不刪除未確認資料。
- 歸檔內容可追溯。
- 下一週期狀態清楚。

