# Codex Command: API DESIGN

用途：在實作 API 前先定義邊界與資料契約。

---

## Trigger Prompt

```text
請依 codex-workflows/commands/api-design.md 設計以下 API：

[需求]

先不要改檔。
```

---

## Objective

產出可實作、可測試、錯誤處理明確的 API 設計文件。

---

## Prerequisites

- 明確知道使用者與資料來源。
- 已確認是否真的需要 API。
- 已確認權限與驗證需求。

---

## Process

1. 定義資源模型。
2. 設計 endpoint。
3. 定義 request body。
4. 定義 response body。
5. 定義 error response。
6. 定義驗證規則。
7. 定義狀態碼。
8. 定義權限需求。
9. 列出邊界條件。
10. 提供範例。

---

## Output Format

```markdown
## API 目標

## 資源模型

## Endpoint

## Request

## Response

## Error Response

## 驗證規則

## 狀態碼

## 權限需求

## 邊界條件

## 範例
```

---

## Verification

- 不混用不一致的命名。
- 錯誤格式一致。
- 可用測試驗證。
- 不暴露 secret 或內部細節。

