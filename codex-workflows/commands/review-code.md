# Codex Command: REVIEW CODE

用途：以 code review 角度找 bug、回歸風險與缺測試。

---

## Trigger Prompt

```text
請依 codex-workflows/commands/review-code.md 審查以下變更：

[貼 diff 或指定檔案]
```

---

## Objective

先找會真的造成錯誤的問題，再談風格。

---

## Review Priority

1. 行為錯誤。
2. 安全問題。
3. 資料遺失或相容性破壞。
4. 缺少測試。
5. 過度設計或可讀性問題。

---

## Output Format

```markdown
## 【品味評分】

綠 / 黃 / 紅

## 【致命問題】

直接指出最糟的地方。

## 【為什麼這是問題】

說明它會造成什麼後果。

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

## Verification

- 有問題就附檔案與行號。
- 沒問題就明確說沒有發現高風險問題。
- 不把個人偏好包裝成 bug。

