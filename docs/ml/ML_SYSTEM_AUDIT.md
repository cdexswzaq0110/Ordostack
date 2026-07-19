# OrdoStack ML 系統審查報告（ML System Audit）

- **審查日期**: 2026-07-18
- **審查基準 commit**: `d21153a`（v0.57.0, branch `feature/ml-p0-hardening` 起點）
- **審查範圍**: `ml-service/`（serving＋training）、`backend-api/app/services/predictions.py`、prediction logging、MLOps 相關文件
- **審查方法**: 逐檔閱讀實際程式碼與 artifacts，所有結論皆附程式碼證據；無法驗證者明確標示

---

## 1. 核對「已知狀態」的結果

| 宣稱 | 驗證結果 | 證據 |
|---|---|---|
| 專案包含 web-dashboard、backend-api、scheduler-service、ml-service、mysql | ✅ 屬實 | `docker-compose.yml`、各服務目錄存在 |
| ML 目標是預測任務實際完成時間（分鐘） | ✅ 屬實 | `ml-service/app/predict.py:21` `predict_duration()`；target 為 `actual_minutes` |
| 訓練資料約 14 筆 | ✅ 屬實，正好 14 筆 | `ml-service/training/data/duration_training_samples.csv`（15 行含 header） |
| Production 模型是 category multiplier table＋人工權重 | ✅ 屬實 | `duration_model.json`：`category_multipliers`＋固定 `difficulty_weight=0.04`、`priority_weight=0.015`、`focus_multiplier=1.05`（`train_duration_model.py:15-17` 寫死，非學習所得） |
| 比較含 naive、multiplier table、Ridge、Gradient Boosting | ✅ 屬實 | `compare_models.py:85-92` |
| Ridge 5-fold CV MAE 優於 production | ✅ 屬實：Ridge 4.95±1.99 vs multiplier table 8.57±2.72 | `training/artifacts/model_comparison.json` |
| 已有 holdout、promotion gate、registry、hot reload、fallback、prediction logging、calibration、ClearML optional | ✅ 皆已實作 | `train_duration_model.py:73-81`、`promote_duration_model.py:87-100`、`app/model_registry.py`、`app/main.py:87-97`、`app/predict.py:105-117`、`backend-api/app/services/predictions.py:64-94,180-205`、`training/clearml_utils.py` |
| 仍是 Local Private Beta，非 production SaaS | ✅ 屬實 | 無雲端部署設定實際啟用；`docs/aws-deployment-plan.md` 僅為規劃 |

---

## 2. 問題清單（含證據、風險、修正、優先級、驗收）

### 2.1 資料問題

| 問題 | 實際程式碼證據 | 風險 | 建議修正 | 優先級 | 驗收方式 |
|---|---|---|---|---|---|
| 樣本僅 14 筆，任何評估結論統計上不可靠 | `duration_training_samples.csv` 14 筆；`duration_metrics.json` `evaluation_rows: 3` | 用 3 筆 holdout 宣稱 `improvement_ratio 0.41` 會誤導；面試時會被追殺 | 所有報告標示樣本數；promotion 加最小評估樣本 gate；文件明講「demo 級證據」 | **P0** | metrics 輸出含樣本數；樣本不足時 promotion 輸出 `insufficient evidence for automatic promotion` |
| 無任何 dataset validation（重複、缺值、範圍、異常 ratio 皆不檢查） | `train_duration_model.py:84-102` `load_training_rows()` 只過濾 `estimated>0 and actual>0`，其餘照單全收 | 髒資料直接進訓練，multiplier 被單筆異常值拉偏 | 建立 data contract＋可執行 validation，輸出報告 | **P0** | `python training/validate_dataset.py` 產出 JSON report；壞資料觸發明確錯誤 |
| 無 train/serving feature schema 單一定義 | serving 特徵散在 `app/schemas.py`＋`app/predict.py`；訓練特徵散在 `train_duration_model.py`、`compare_models.py:48-58`，各自手寫 | training-serving skew：改一邊忘了另一邊，無測試會抓到 | 抽出共用 data contract module；加 parity test | **P0** | parity test：同輸入 training 編碼與 runtime inference 預測一致 |
| `actual_minutes` 同時是 target 又是 serving 輸入（blending） | `app/predict.py:68-71`：serving 時 `actual_minutes>0` 就混入預測 | 這不是 leakage（是刻意的 execution-signal blending），但語意未文件化，且 pairing 評估時 blended 預測會偷看部分 actual | 文件化 blending 行為；評估時使用 raw prediction（已存 `raw_predicted_minutes`）並明確區分 | P1 | DATA_CARD 說明；accuracy 計算註明使用欄位 |
| 訓練資料無 `user_id`、無時間戳，random split 忽略時間順序與使用者分組 | CSV 只有 6 欄；`split_rows()` 用 `random.Random(seed).shuffle` | 同使用者相似任務同時進 train/validation，CV 分數偏樂觀 | 資料量小暫無法做 time/group split；文件明示此限制；feedback export 未來附 user_id/timestamp | P1 | DATA_CARD 限制章節；roadmap 記錄 group split 條件 |
| 任務 `title` 有傳給 ml-service 但未用於模型 | `app/schemas.py:6` 收 `title`；`predict.py` 未使用 | 目前無過擬合風險，但 payload 傳輸 PII 級文字欄位無必要性未文件化 | data contract 將 `title` 標為「不得進入模型」欄位 | P2 | data contract 列出 excluded fields |
| Demo seed data 與訓練資料是手寫示範資料，非真實行為資料 | CSV 數值分佈過度乾淨（ratio 全在 0.8–1.37） | 若對外宣稱「模型有效」即為虛假成效 | 所有文件標示資料來源為 curated demo data | **P0** | DATA_CARD 資料來源章節 |

### 2.2 模型問題

| 問題 | 實際程式碼證據 | 風險 | 建議修正 | 優先級 | 驗收方式 |
|---|---|---|---|---|---|
| multiplier table 是統計查表（per-category mean ratio）＋人工權重，不是嚴格意義的 ML 模型，但文件稱 regressor | `MODEL_NAME = "local-duration-regressor"`（`train_duration_model.py:13`）；difficulty/priority/focus 權重寫死非學習 | 面試時稱其為 regressor 會被拆穿 | 正名為 baseline statistical model；MODEL_CARD 誠實定位 | **P0** | MODEL_CARD 模型定位章節 |
| Ridge CV 勝出（4.95 vs 8.57）但 serving 無法載入 Ridge——比較結果無路徑落地 | `app/predict.py:84-98` 只認 multiplier-table 欄位；無 sklearn runtime、無係數匯出 | 「比較了但沒用」——最好的模型無法上線 | Ridge 匯出 coefficients/scaling/category mapping 成 JSON，serving 加純 Python linear inference | **P0** | ridge-json artifact 可被 `/duration/predict` 服務；parity test 通過 |
| 缺 DummyRegressor／正式統計 baseline | `compare_models.py:85-92` 只有 naive-estimate | 無法回答「模型比預測平均值好多少」 | 比較加入 DummyRegressor(mean) | **P0** | model_comparison.json 含 dummy-mean 結果 |
| 只報 MAE mean/std，無 Median AE、RMSE、per-fold 誤差、樣本數不完整 | `compare_models.py:115-121` 只有 `mae_mean`、`mae_std` | 單一指標在 14 筆下不穩，離群值影響不可見 | 加 Median AE、RMSE、per-fold errors、vs naive 改善量 | **P0** | model_comparison.json 含完整指標 |
| 3 筆 holdout 即可通過 promotion gate | `promote_duration_model.py:87-100` 無最小樣本檢查；`duration_metrics.json` `evaluation_rows: 3` | 3 筆的 41% 改善毫無統計意義卻能自動晉升 | 加 minimum evaluation sample gate | **P0** | 樣本不足時 promotion 拒絕並輸出指定訊息 |
| unseen category：multiplier 用 global fallback（合理）但無 OOD 警示 | `predict.py:87` `.get(category, global_multiplier)` | 使用者無從得知該預測是外推 | prediction 回傳 out-of-distribution warning 欄位 | P1 | unseen category 回應含 warning |
| confidence 是規則換算（1 - MAE/estimate ＋加分項），不是 calibrated probability | `predict.py:40-59`：floor/ceiling/bonus 全是 magic number | 對外顯示 0.87 會被誤讀為機率 | 改語意為 reliability score，附 sample_count 與說明；不足時明示 | **P0** | API 回應含 reliability label＋sample_count；文件不再稱機率 |
| per-user calibration 3 筆即啟動 | `backend-api/app/services/predictions.py:23` `CALIBRATION_MIN_SAMPLES = 3` | 3 筆 median 極不穩定（有 clamp 0.5–2.0 護欄，風險部分緩解） | 已有 clamp＋window；文件化並於 UI 顯示樣本數（已回傳 `calibration_samples`） | P2 | 文件說明；現行為可接受 |
| 極端輸入 clamp 至 1–480 分鐘（有護欄） | `predict.py:101-102`、`train_duration_model.py:166` | 已緩解；但 bounds 未寫入 artifact | artifact 記錄 prediction bounds | P1 | artifact 含 `prediction_bounds` |

### 2.3 MLOps 問題

| 問題 | 實際程式碼證據 | 風險 | 建議修正 | 優先級 | 驗收方式 |
|---|---|---|---|---|---|
| artifact 無 schema version、feature names、dataset checksum、程式/套件版本 | `duration_model.json` 僅 13 個 key，無上述任何欄位 | 無法追溯 artifact 由哪份資料/程式產生；schema 演進無法防呆 | artifact 加完整 metadata；serving 檢查 schema 相容性 | **P0** | 新 artifact 含全部欄位；不相容 schema 觸發 fallback 測試 |
| registry 寫入非 atomic | `promote_duration_model.py:71` 直接 `registry_path.write_text()` | 寫入中斷產生半份 JSON，serving 讀壞檔 | 寫 temp file＋`os.replace()` | **P0** | promotion 測試通過；損毀 registry 有 fallback（`model_registry.py:28-34` 已處理不存在，需補壞 JSON 情況） |
| 損毀 artifact：缺 key 回 None（OK），但非法 JSON 會直接 crash | `predict.py:111-112` `json.load` 無 try/except | `/duration/predict` 500，整條 ML 路徑斷線（backend 有 fallback 護住，但 ml-service 自身不優雅） | load 包 try/except → heuristic fallback | **P0** | corrupted artifact fallback test |
| 無 rollback CLI | 只有 `--allow-regression` 旗標；registry 有 archived 紀錄但無指令切回 | 壞模型上線後只能手改 JSON | 新增 rollback CLI＋測試 | **P0** | rollback 後 active_model 指向前一版；測試通過 |
| 無 promotion audit log、無 dry-run | `promote_duration_model.py` 全檔 | 晉升歷史只能靠 git；無法先驗證再執行 | 加 `--dry-run` 與 JSONL audit log | P1 | dry-run 不改 registry；audit log 逐筆追加 |
| `/model/reload` 無任何保護（內部網路假設） | `app/main.py:87-97` 無 auth | Compose 網路內僅 backend 可達，風險有限；但假設未文件化 | 文件化信任邊界；roadmap 記 token 保護 | P2 | ARCHITECTURE 信任邊界章節 |
| 監控端 accuracy 無樣本充分性判定 | `predictions.py:97-129` 任何 paired 數都輸出 improvement_ratio | 2 筆 paired 也顯示漂亮百分比 | response 加 `sufficient_data`＋門檻；前端顯示樣本不足 | **P0** | API 回應含判定欄位；測試覆蓋 |
| drift monitoring 不存在（文件 roadmap 提及） | `ml-service/`、`backend-api/` 無任何 drift 計算程式 | 文件若稱「有 drift 偵測」即不實 | 維持 roadmap 定位，不實作 | P2 | FUTURE_ML_ROADMAP 記載啟用條件 |
| prediction log 有 model_version/raw/calibrated/actual（良好），但無 fallback reason、無 prediction/pairing timestamp 分離 | `memory_store.py:224-262`、`mysql_store.py:332` | 無法分析 fallback rate 與回填延遲 | P1 補欄位（不建第二套 log） | P1 | schema 擴充後 pairing 測試通過 |

---

## 3. 五類實作狀態總分類

**已實作且已驗證**（有測試）
- Heuristic fallback、artifact 載入（缺 key 情況）、holdout 訓練、promotion 基本 gate、hot reload、prediction logging＋pairing、per-user calibration、backend ML timeout fallback（`backend-api/tests/test_predictions.py`、`ml-service/tests/` 41 個測試）

**已實作但不完整**
- Promotion gate（缺最小樣本 gate、atomic write、audit、dry-run）
- 模型比較（缺 dummy baseline、Median AE/RMSE/per-fold、勝出模型無法 serving）
- Confidence（有實作但語意不誠實）
- Artifact metadata（缺 schema/checksum/版本追溯）
- 損毀處理（缺 key OK；壞 JSON 會 crash）

**文件宣稱有、程式碼卻沒有**
- `docs/clearml-mlops.md` 描述的 ClearML server 工作流：程式碼為 optional no-op（`clearml_utils.py` 未安裝/未設定時跳過）——文件需標示 optional
- 「regressor」命名暗示學習型迴歸模型：實為統計查表＋人工權重

**尚未實作**
- Data contract／dataset validation、parity test、rollback CLI、reliability 語意、explainability factors、OOD warning、監控樣本充分性、drift

**現階段不應實作**（樣本量不足，列入 roadmap）
- 深度學習／Transformer title encoder、RL 排程、bandit、完成機率分類、自動 retraining、全自動 promotion、production ClearML/AWS

---

## 4. 審查結論

系統骨架（fallback、registry、logging、calibration、測試文化）在同規模 side project 中屬前段班；**最大的誠實性風險在於「評估敘事」**：14 筆資料、3 筆 holdout 的數字被以正式 metrics 呈現，且 CV 勝出的 Ridge 無法落地 serving，使「模型比較」流於展示。P0 修正全數圍繞：資料契約、可落地的最佳候選、誠實的不確定性表達、與有 gate 的 promotion。
