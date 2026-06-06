# Codex Command: OPTIMIZE PERFORMANCE

用途：用數據找效能瓶頸，再做最小優化。

---

## Trigger Prompt

```text
請依 codex-workflows/commands/optimize-performance.md 分析以下效能問題：

[症狀、指標或重現方式]
```

---

## Objective

先量測，再優化；避免憑直覺改大量程式碼。

---

## Prerequisites

- 有可觀察的效能症狀。
- 有測量方式，或先建立最小測量方式。
- 不為了效能犧牲可讀性，除非數據證明必要。

---

## Process

1. 定義效能問題與目標。
2. 找出量測方式。
3. 建立 baseline。
4. 找瓶頸。
5. 提出最小優化方案。
6. 實作後重新量測。
7. 記錄前後差異。

---

## Output Format

```markdown
## 效能問題

## Baseline

## 瓶頸分析

## 修改內容

## 優化後結果

## 風險

## 後續建議
```

---

## Verification

- 有前後數據。
- 沒有無根據的「應該變快」。
- 沒有引入難維護的複雜度。

