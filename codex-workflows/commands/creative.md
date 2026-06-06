# Codex Command: CREATIVE MODE

用途：在實作前完成技術設計、資料結構與架構決策。

---

## Trigger Prompt

```text
請依 codex-workflows/commands/creative.md 為 Task-XXX 做技術設計。
先不要改檔。
```

---

## Objective

用最小必要設計降低實作風險，不追求過度架構。

---

## Prerequisites

- 已有明確任務或需求。
- 已讀 `tasks.md` 與相關程式碼。
- 若任務很小，可跳過本模式直接進 IMPLEMENT。

---

## Process

1. 定義問題。
2. 分析資料結構。
3. 界定模組責任。
4. 設計 API 邊界，如果需要。
5. 比較 2 到 3 個方案。
6. 選擇 MVP 方案。
7. 列出風險與測試策略。
8. 需要時寫入 `docs/decisions.md`。

---

## Output Format

```markdown
## 問題定義

## 資料結構

## 模組邊界

## API 邊界

## 方案比較

## 建議方案

## 測試策略

## 風險

## 是否寫入決策文件
```

---

## Verification

- 沒有導入不必要框架。
- 資料結構優先於程式細節。
- 設計能支撐 MVP。

