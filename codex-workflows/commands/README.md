# Codex Commands Index

這裡放的是 Codex 可引用的命令文件。它們不是 IDE 內建 slash commands，而是「可直接叫 Codex 依照文件執行」的工作流規格。

使用方式：

```text
請依 codex-workflows/commands/plan.md 執行 PLAN MODE，先不要改檔：

[需求]
```

---

## Core Commands

| 文件 | 用途 |
| --- | --- |
| `van.md` | 檢查或初始化 Memory Bank |
| `task-init.md` | 建立高層任務與 PRD 草案 |
| `plan.md` | 拆解任務、WBS、風險與測試方式 |
| `creative.md` | 技術設計與架構決策 |
| `implement.md` | 實作 MVP |
| `debug.md` | 系統化除錯 |
| `write-tests.md` | 補測試 |
| `review-code.md` | 程式碼審查 |
| `api-design.md` | API 設計文件 |
| `task-next.md` | 選下一個最小可做任務 |
| `optimize-performance.md` | 效能分析與優化 |
| `reflect.md` | 復盤與教訓紀錄 |
| `archive.md` | 週期歸檔 |

---

## Rule Priority

當命令文件與其他文件有衝突時，優先順序：

1. 使用者最新明確要求。
2. `AGENTS.md`
3. 具體 command 文件。
4. `memory-bank/current/*`
5. 其他文件。

