# WBS - OrdoStack

**建立日期:** 2026-07-08
**最後更新:** 2026-07-08（v0.52.0：ML 重訓迴路 + 前端 UX P0 完成）
**開發模式:** MVP
**專案描述:** Local-first 每日排程規劃器。目前為 Customer Demo MVP / Technical Preview，本 WBS 追蹤從 MVP 走向 public launch 的剩餘工作（來源：ORDOSTACK_PROJECT_SPEC.md「Remaining Gaps Before Public Launch」）。

---

## 任務清單

| # | 任務 | 狀態 | 優先級 | 依賴 | 預估 | 備註 |
|---|------|------|--------|------|------|------|
| 1.1 | MVP 核心功能（auth、tasks、events、schedule、analytics、export、ML 預測） | ✅ 完成 | 高 | - | - | 已實作，見 spec Implemented Scope |
| 1.2 | 本地品質閘門（ponytail、e2e/browser smoke、audits） | ✅ 完成 | 高 | - | - | 已實作 |
| 1.3 | Claude Code 思維架構整合（CLAUDE.md、.claude/、ADR、WBS） | ✅ 完成 | 中 | - | 4h | 2026-07-08 由 Godzilla-z 模板導入 |
| 1.4 | ML 本地重訓迴路（回饋匯出、holdout 評估、指標閘門晉升、熱載入） | ✅ 完成 | 高 | 1.1 | 6h | 2026-07-08，見 docs/internal/mlops-production-roadmap.md |
| 1.5 | 前端 UX P0（刪除防呆、誠實 model panel、Now 高亮、快捷鍵） | ✅ 完成 | 中 | 1.1 | 4h | 2026-07-08，見 docs/internal/frontend-ux-improvement-plan.md |
| 1.6 | 介面重設計 + 側邊欄視圖導覽（編輯風設計系統、六視圖、真實涵蓋率、死按鈕清除） | ✅ 完成 | 高 | 1.5 | 8h | 2026-07-09，v0.53.0 |
| 2.1 | 安全審查（load testing 前置：OWASP 檢查、依賴掃描、auth 流程審計） | ⏳ 待處理 | 高 | - | 8h | 可用 /verify 與 sunnydata-security skill |
| 2.2 | 負載測試基線（單機 Docker Compose 下的容量報告） | ⏳ 待處理 | 中 | 2.1 | 6h | |
| 3.1 | 生產級 auth：session 管理、帳號救援、管理端支援 | ⏳ 待處理 | 高 | 2.1 | 16h | |
| 4.1 | 託管部署：DNS、TLS、production secrets、監控基礎設施 | ⏳ 待處理 | 高 | 2.1, 3.1 | 24h | 需要雲端帳號決策（目前 Non-Goal） |
| 4.2 | Off-host 備份儲存與 production 還原演練 | ⏳ 待處理 | 高 | 4.1 | 8h | 本地備份腳本已存在 |
| 5.1 | Production ML model registry 與 promotion workflow | 🔄 進行中 | 中 | 4.1 | 12h | 本地 JSON registry + 指標閘門晉升 + /model/reload 已完成（1.4）；生產版（ClearML/雲端）待 M3 |
| 5.2 | ClearML agent 執行 | ⏳ 待處理 | 低 | 5.1 | 8h | 目前僅文件 |
| 6.1 | 外部行事曆整合（Google/Outlook） | ⏳ 待處理 | 中 | 3.1 | 16h | |
| 6.2 | Mobile app 實作 | ⏳ 待處理 | 低 | 3.1 | 40h+ | 目前為 placeholder |
| 6.3 | 前端 UX P1 殘項（經過時間計時器、預測偏差徽章、範圍化 refetch、App.tsx 分模組） | ⏳ 待處理 | 中 | 1.6 | 8h | 死按鈕/plan score/視圖導覽已於 1.6 完成 |
| 6.4 | 預測日誌表（線上預測落盤 + 實際值配對） | ⏳ 待處理 | 高 | 2.1 | 6h | ML 監控與再評估的地基，越早開始累積越好 |

### 狀態說明
- ✅ 完成
- 🔄 進行中
- ⏳ 待處理
- 🚫 阻塞
- ⏭️ 跳過

---

## 里程碑

| 里程碑 | 目標日期 | 包含任務 | 狀態 |
|--------|----------|----------|------|
| M1: Customer Demo MVP | 已達成 | 1.x | ✅ 完成 |
| M2: 安全與生產前準備 | 未定 | 2.x, 3.1 | ⏳ 待處理 |
| M3: Hosted Beta | 未定 | 4.x | ⏳ 待處理 |
| M4: ML 治理與整合 | 未定 | 5.x, 6.x | ⏳ 待處理 |

---

## 風險與阻塞

| 風險 | 影響 | 緩解策略 |
|------|------|----------|
| 託管部署需要雲端帳號與費用，目前為 Non-Goal | M3 無法啟動 | 先完成 M2；雲端決策由 owner 拍板後再開 4.x |
| 生產 auth 改動可能破壞現有 demo 流程 | 回歸 | 沿用既有測試閘門，先寫測試再改（/tdd） |
| ML registry 與 ClearML 缺乏實際運行環境 | 5.x 停留在文件 | 以本地 JSON artifact 流程為準，registry 延後 |
