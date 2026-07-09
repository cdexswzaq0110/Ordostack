# VibeCoding 思維架構缺口分析

> **日期:** 2026-07-08
> **基準:** `claude-Godzilla-z` 專案思維架構（.claude 配置 + VibeCoding_Workflow_Templates 17 個模板）
> **對象:** OrdoStack（Customer Demo MVP / Technical Preview）

本文件記錄以 claude-Godzilla-z 的開發思維架構稽核 OrdoStack 的結果：哪些已覆蓋、哪些缺失、本次補齊了什麼、哪些刻意不做。

---

## A. Claude Code 配置層

| 項目 | 稽核前 | 處置 |
| --- | --- | --- |
| 根 `CLAUDE.md`（自動載入的專案指令） | ❌ 缺（AI_RULEBOOK / DEVELOPMENT_RULEBOOK 有內容但 Claude Code 不會自動載入） | ✅ 本次建立，整合兩份 rulebook、品質閘門與架構速覽 |
| `.claude/rules/`（8 條自動載入規則） | ❌ 缺 | ✅ 自 Godzilla-z 導入 |
| `.claude/agents/`（13 個專業 Agent） | ❌ 缺 | ✅ 導入 |
| `.claude/commands/`（17 個 Slash Command） | ❌ 缺 | ✅ 導入 |
| `.claude/skills/`（sunnydata + community） | ❌ 缺 | ✅ 導入 |
| `.claude/output-styles/`（15 個產出格式） | ❌ 缺 | ✅ 導入 |
| `.claude/taskmaster-data/`（WBS + project.json） | ❌ 缺 | ✅ 建立 OrdoStack 專屬 WBS（未複製 Godzilla 自身資料） |
| `.claude/settings.json` / hooks / statusline | ❌ 缺 | ✅ 導入（statusline 二進位檔與 debug 腳本未複製） |
| `.mcp.json` | ❌ 缺 | ⏭️ 不做 — MCP 為選用，含 API key 佔位，由使用者依 `MCP_SETUP_GUIDE.md` 自行設定 |

## B. VibeCoding 文件層（17 模板對照）

| # | 模板 | OrdoStack 對應 | 狀態 | 處置 |
| --- | --- | --- | --- | --- |
| 01 | 工作流總覽 | `.claude/WORKFLOW.md` | 本次導入 | ✅ |
| 02 | PRD | `ORDOSTACK_PROJECT_SPEC.md` | 已覆蓋 | 保留 |
| 03 | BDD 指南 | 無 | 缺 | ⏭️ 延後 — 現有 QA 以 pytest + smoke 為主，導入 Gherkin 屬新流程，應由 owner 決定 |
| 04 | ADR | 無 | **缺（關鍵）** | ✅ 建立 `docs/adr/`，回溯 4 個已定案決策 |
| 05 | 架構設計文檔 | `ARCHITECTURE.md` + `docs/system-analysis.md` | 已覆蓋 | 保留 |
| 06 | API 設計規範 | `docs/api.md` | 已覆蓋 | 保留 |
| 07 | 模組規格與測試 | `docs/algorithms.md` + 各服務 tests/ | 部分覆蓋 | 保留（演算法已有文件與單元測試） |
| 08 | 專案結構指南 | README 架構段 + `DEVELOPMENT_RULEBOOK.md` | 部分覆蓋 | 保留 |
| 09 | 依賴關係分析 | 無 | 缺 | ⏭️ 延後 — 5 個服務邊界簡單清晰，文件價值低於維護成本 |
| 10 | 類別關係 (UML) | 無 | 缺 | ⏭️ 延後 — 同上，程式碼分層已在 rulebook 明定 |
| 11 | Code Review 指南 | `AI_RULEBOOK.md` 審查格式 + `.claude/rules/` | 本次補強 | ✅ |
| 12/17 | 前端架構 / IA | 無 | 缺 | ⏭️ 延後 — dashboard 為單頁 MVP，正式化前端架構文件待功能擴張後再做 |
| 13 | 安全檢查清單 | `SECURITY.md` + `scripts/security_audit.py` | 已覆蓋 | 保留 |
| 14 | 部署運維指南 | `docs/deployment.md` + `docs/backup-restore.md` + `docs/observability.md` | 已覆蓋 | 保留 |
| 15 | 文檔維護指南 | `docs/documentation-completeness.md` + 檢查腳本 | 已覆蓋 | 保留 |
| 16 | WBS 開發計劃 | 無（spec 只有 gap 清單，無任務分解） | **缺（關鍵）** | ✅ 建立 `.claude/taskmaster-data/wbs.md`（M1-M4 里程碑） |

## C. Git 工作流

| 項目 | 稽核結果 |
| --- | --- |
| 分支策略 | ✅ 已有 `docs/branching-strategy.md`，實際歷史符合 issue-per-branch |
| PR 模板 / Issue 模板 / CI | ✅ `.github/` 已齊備 |
| Commit 品質標準（WHY/WHAT/IMPACT） | 本次由 `.claude/rules/git-workflow.md` 導入補強 |

## 結論

OrdoStack 的「產品與工程文件層」原本就相當完整（PRD、架構、API、QA、部署、文檔索引皆在）；主要缺口集中在「AI 協作思維架構層」：沒有 CLAUDE.md、沒有 .claude 配置、沒有 ADR、沒有 WBS。本次已全部補齊。刻意延後的項目（BDD、依賴/類別圖、前端架構文件、MCP 設定）都標了理由，避免為補文件而補文件。

## 驗證

```powershell
python scripts\docs_completeness_check.py --root .
python scripts\ponytail.py --include-compose-config
```
