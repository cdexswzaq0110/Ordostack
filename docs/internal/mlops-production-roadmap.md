# MLOps 產品化路線圖

> **日期:** 2026-07-08
> **視角:** 資深 ML / MLOps 工程實務——把 OrdoStack 從本地 Demo 變成可上線、可維運、可持續改進的產品
> **對齊:** WBS 里程碑 M2（安全與生產前準備）、M3（Hosted Beta）、M4（ML 治理）

## 一句話結論

OrdoStack 的 ML 部分不需要更強的模型，需要的是**更完整的迴路**。模型只是一張類別乘數表——這在資料量 < 1000 筆時是正確的選擇；真正決定產品成敗的是資料迴路（收集 → 訓練 → 驗證 → 晉升 → 服務 → 監控）是否閉合、可重複、可回滾。本次已把迴路在本地閉合，上線工作是把同一條迴路搬到託管環境並加上監控。

## 現況盤點（2026-07-08 後）

本地迴路已閉合，每一步都有指令與測試：

```
執行紀錄（execution logs, MySQL）
  → scripts/export_duration_feedback.py        # 拉最近 N 天已完成任務的實際工時
  → ml-service/training/train_duration_model.py # 合併回饋資料，seed 固定，holdout 切分
      產出 duration_model.json + duration_metrics.json（樣本外 MAE vs 天真基線）
  → ml-service/training/promote_duration_model.py # 指標閘門：必須贏過基線、不得比現役模型退步 >5%
      更新 model_registry.json（版本化 artifact + active/archived 歷史）
  → POST /model/reload                          # 熱載入，不重啟服務
  → /model/info、/ready 回報現役模型版本與來源
```

安全網：artifact 缺失時回退決定性 heuristic，預測永遠有答案；ml-service 掛掉時 backend 回退 estimate-fallback。**這兩層降級是產品最重要的 ML 資產，任何改動都不得破壞。**

目前誠實的指標基線：holdout MAE 4.33 分鐘 vs 天真估時基線 7.33 分鐘（14 筆樣本、3 筆評估——樣本太少，數字只代表管線正確，不代表模型品質）。

## 差距分析：離「實際產品上線」還缺什麼

### 1. 資料層（最大瓶頸，先做）

| 缺口 | 說明 | 對策 |
| --- | --- | --- |
| 訓練資料量 | 14 筆種子資料，統計上無意義 | 上線初期以收集為目標：每個完成任務都寫入回饋；設定「≥300 筆才第一次真訓練」的紀律 |
| 無資料驗證 | 匯出的 CSV 沒有 schema/範圍檢查 | 訓練前加驗證步驟：estimated/actual > 0、類別白名單、離群值截斷（>480 分鐘） |
| 無預測日誌 | 線上預測沒有落盤，無法事後比對 | backend 在排程生成時把 (prediction, model_version, task_id) 寫入表，任務完成時自動配對 actual —— 這是未來所有評估的地基 |
| 隱私 | 訓練資料含用戶行為 | 訓練特徵已去識別化（無 title/user_id 進模型），維持此設計並寫進 SECURITY.md |

### 2. 模型層（刻意保持簡單）

- 現在的乘數表模型**不需要換**。換成 GBM/神經網路前必須先回答：「在真實回饋資料的 holdout 上，它贏過乘數表多少分鐘？」贏不到 2 分鐘就不值得增加維運複雜度。
- 該做的升級順序：全域模型 → 每用戶校正係數（單一 float，冷啟動用全域值）→ 再考慮更複雜模型。個人化係數的投報率遠高於換模型架構。
- confidence 目前是寫死常數（0.74/0.58/0.62/0.45）。改為由該類別的歷史誤差分布推導（如 1 - MAE/estimate），並在前端呈現。

### 3. 服務層（M3 之前必須完成）

| 項目 | 現況 | 上線要求 |
| --- | --- | --- |
| 部署 | 本地 Compose | 單 VM + Docker Compose 即可起步（產品規模不需要 K8s），加 systemd 自動重啟與 `docker compose pull && up -d` 部署腳本 |
| CI/CD | CI 跑測試 | 加上 image build + push 到 registry；main merge 觸發 staging 部署；prod 手動批准 |
| TLS/DNS | 無 | Caddy 或 nginx + Let's Encrypt（infra/nginx 已有雛形） |
| Secrets | .env 手工 | 最低限度：VM 上的受控 .env + 檔案權限；下一步 SOPS 或雲 secret manager |
| DB | 容器 MySQL 空密碼 | 上線前必改：專用密碼、非 root 用戶、每日備份到 off-host（S3/B2），**每月演練還原** |

### 4. 觀測層（沒有這個就不算上線）

- 現有：request ID、結構化請求日誌、health/ready。缺：指標、告警、儀表板。
- 最小可行監控（一天工作量）：Prometheus + Grafana 容器，三個服務各曝露 `/metrics`（fastapi instrumentator），核心指標：
  - 系統：p95 延遲、錯誤率、容器重啟數
  - **ML 專屬：預測請求數、artifact vs heuristic vs estimate-fallback 的比例**（fallback 比例上升 = 模型服務出問題的先行指標）
  - 產品：排程生成成功率、每日活躍任務數
- 模型監控（M4）：每週離線 job 比對「本週預測 vs 實際」滾動 MAE；類別分布 PSI 漂移檢查。觸發條件明確：滾動 MAE 比晉升時退步 >20% → 告警並考慮回滾（registry 已有 archived 版本，回滾 = 改 active + reload）。

### 5. 治理層（M4，資料量到位後才做）

- ClearML（docs/clearml-mlops.md 已規劃）此時才引入：experiment tracking + model registry 取代本地 JSON registry。**介面已對齊**：`model_registry.py` 的 `active_model_path()` 抽象讓後端換 registry 不動服務程式。SDK 端已於 v0.54.0 接上（選配 tracking＋晉升註冊，離線模式驗證），伺服器化時只需設定憑證。
- 每次晉升自動產出 model card（訓練資料量、日期範圍、指標、diff 對比前一版）——promote 腳本已留好 metrics 欄位，補一個 markdown 產生器即可。
- 影子部署：新模型先以 shadow 模式跑一週（預測寫日誌不回傳用戶），比較實際誤差後再晉升。這比 A/B 簡單且對單人團隊足夠。

## 上線路線（90 天務實版）

```
第 1-2 週  M2：安全審查（OWASP + 依賴掃描 + auth 流程審計）、DB 憑證硬化、
           預測日誌表（地基，越早開始累積越好）
第 3-4 週  M3 基礎:單 VM staging 環境、TLS、CI/CD 到 staging、off-host 備份 + 還原演練
第 5-6 週  監控三件套（Prometheus/Grafana/告警）、SLO 定義、負載測試基線
第 7-8 週  生產 auth 強化（session 管理、密碼重設）、Beta 用戶引入（10-50 人）
第 9-12 週 收集真實回饋資料 → 第一次真訓練 → shadow 驗證 → 晉升
           （此時 registry/promotion/reload 迴路直接複用，只是資料變真的）
```

## SLO 與成功指標

| 指標 | 目標 | 量測來源 |
| --- | --- | --- |
| API 可用性 | 99.5%（Beta 階段） | 監控 uptime |
| 排程生成 p95 | < 2s | 請求日誌 |
| 預測降級比例（heuristic/fallback） | < 5% | ml-service 指標 |
| **產品北極星：估時偏差中位數** | 逐月下降 | analytics（estimate drift） |
| 模型滾動 MAE vs 基線 | 模型持續優於天真估時 | 每週離線評估 job |

北極星是最後一列的前一項：**用戶的估時是否因為用了這個產品而變準**。模型 MAE 只是手段；如果乘數表就能讓用戶偏差下降，那就是對的模型。

## 明確不做（避免過度工程）

- 不上 Kubernetes——單 VM Compose 撐得起 Beta 到數千用戶。
- 不換深度模型/LLM——資料量與問題結構都不支持。
- 不自建 feature store——特徵只有 6 個欄位，CSV + 驗證足夠。
- 不做即時（online）訓練——每日/每週批次重訓已超過需求。
