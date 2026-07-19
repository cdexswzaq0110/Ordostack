# Experiment Report — Duration Model Candidates

- **日期**: 2026-07-18
- **執行環境**: Python 3.12.10、scikit-learn 1.8.0、seed 42
- **資料**: `duration_training_samples.csv` — 14 筆（curated demo data，見 [DATA_CARD.md](DATA_CARD.md)）
- **重現指令**:

```powershell
# Windows PowerShell（repo 根目錄）
python ml-service\training\validate_dataset.py
python ml-service\training\compare_models.py
python ml-service\training\train_linear_model.py --artifact-dir ml-service\training\artifacts\candidates\linear
python ml-service\training\train_duration_model.py
```

## 1. 實驗設計

- **比較**: 5-fold CV（`KFold(shuffle=True, random_state=42)`），每 fold 重新 fit 所有候選，row-level 絕對誤差跨 fold 匯總後計算 pooled MAE / Median AE / RMSE；另報告 per-fold MAE 平均±標準差。
- **候選**: naive estimate、DummyRegressor(mean)、multiplier table（現行 production）、Ridge(α=1.0)、ElasticNet(α=0.1, l1_ratio=0.5)、GradientBoosting(100 trees, depth 2)。線性模型皆前置 StandardScaler。
- **Feature encoding**: 共用 `app/data_contract.py::encode_features` —— `[estimated, priority, difficulty, focus, one-hot(category)]`，unseen category 全零。

## 2. 結果（5-fold CV, 14 rows, seed 42）

| 候選 | fold MAE mean±std | Pooled MAE | Median AE | RMSE | vs naive | servable |
|---|---|---|---|---|---|---|
| **elastic-net** | 3.63 ± 1.34 | **3.77** | 3.22 | 4.87 | **+73.3%** | ✅ |
| ridge-regression | 4.47 ± 1.32 | 4.65 | 4.34 | 5.44 | +67.1% | ✅ |
| gradient-boosting | 8.58 ± 3.22 | 8.27 | 7.74 | 9.36 | +41.5% | ❌ |
| multiplier-table (production) | 8.57 ± 2.72 | 8.64 | 8.00 | 10.96 | +38.9% | ✅ |
| naive-estimate | 14.17 ± 3.33 | 14.14 | 9.00 | 18.79 | — | ✅ |
| dummy-mean | 33.13 ± 13.29 | 33.75 | 29.18 | 41.43 | −138.7% | ✅ |

（fold-level 數值見 `ml-service/training/artifacts/model_comparison.json` 的 `fold_mae`。）

### Holdout 訓練驗證（11 train / 3 eval, seed 42）

| 模型 | model MAE | Median AE | RMSE | baseline MAE | improvement | sufficient_evidence |
|---|---|---|---|---|---|---|
| duration-linear 0.3.0（elastic-net） | 5.54 | 4.15 | 6.63 | 7.33 | +24.4% | **false** |
| local-duration-regressor 0.2.0 | 4.33 | — | — | 7.33 | +40.9% | 3 筆 eval，gate 拒絕 |

## 3. 分析

1. **dummy-mean 的價值**：MAE 33.75 慘輸 naive 的 14.14，證明使用者估時本身就是最強的單一訊號。任何模型的第一要務是「善用估時」而非「取代估時」。
2. **線性模型為何勝出**：actual 與 estimated 高度線性相關（示範資料 ratio 0.8–1.37），線性模型天然吻合；tree model 在 14 筆上只會切出高變異的階梯。ElasticNet 的 L1 成分把弱特徵係數壓向 0，在極小樣本上比 Ridge 略穩。
3. **為何不能宣稱 ElasticNet「證明有效」**：
   - 14 筆 < 30 筆比較門檻；fold 排名在此規模是噪音級。
   - 選型與評估共用同一組 folds → 選出的贏家分數天然偏樂觀（selection optimism）。
   - 資料是手工示範資料，分佈乾淨度遠高於真實行為。
4. **決策**：production 維持 multiplier table（bootstrap，以 `--allow-insufficient-evidence` 晉升並記入 audit log）；ElasticNet 以 `linear-json` artifact 形式完成 serving 能力與 parity 驗證，等真實回饋資料達到 evidence gate（≥10 筆 out-of-sample）再走正常晉升。

## 4. Promotion gate 實測

```text
$ python training/promote_duration_model.py --artifact ...candidates/linear/duration_model.json --metrics ... --dry-run
Promotion rejected: insufficient evidence for automatic promotion: 3 evaluation rows (minimum 10)
```

Audit log（`promotion_audit.jsonl`，本地狀態）記錄了 dry-run-rejected 與 production bootstrap 晉升兩筆事件。

## 5. 真實資料實驗：SiP dataset（2026-07-19 新增）

- **資料**: `data/external/sip_duration_tasks.csv` — 4,227 筆真實商業軟體任務（來源與映射見 [DATA_CARD.md](DATA_CARD.md) 第 6 節）
- **重現**: `python ml-service/training/compare_models.py --input ml-service/training/data/external/sip_duration_tasks.csv`

### 5.1 六候選 5-fold CV（4,227 rows, seed 42）

| 候選 | Pooled MAE | Median AE | RMSE | vs naive |
|---|---|---|---|---|
| gradient-boosting | **151.79** | 101.03 | 223.71 | +3.1% |
| naive-estimate | 156.71 | **60.00** | 259.71 | 基準 |
| multiplier-table | 158.78 | 82.00 | 243.12 | −1.3% |
| ridge-regression | 168.75 | 125.64 | 237.21 | −7.7% |
| elastic-net | 170.16 | 127.63 | 237.61 | −8.6% |
| dummy-mean | 216.38 | 191.13 | 280.33 | −38.1% |

### 5.2 補充實驗：正確的模型形式也贏不了

因誤差呈乘法性長尾，另測了文獻上正確的兩種形式（一次性實驗，未進 pipeline）：

| 形式 | MAE | Median AE |
|---|---|---|
| naive（clamp 後） | 152.88 | 60.00 |
| QuantileRegressor(q=0.5)（直接優化 MAE） | 153.10 | 67.50 |
| Ridge log-log（log 估時→log 實際） | 154.90 | 82.20 |
| Ridge lin-lin | 168.75 | 125.64 |

Median regression 本質上收斂到「照抄估時」——**任務級估時本身就是條件中位數的近似**，與 SiP 論文結論一致。

### 5.3 正式晉升結果（實際執行）

Ridge 於 3,382/845 holdout 訓練評估：model MAE 165.86 vs baseline 152.69，`sufficient_evidence: true`（845 筆）。

```text
$ python training/promote_duration_model.py --artifact ...sip-linear/duration_model.json --metrics ...
Promotion rejected: candidate model_mae 165.86 does not beat baseline_mae 152.69
```

### 5.4 結論（本專案最重要的一張實驗表）

1. 14 筆 demo 資料：evidence gate 拒絕（樣本不足）。
2. 4,227 筆真實資料：evidence gate **通過**，baseline gate **拒絕**——沒有可 serving 的模型打得贏使用者自己的估時（MAE）。
3. 線性模型 MAE 較差但 RMSE 較好（237 vs 260）：它們最小化平方誤差，是目標函數不匹配，不是 bug。
4. GBM 的 +3.1% 不足以支付把 scikit-learn 塞進 runtime 的成本。
5. **Production 維持估時錨定策略是被真實資料驗證的決策**——gates 不是儀式，它們真的擋下了兩次。

## 6. Training-serving 一致性

- 線性推論數學單一實作於 `app/data_contract.py::linear_predict`，訓練評估與 runtime serving 共用。
- Parity test（`tests/test_training_serving_parity.py`）驗證：匯出 JSON 的預測與 fitted sklearn pipeline 之差 < 0.01 分鐘；serving endpoint 與 training reference 整數分鐘完全一致。
- 匯出方式選擇（兩案比較後採 B）：
  - A. pickle 完整 sklearn Pipeline — 優點：零重實作；缺點：runtime 需裝 sklearn+numpy（映像 +數百 MB）、pickle 有版本相容與反序列化安全問題、artifact 不可讀。
  - B. **JSON 係數匯出（採用）** — 優點：runtime 零額外依賴、artifact 人類可讀可 diff、無 pickle 風險；缺點：僅支援線性模型、需 parity test 保護重實作。
