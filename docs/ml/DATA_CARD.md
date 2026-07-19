# Data Card — Duration Training Dataset

- **檔案**:
  - `ml-service/training/data/duration_training_samples.csv`（14 筆 curated demo data）
  - `ml-service/training/data/external/sip_duration_tasks.csv`（4,227 筆，轉換自公開 SiP 資料集，見第 6 節）
  - 選用回饋檔 `duration_feedback.csv`（由 `/api/ml/duration-feedback` 匯出，gitignored）
- **Schema 版本**: `1.0.0`（定義於 `ml-service/app/data_contract.py`）
- **最後更新**: 2026-07-19

## 1. 資料來源與誠實聲明

- 14 筆種子資料為**手工整理的示範資料（curated demo data）**，不是真實使用者行為記錄。
- 任何基於此資料的評估數字都是**方向性參考**，不構成模型有效性的證據。系統各處（comparison 輸出、metrics、promotion gate）皆明確標示 `insufficient evidence for automatic promotion`。
- 真實資料來源：使用者完成任務後，執行紀錄（execution logs）計算出 `actual_minutes`，經 `/api/ml/duration-feedback` 匯出成與訓練資料同 schema 的 CSV，訓練時以 `--feedback` 併入。

## 2. 欄位定義（Data Contract）

| 欄位 | 型態 | 合法範圍 | 角色 | 缺值策略 |
|---|---|---|---|---|
| `category` | string | 非空字串；正規化為 `strip().lower()` | model input（one-hot／查表鍵） | 不允許缺值（validation error） |
| `estimated_minutes` | int | 1–1440 | model input | 不允許缺值 |
| `priority` | int | 1–5 | model input | 不允許缺值 |
| `difficulty` | int | 1–5 | model input | 不允許缺值 |
| `requires_focus` | bool | true/false | model input | 不允許缺值 |
| `actual_minutes` | int | 1–1440 | **target** | 不允許缺值 |

### 不得進入模型的欄位（excluded fields）

定義於 `data_contract.EXCLUDED_FIELDS`：

- `title` — 使用者私有文字，高維度、過擬合陷阱、隱私風險。API 會收到但 serving 絕不使用。
- `task_id` / `user_id` — 識別碼，模型使用會變成記憶而非泛化。

### 關於 `actual_minutes` 的雙重角色（重要）

- 訓練時 `actual_minutes` 是 target。
- Serving 時，若任務**已有部分執行紀錄**（`actual_minutes > 0`），預測會與其加權混合（blend weight 0.45，見 `app/predict.py`）。這是刻意的 execution-signal blending，不是 leakage；但**評估配對時必須使用 `raw_predicted_minutes`**（backend prediction log 已分開儲存 raw 與 calibrated/served 值），避免自我印證。

## 3. 驗證規則（可執行）

`python ml-service/training/validate_dataset.py` 會檢查：

- 空資料集（error）
- 欄位缺失（error）
- 非整數／非布林型態（error）
- 分鐘數 ≤ 0 或 > 1440（error）
- priority／difficulty 超出 1–5（error）
- `actual/estimated` 比值超出 [0.2, 5.0]（warning——可能是記錄錯誤）
- 完全重複列（warning）

報告輸出：`training/artifacts/dataset_validation_report.json`。訓練腳本在 validation error 時直接拒絕訓練。

## 4. 分割策略與已知限制

- Holdout：≥10 筆時固定 seed 洗牌後留 20%（`train_duration_model.split_rows`）；<10 筆退回 in-sample 並標記。
- 比較用 5-fold CV（`compare_models.py`），row-level 誤差跨 fold 匯總。
- **限制（誠實記錄）**：
  - 種子資料無 `user_id` 與時間戳 → 無法做 time-based 或 group split；同使用者相似任務可能同時落在 train/validation，CV 分數偏樂觀。
  - 14 筆遠低於比較可信門檻（30 筆，`MIN_ROWS_FOR_COMPARISON_EVIDENCE`）。
  - 資料分佈乾淨（ratio 0.8–1.37），真實資料的長尾（會議打斷、日間切換）未被代表。

## 5. 隱私

- 訓練資料不含姓名、email、任務標題等 PII。
- feedback export 僅含 6 個 contract 欄位。
- Prediction logs（MySQL `prediction_logs`）以 `user_id` 隔離，僅供本人查詢。

## 6. 外部資料集：SiP effort estimation dataset

- **來源**: [github.com/Derek-Jones/SiP_dataset](https://github.com/Derek-Jones/SiP_dataset)，Jones & Cullum (2019), *A conversation around the analysis of the SiP effort estimation dataset*, [arXiv:1901.01621](https://arxiv.org/abs/1901.01621)。一間英國軟體公司十年、12,299 筆真實商業任務，含逐任務估時與實際工時。作者公開發佈供分析，僅要求論文使用時告知。
- **原始檔 SHA-256**: `28621aa8b0ce05c270085a78e96a4d37f1bb39c1a5d260059ff3c197de961a4a`（`Sip-task-info.csv`）
- **轉換**: `ml-service/training/prepare_external_dataset.py`（可離線重跑，含來源 checksum）
- **欄位映射（刻意有損但誠實）**:

| Contract 欄位 | SiP 來源 | 映射 |
|---|---|---|
| `estimated_minutes` | HoursEstimate | ×60 四捨五入 |
| `actual_minutes` | HoursActual | ×60 四捨五入 |
| `category` | Category | 小寫化（development／management／operational）|
| `priority` | Priority（1–10）| `ceil(p/2)` → 1–5 |
| `difficulty` | **無此欄位** | 常數 3（中性；此特徵在本資料集無訊號） |
| `requires_focus` | **無此欄位** | 常數 false（同上） |

- **過濾**: 僅 `StatusCode=FINISHED`（實際值已定案）、估時與實際皆 >0 且 ≤1440 分鐘。12,299 → 4,227 筆（排除 7,349 筆未完成、723 筆超出 contract 上界）。
- **已知限制（誠實聲明）**:
  - 這是**一間軟體公司的任務分佈**，不是 OrdoStack 個人使用者的行為資料；category 集合（development/management/operational）與 demo 的個人類別（study/coding/…）不同——SiP 訓練的模型對個人任務**全部觸發 out-of-distribution 警示**，這是系統設計的正確行為。
  - difficulty／requires_focus 為常數，模型無法從中學到任何東西。
  - 2,893 筆 contract warning（極端 duration ratio 與 reduced-schema 下的重複列）被**保留**——真實估計誤差本來就是長尾，validation report 已截斷顯示（完整計數保留）。
  - 無時間欄位進入 contract schema，split 仍為 random——SiP 論文顯示估計行為隨時間變化，CV 分數可能偏樂觀。
