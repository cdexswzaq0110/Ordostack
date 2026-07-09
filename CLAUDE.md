# CLAUDE.md - OrdoStack

> **專案:** OrdoStack
> **描述:** Local-first 每日排程規劃器 — 任務、固定行程、排程生成、執行紀錄、工時預測
> **語言:** Python (FastAPI) + TypeScript (React/Vite)
> **階段:** Customer Demo MVP / Technical Preview（版本見 `VERSION`）
> **建立:** 2026-07-08

## 開發流程

遵循 `.claude/WORKFLOW.md` 的標準流程：

```
/task-next → /plan → /tdd → /verify
```

WBS 任務清單在 `.claude/taskmaster-data/wbs.md`，用 `/task-status` 查看進度。

## 專案規則

`.claude/rules/` 中的通用規則自動生效（coding-style、development-workflow、git-workflow、security、testing、performance、patterns、subagent-context）。

OrdoStack 專屬規則以下列文件為準（英文版為正式版本）：

- [docs/internal/AI_RULEBOOK.md](docs/internal/AI_RULEBOOK.md) — AI 協作規則：Accuracy First、範圍控制、安全規則、審查格式
- [docs/internal/DEVELOPMENT_RULEBOOK.md](docs/internal/DEVELOPMENT_RULEBOOK.md) — 分層架構、相容性、分支、埠號、健康檢查契約、測試與秘密政策
- [ORDOSTACK_PROJECT_SPEC.md](ORDOSTACK_PROJECT_SPEC.md) — 產品範圍、Non-Goals、Definition Of Done

## 架構速覽

```
Browser → web-dashboard :5173 → backend-api :8000 → MySQL :3306（host :3307）
                                      ├→ scheduler-service :8100
                                      └→ ml-service :8200
```

- `backend-api` 是唯一對外產品 API；dashboard 不直連 MySQL、scheduler、ml-service。
- 排程演算法只放 `scheduler-service`；工時預測只放 `ml-service`。
- 分層：routes（薄）→ services（商業邏輯）→ repositories（持久化）。
- Docker 用 MySQL，測試用 in-memory store。

詳見 [ARCHITECTURE.md](ARCHITECTURE.md)。重大技術決策記錄在 `docs/adr/`。

## 品質閘門（Verify 必跑）

快速閘門（commit 前）：

```powershell
python scripts\ponytail.py --include-compose-config
```

執行期閘門（Docker / DB / 部署變更後必跑）：

```powershell
docker compose up --build -d
python scripts\e2e_smoke.py
python scripts\browser_smoke.py
```

沒有跑過對應閘門，不能宣稱任務完成。

## 禁止事項

- 不使用付費 API — 本專案必須完全本地執行。
- 不提交 secrets、`.env`、token、ClearML/AWS 憑證。
- 不直接推送 `main`。
- 不為了讓 CI 通過而移除測試。
- 不破壞既有 endpoint、不擅自改名公開路由。
- 不改 Docker 埠號，除非同步更新 README、Compose 與健康檢查。
- 不在未經使用者以繁體中文確認前刪除任何檔案。
- 不建立重複檔案（v2、enhanced_、new_ 前綴）— 擴展現有檔案。

## 強制要求

- 每個 issue 使用一個短生命週期分支（`feature/`、`fix/`、`chore/`、`docs/` 前綴）。
- 保持 `main` 隨時可執行。
- 新增行為可能回歸時必須加測試；scheduler 演算法必須有單元測試。
- 變更完成後更新相關文件與 `CHANGELOG.md`。
- 健康端點必須回傳 `{"status": "ok", "service": "...", "version": "..."}`。

## 技術棧

| 元件 | 技術 |
| --- | --- |
| web-dashboard | React + Vite + TypeScript |
| backend-api / scheduler-service / ml-service | Python 3.11 + FastAPI |
| 資料庫 | MySQL 8（Alembic 遷移）；測試用 in-memory store |
| 執行環境 | Docker Compose（本地） |
| QA | pytest、e2e/browser smoke、visual regression、a11y/security audit |
