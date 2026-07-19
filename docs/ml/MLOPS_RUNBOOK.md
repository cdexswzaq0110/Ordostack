# MLOps Runbook — Duration Model 操作手冊

> 所有指令在 repo 根目錄執行（Windows PowerShell）。訓練依賴需先安裝：
> `python -m pip install -r ml-service\training\requirements-training.txt`

## 1. 完整生命週期一覽

```text
收集 (execution logs → /api/ml/duration-feedback 匯出)
→ 驗證 (validate_dataset.py，data contract 1.0.0)
→ 訓練 (train_linear_model.py / train_duration_model.py)
→ 比較 (compare_models.py，6 候選)
→ 評估 (holdout MAE/MedianAE/RMSE vs naive baseline)
→ 晉升 (promote_duration_model.py，三道 gate＋audit log)
→ 部署 (POST /model/reload 熱載入，或重啟容器)
→ 監控 (prediction logs 配對、/api/ml/prediction-accuracy)
→ 回滾 (rollback_duration_model.py)
```

## 2. 日常操作

### 2.1 匯出真實回饋資料

```powershell
python scripts\export_duration_feedback.py   # 或於 dashboard ML 頁面下載 CSV
# 輸出 schema 與訓練資料一致，放到 ml-service\training\data\duration_feedback.csv
```

### 2.2 驗證資料（訓練前必跑）

```powershell
python ml-service\training\validate_dataset.py
# exit 0 = 可訓練；報告在 training\artifacts\dataset_validation_report.json
```

### 2.3 訓練候選

```powershell
# 線性候選（預設 elastic-net；--estimator ridge 可切換）
python ml-service\training\train_linear_model.py --artifact-dir ml-service\training\artifacts\candidates\linear

# Production 系列（multiplier table）
python ml-service\training\train_duration_model.py
```

兩者皆會：先跑 data contract 驗證 → 依 seed 決定 holdout → 寫出 `duration_model.json`＋`duration_metrics.json`（含 schema_version、feature_names、dataset_checksum、source_commit_sha、python/library versions、prediction_bounds）。

### 2.4 比較候選

```powershell
python ml-service\training\compare_models.py
# 標 * 者為「可 serving 候選中 pooled MAE 最低」；輸出含 evidence 判定
```

### 2.5 晉升（含 gate）

```powershell
# 先 dry-run：評估所有 gate、不寫任何狀態
python ml-service\training\promote_duration_model.py --artifact <model.json> --metrics <metrics.json> --dry-run

# 正式晉升（三道 gate 全過才會執行）
python ml-service\training\promote_duration_model.py --artifact <model.json> --metrics <metrics.json>
```

Gate 順序：

1. **Evidence gate** — evaluation_rows ≥ 10 且 evaluation_mode = holdout，否則輸出
   `insufficient evidence for automatic promotion`（覆寫：`--allow-insufficient-evidence`，人為決策）
2. **Baseline gate** — model MAE 必須贏過 naive estimate
3. **Regression gate** — 不得比現任 active model 差超過 5%（2、3 覆寫：`--allow-regression`）

晉升動作：artifact 複製為版本化檔案 → registry **atomic 改寫**（temp file + `os.replace`）→ `promotion_audit.jsonl` 追加紀錄 →（若設定 ClearML）註冊模型。

### 2.6 熱載入

```powershell
curl -X POST http://localhost:8200/model/reload
# 回傳目前 active model 的 name/version/source
```

信任邊界：`/model/reload` 無認證，僅限 Compose 內部網路與本機使用；正式部署需加 token（見 roadmap）。

### 2.7 回滾

```powershell
python ml-service\training\rollback_duration_model.py              # 回上一版
python ml-service\training\rollback_duration_model.py --version 0.2.0   # 指定版本
curl -X POST http://localhost:8200/model/reload                    # 生效
```

回滾前會驗證目標 artifact 存在且為合法 JSON；失敗時 registry 完全不動。

## 3. 故障處理

| 情境 | 系統行為 | 操作 |
|---|---|---|
| artifact JSON 損毀 | serving 自動降級 heuristic（`fallback: true`） | 重新訓練或回滾；`/model/info` 確認 source |
| artifact schema major 不相容 | 同上，拒載 | 用相容版程式重新輸出 artifact |
| registry 損毀/缺失 | 落回預設 `duration_model.json` | 重新 promote 建 registry |
| ml-service 整個掛掉 | backend 回原始估時（`estimate-fallback`，8 秒 timeout） | `docker compose restart ml-service` |
| 訓練資料違反 contract | 訓練直接拒絕並列出違規列 | 依 validation report 修資料 |
| 晉升誤判 | audit log 可追溯每筆決策 | rollback＋reload |

## 4. 監控與樣本充分性

- Prediction log（MySQL `prediction_logs`）每筆記錄：model_name/version、raw 與 calibrated 預測、estimated、target_date；任務完成時回寫 actual_minutes 完成配對。
- `/api/ml/prediction-accuracy` 回傳 rolling model MAE vs estimate MAE、improvement、`sufficient_data`（< 10 筆配對時為 false）。
- Dashboard 在樣本不足時顯示「樣本不足，暫無法評判模型」而非百分比。
- **Drift 偵測未實作**（需基準資料量，見 [FUTURE_ML_ROADMAP.md](FUTURE_ML_ROADMAP.md)）。

## 5. ClearML（選用）

`clearml_utils.py` 在未安裝/未設定 ClearML 時為 no-op；設定後訓練與晉升會自動記錄 experiment 與 model。本專案不依賴 ClearML server 也能完整運作。
