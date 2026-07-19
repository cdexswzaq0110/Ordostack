# Model Card — Task Duration Prediction

- **最後更新**: 2026-07-18
- **Serving 程式**: `ml-service/app/predict.py`
- **共用契約**: `ml-service/app/data_contract.py`（schema `1.0.0`）

## 1. 任務定義

- **問題型態**: Regression（迴歸）。輸入任務屬性，輸出預期實際耗時（分鐘，1–480 clamp）。
- **Input features**: `category`、`estimated_minutes`、`priority`、`difficulty`、`requires_focus`。
- **Target**: `actual_minutes`（由執行紀錄計算）。
- **主要指標**: MAE（分鐘）——誤差單位直觀、對離群值比 RMSE 穩健；輔以 Median AE、RMSE。
- **Baseline**: naive estimate（直接使用使用者自己的 `estimated_minutes`）。模型存在的意義就是打敗它。

## 2. 三層模型階梯（實際 serving 順序）

| 層 | 模型 | 定位 | 何時使用 |
|---|---|---|---|
| 1 | `local-duration-regressor` 0.2.0（**multiplier table**） | **Production**。按 category 統計 actual/estimated 平均比值（clamp 0.75–1.45），difficulty/priority/focus 為人工設定權重。誠實定位：**統計查表＋規則修正，不是學習型迴歸模型** | registry active 或預設 artifact |
| 2 | `duration-linear` 0.3.0（**ElasticNet, linear-json**） | **候選**。StandardScaler＋ElasticNet(α=0.1, l1=0.5)，以純 JSON 係數匯出，runtime 無需 scikit-learn | 通過 promotion gate 後（目前被 evidence gate 擋下，見下） |
| 3 | `heuristic-duration` 0.1.0 | **Fallback**。寫死的 category multiplier＋規則 | artifact 缺失／損毀／schema 不相容時 |

Backend 另有第四層：ml-service 整個不可達時回傳原始估時（`estimate-fallback`）。

## 3. 最新評估結果（2026-07-18, seed 42）

### 5-fold CV（14 筆，row-level 誤差跨 fold 匯總）

| 候選 | Pooled MAE | Median AE | RMSE | vs naive | 可 serving |
|---|---|---|---|---|---|
| elastic-net | **3.77** | 3.22 | 4.87 | +73.3% | ✅（linear-json） |
| ridge-regression | 4.65 | 4.34 | 5.44 | +67.1% | ✅（linear-json） |
| gradient-boosting | 8.27 | 7.74 | 9.36 | +41.5% | ❌（需 sklearn runtime） |
| multiplier-table（production） | 8.64 | 8.00 | 10.96 | +38.9% | ✅ |
| naive-estimate | 14.14 | 9.00 | 18.79 | — | ✅ |
| dummy-mean（DummyRegressor） | 33.75 | 29.18 | 41.43 | −138.7% | ✅ |

**判讀（誠實版）**：
- dummy-mean 慘敗證明「使用者估時」本身是強訊號——任何忽略估時的模型都不值得做。
- ElasticNet/Ridge 勝出方向合理（能同時利用估時的線性關係與其他特徵），但 **14 筆資料的排名是噪音級**（門檻 30 筆）；選型與評估共用同一批 folds，數字偏樂觀。
- 因此 comparison 輸出明確標示：`insufficient evidence for automatic promotion`。

### Holdout（11 train / 3 eval）

| 模型 | model MAE | baseline MAE | 判定 |
|---|---|---|---|
| multiplier-table 0.2.0 | 4.33 | 7.33 | 3 筆 eval → gate 拒絕自動晉升 |
| duration-linear 0.3.0 | 5.54 | 7.33 | 同上，`sufficient_evidence: false` |

## 4. 為什麼 production 還是 multiplier table？

這是刻意的工程決策，且已被兩種資料規模驗證：

1. **14 筆 demo 資料**：evidence gate 要求 ≥10 筆 out-of-sample 評估，3 筆 holdout 觸發 `insufficient evidence for automatic promotion`。
2. **4,227 筆真實資料（SiP）**：evidence gate 通過（845 筆 holdout），但 **baseline gate 拒絕**——ridge MAE 165.9 輸給 naive 152.7；補充實驗顯示連直接優化 MAE 的 median regression 也只能追平估時（見 [EXPERIMENT_REPORT.md](EXPERIMENT_REPORT.md) 第 5 節）。任務級估時本身就是最強的預測子。
3. multiplier table 是「估時錨定＋類別修正」策略中最可解釋、行為有界（clamp 0.75–1.45）的實作，冷啟動風險低。
4. ElasticNet/Ridge 的 serving 能力已就緒（`linear-json` artifact＋parity test）——**能力先行，晉升等證據**；兩次拒絕都在 `promotion_audit.jsonl` 留有紀錄。
5. 目前 production 是以 `--allow-insufficient-evidence` 明確覆寫晉升的 bootstrap 模型，audit log 有紀錄。

## 5. 不確定性表達（誠實命名）

- `confidence`（保留欄位，向後相容）：由 category 歷史 MAE 換算的 0–1 分數，**不是機率、未經 calibration**。
- 新欄位（v0.58.0 起）：
  - `lower_bound`／`upper_bound` — **historical error band**（預測 ± category MAE），非統計預測區間
  - `reliability` — `high`／`medium`／`low`／`insufficient-data`（樣本 <3 或無 error profile 時一律 insufficient-data）
  - `sample_count` — 該 category 的訓練樣本數
  - `out_of_distribution` — unseen category 或估時超出訓練範圍 2 倍
  - `factors` — 逐項貢獻（線性模型為精確係數貢獻；multiplier 為逐步乘數增量）
  - `fallback` — 是否為 heuristic fallback

## 6. Unseen category 策略

- multiplier table：落回 `global_multiplier`。
- linear-json：one-hot 全零（等同「平均 category」），同時 `out_of_distribution: true`。
- 兩者皆將 reliability 降為 `insufficient-data`（sample_count = 0）。

## 7. 已知限制與失效模式

- 資料量：所有評估皆為 demo 級證據。
- 極端輸入：預測 clamp 1–480 分鐘；超長估時會觸發 OOD 旗標但仍會外推。
- per-user calibration（backend）：3 筆即啟動，以 median ratio、clamp 0.5–2.0 護欄限制波動。
- 訓練殘差（category_mae）低估真實誤差——reliability band 偏窄，文件與 UI 不得將其表述為統計區間。
