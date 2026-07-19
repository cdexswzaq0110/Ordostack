# OrdoStack 面試手冊

<!-- meta: subtitle=Machine Learning Engineer 作品集完整解說（含系統架構、ML pipeline、MLOps、面試 Q&A） -->
<!-- meta: version=v0.58.0 -->
<!-- meta: date=2026-07-18 -->

本手冊對應 repository 版本 v0.58.0（branch `feature/ml-p0-hardening`）。所有檔案路徑、function 名稱、指令與數字皆取自實際程式碼與實際執行結果；凡屬規劃中功能均明確標示「尚未實作」。

# 第 1 章　專案一句話介紹

**OrdoStack 是一個在自己電腦上執行的每日排程規劃器：你輸入今天要做的任務，它會用你過去的實際執行紀錄預測每件事真正需要多久，然後自動把任務排進你的空檔，執行後再把「預測 vs 實際」的差距回饋給模型。**

給完全沒看過專案的人的白話版本：

> 一般待辦清單只會列出「要做什麼」；OrdoStack 還回答「今天排得下嗎？每件事實際會花多久？」。它由五個服務組成（前端畫面、主後端、排程引擎、時長預測 ML 服務、MySQL 資料庫），用 Docker Compose 一鍵啟動，完全本地執行、不呼叫任何付費雲端 API。

三個關鍵詞：**local-first**（資料留在本機）、**service-oriented**（前端／後端／排程／ML 各司其職）、**honest ML**（資料只有幾十筆時，系統會直說「樣本不足」而不是假裝準確）。

# 第 2 章　三種面試介紹版本

## 2.1　30 秒版本（電梯簡報）

> 「OrdoStack 是我做的本地端智慧日程規劃器。使用者建立任務後按一個鍵，系統會呼叫排程服務用 priority scoring 加上拓撲排序把任務排進空檔，同時呼叫獨立的 ML 服務預測每個任務的實際耗時。任務完成後，實際時間會回寫成訓練資料，形成『預測、執行、回饋、再訓練』的完整 MLOps 迴圈——包含 data contract、promotion gate、hot reload 和 rollback。整套系統五個服務，Docker Compose 一鍵起，147 個測試。」

## 2.2　1 分鐘版本

> 「我求職目標是 ML Engineer，所以這個專案的重點不是模型多炫，而是完整的 ML 系統工程。產品面：OrdoStack 是每日排程規劃器，React 前端、FastAPI 後端、獨立的排程微服務和 ML 微服務、MySQL 儲存。
> ML 面：任務耗時預測是一個 regression 問題，target 是實際執行分鐘數。因為初期只有十幾筆資料，我刻意讓 production 模型是一個可解釋的 category 統計查表，同時用 5-fold CV 比較了 naive baseline、DummyRegressor、Ridge、ElasticNet、Gradient Boosting 六個候選——ElasticNet 明顯勝出，但我沒有直接上線，因為 promotion gate 要求至少 10 筆 out-of-sample 評估，3 筆 holdout 不構成證據。
> MLOps 面：訓練和 serving 共用同一個 data contract 模組防止 skew；線性模型以純 JSON 係數匯出，runtime 不需要裝 scikit-learn，並有 parity test 保證兩邊預測一致；promotion 有三道 gate、atomic 寫入、audit log、dry-run 和 rollback CLI；每筆預測都帶可解釋的因素分解和誠實的 reliability 標籤。
> 我還把 pipeline 拿到真實資料上驗證：轉換了公開的 SiP 資料集——4,227 筆真實商業軟體任務的估時與實際工時。結果 evidence gate 通過了，但 baseline gate 拒絕了所有候選模型，因為沒有模型在 MAE 上贏過使用者自己的估時。這證明我的 gate 不是儀式，是真的在做決策。」

## 2.3　3 分鐘版本（白板輔助）

依序講四段，邊講邊畫：

1. **問題**（30 秒）：「待辦清單的通病是高估自己。我想要一個系統回答兩個問題：今天的任務排得下嗎？每件事實際要多久？第二個問題就是一個天然的 regression 問題，而且使用者每完成一個任務就產生一筆帶標籤的訓練資料。」
2. **架構**（60 秒）：畫五個框——`web-dashboard :5173 → backend-api :8000 → {scheduler-service :8100, ml-service :8200} + MySQL :3306`。「dashboard 只跟 backend 講話；backend 是唯一擁有資料庫的服務；排程演算法和 ML 預測分成兩個獨立服務，因為它們的變更頻率、依賴和失效模式完全不同。任何內部服務掛掉，backend 都有降級策略，使用者操作不會中斷。」
3. **ML pipeline**（60 秒）：「資料從執行紀錄來，經過 data contract 驗證，訓練時做 seeded holdout，比較六個候選模型。所有指標以分鐘為單位：MAE、Median AE、RMSE，並跟 naive estimate 比改善量。晉升有三道 gate，其中 evidence gate 在評估樣本不足 10 筆時直接輸出 insufficient evidence for automatic promotion。上線後每筆預測都被記錄，任務完成後配對實際時間，dashboard 顯示 rolling MAE——樣本不足時顯示『樣本不足』而不是漂亮百分比。」
4. **取捨與誠實**（30 秒）：「這個專案最大的設計原則是：資料量決定方法。14 筆示範資料撐不起深度學習，也撐不起自動晉升，所以我把工程投資放在資料迴路、可靠 serving、fallback 和可解釋性。模型會隨資料成長升級，系統已經準備好了。」

# 第 3 章　問題與使用者情境

## 3.1　一般待辦清單缺什麼

| 待辦清單給你的 | 實際規劃需要的 | OrdoStack 的對應功能 |
|---|---|---|
| 任務名稱與勾選框 | 今天總共有多少可用時間 | 固定行程（fixed events）切出空檔，`build_free_slots` |
| 自己填的預估時間 | 這個預估通常偏樂觀多少 | ML 耗時預測＋歷史誤差帶 |
| 一個平面清單 | 哪些先做、哪些依賴哪些 | priority scoring＋拓撲排序 |
| 完成後打勾就忘了 | 這次花了多久、下次怎麼修正 | 執行紀錄→prediction log 配對→per-user calibration |

## 3.2　核心使用情境（實際操作流）

1. 早上：登入 dashboard，看到今天的任務佇列與固定行程（會議、課程）。
2. 按 **Generate Plan**：後端呼叫 ml-service 取得每個任務的預測分鐘數，再把任務、固定行程、預測值交給 scheduler-service，產生一份排進空檔的時間表。
3. 執行中：對任務按 start／pause／complete；系統累計實際分鐘數。
4. 完成後：實際分鐘回寫 prediction log 完成配對；Analytics 顯示估時 vs 預測 vs 實際；MLOps 頁顯示模型 rolling 誤差。
5. 累積夠多資料後（本地指令）：匯出回饋 CSV → 重新訓練 → 通過 gate 才晉升 → hot reload。

## 3.3　目標使用者

現階段是**單機單人**（Local Private Beta / Customer Demo MVP）：學生、工程師、自由工作者等需要把一天排滿又常低估工時的人。多使用者 SaaS 不在目前範圍（見第 12 章與 roadmap）。

# 第 4 章　完整系統架構

## 4.1　架構圖

```text
Browser
   │
   ▼
web-dashboard  (React + Vite + TS, :5173)
   │  HTTP/JSON (唯一對外 API)
   ▼
backend-api    (FastAPI, :8000) ──────────────► MySQL 8.4 (:3306, host :3307)
   │                                             8 張資料表、Alembic 遷移
   ├── HTTP ► scheduler-service (FastAPI, :8100)   排程演算法（無狀態）
   └── HTTP ► ml-service        (FastAPI, :8200)   耗時預測（無狀態＋JSON artifact）
```

## 4.2　各元件職責

- **web-dashboard**：單頁 React 應用（`web-dashboard/src/App.tsx`）。六個工作區視圖（Planner、Tasks、Schedule、Analytics、MLOps、Settings）、i18n（英文預設、繁中完整翻譯）、以 fetch 呼叫 `/api/*`。不直連 MySQL、scheduler、ml-service。
- **backend-api**：唯一對外產品 API。分層：routes（薄，`app/api/`）→ services（商業邏輯，`app/services/`）→ repositories（持久化，`app/repositories/`）。擁有全部產品資料與使用者驗證（PBKDF2 600k iterations、Bearer token）。
- **scheduler-service**：純函數式排程引擎。輸入任務＋固定行程＋鎖定項，輸出時間表。**不碰資料庫**——排程結果由 backend 存檔。
- **ml-service**：耗時預測。載入 JSON artifact（registry 指定或預設路徑），artifact 壞掉時降級 heuristic。**不碰資料庫**——prediction log 由 backend 記錄。
- **MySQL**：唯一有狀態的服務；Docker named volume 持久化；Alembic 管 schema 版本。

## 4.3　為什麼 dashboard 不直接呼叫 ml-service？

1. **安全與信任邊界**：ml-service 沒有使用者驗證（內部服務）。所有對外流量必須經過 backend 的 auth。
2. **資料完整性**：預測要跟 per-user calibration、prediction logging 綁在一起，這些邏輯屬於 backend；前端直連會繞過記錄。
3. **演進自由**：ml-service 的 schema 可以改版，只要 backend 適配即可，前端合約不動。
4. **降級一致性**：ml-service 掛掉時 backend 回估時 fallback，前端完全無感。

## 4.4　為什麼排程和 ML 預測分成兩個服務？

- **變更頻率不同**：排程演算法改版與模型 artifact 晉升是兩條獨立的發佈節奏。
- **依賴不同**：ml-service 的訓練生態（scikit-learn）被隔離在訓練期；runtime 兩個服務都輕量。
- **失效模式不同**：ML 掛了→用估時仍能排程；排程掛了→預測照常顯示。分開部署讓兩種失效互不牽連。
- **面試誠實版**：單機跑其實一個服務也行；拆開的成本是多兩個容器與 HTTP 呼叫。我選擇拆開是為了讓邊界清楚、測試獨立、並示範真實團隊的服務切分——這是刻意的學習型架構決策（成本我講得出來）。

## 4.5　Service-oriented 架構的優點與成本

| 優點 | 成本 |
|---|---|
| 職責邊界清楚，單一服務可獨立測試與重建 | 跨服務呼叫要處理 timeout／fallback（backend 兩處 8 秒 timeout） |
| 依賴隔離（sklearn 不進 runtime image） | 本地 debug 要看多個容器的 log |
| 失效隔離（每服務有 /health /ready） | Compose 啟動順序與 healthcheck 依賴要維護 |
| 模型熱更新不動其他服務 | 整體記憶體占用比單體高 |

# 第 5 章　四條完整資料流

## 5.1　使用者登入與驗證

```text
Browser → POST /api/auth/register 或 /api/auth/login (email+password)
backend: services/auth.py 驗證 → PBKDF2-HMAC-SHA256 (600k iterations) 比對
       → 簽發 bearer token → 前端存入 memory/localStorage
之後所有請求: Authorization: Bearer <token>
       → app/dependencies.py::get_current_user 解析 → 注入 user_id
       → 所有 service 層查詢一律帶 user_id（資料隔離，測試 test_user_isolation.py）
失敗路徑: 缺 token → 401（RFC 7235）；token 無效 → 401；跨使用者資源 → 404
```

## 5.2　使用者按下 Generate Plan（最重要的一條）

```text
1. App.tsx::generatePlan()  →  POST /api/schedules/generate
2. backend app/api/schedules.py（路由薄層）
   → app/services/schedules.py::generate_schedule()
3. 收集材料: task_service.list_tasks() ＋ fixed_event_service.list_fixed_events()
4. 呼叫 ML: prediction_service.predict_for_tasks()
   → POST http://ml-service:8200/duration/predict（timeout 8s）
   → 失敗則 build_fallback_predictions()（用估時，fallback=true）
   → 成功則套 per-user calibration factor（raw 值另存）
5. 呼叫排程: POST http://scheduler-service:8100/schedule/generate
   payload = 任務(含 predicted_minutes) + fixed_events + locked_items
   → scheduler: score → topological sort → capacity 選擇 → 排入空檔
6. 存檔: get_store().save_generated_schedule() → MySQL schedule_runs + schedule_items
7. 記錄預測: prediction_service.log_served_predictions() → prediction_logs（每筆含
   model_name/version、raw 與 calibrated 預測、estimated_minutes）
8. 回傳排程 JSON → 前端渲染時間軸
```

## 5.3　任務執行與 actual duration 回寫

```text
start:    POST /api/tasks/{id}/execution/start   → execution_logs 記 start 事件
pause:    POST /api/tasks/{id}/execution/pause   → 累計區間
complete: POST /api/tasks/{id}/execution/complete
   → services/execution_logs.py 計算 actual_minutes（start→complete 扣暫停）
   → 任務狀態改 completed
   → prediction_service.record_prediction_actual(user_id, task_id, actual_minutes)
      → 回寫該任務最近一筆 prediction log 的 actual_minutes（完成配對）
Analytics 頁: estimated vs predicted vs actual 逐任務比較
```

## 5.4　Feedback → Training → Promotion → Reload → Monitoring

```text
1. 匯出: GET /api/ml/duration-feedback（或 scripts/export_duration_feedback.py）
   → 完成任務轉成訓練 CSV（6 個 contract 欄位）
2. 驗證: python ml-service/training/validate_dataset.py
   → data contract 1.0.0 檢查，報告寫入 artifacts/
3. 訓練: train_duration_model.py（multiplier）或 train_linear_model.py（elastic-net/ridge）
   → seeded holdout → duration_model.json + duration_metrics.json（含 checksum、版本、bounds）
4. 比較: compare_models.py → 6 候選 5-fold CV → model_comparison.json
5. 晉升: promote_duration_model.py [--dry-run]
   → evidence gate（≥10 筆 out-of-sample，不足輸出 insufficient evidence）
   → baseline gate → regression gate → atomic 改寫 registry → audit log
6. 部署: POST /model/reload → lru_cache 清空 → 下一請求載新 artifact
7. 監控: 每次 Generate Plan 記 prediction log；完成任務配對 actual
   → GET /api/ml/prediction-accuracy → rolling MAE、sufficient_data 判定
8. 回滾: rollback_duration_model.py [--version X] → reload
```

# 第 6 章　ML 問題定義

## 6.1　正式定義

- **問題型態**：監督式**迴歸（regression）**——輸出是連續分鐘數，不是類別。
- **Input features（5 個，defined in `ml-service/app/data_contract.py`）**：
  - `estimated_minutes`（int, 1–1440）：使用者自估時間——最強的單一訊號
  - `category`（string，正規化小寫；one-hot 或查表）
  - `priority`（int, 1–5）、`difficulty`（int, 1–5）
  - `requires_focus`（bool）
- **Target**：`actual_minutes`（int, 1–1440）——由執行紀錄計算的實際耗時。
- **禁用欄位**（`EXCLUDED_FIELDS`）：`title`（隱私＋高維過擬合）、`task_id`／`user_id`（識別碼會被記憶）。

## 6.2　為什麼主要用 MAE？

1. 單位就是分鐘，「模型平均差 5 分鐘」對使用者與面試官都直觀。
2. 對離群值比 RMSE 穩健——一筆爆表任務不會綁架整個指標。
3. 輔助指標：**Median AE**（更抗離群、代表典型誤差）、**RMSE**（懲罰大誤差、對「偶爾嚴重遲到」敏感）。三個一起看才知道誤差分佈的形狀。

## 6.3　Baseline 是什麼？

**Naive estimate**：直接把使用者的 `estimated_minutes` 當預測。這是「不做任何 ML」的成本為零方案；模型唯一的存在理由是穩定打敗它。另有 **DummyRegressor(mean)**（永遠預測訓練集平均）作為統計下限——它在比較中 MAE 33.75 慘輸 naive 的 14.14，反向證明估時本身資訊量極高。

## 6.4　14 筆資料能證明什麼、不能證明什麼

**能**：
- pipeline 端到端可運作（資料→訓練→評估→gate→serving）。
- 方向性訊號：線性模型看起來優於查表與 naive（ElasticNet pooled MAE 3.77 vs naive 14.14）。
- Dummy baseline 慘敗證明估時是必用特徵。

**不能**：
- 不能宣稱任何模型「已驗證有效」——14 筆 < 30 筆比較門檻，fold 排名是噪音級。
- 不能支持自動晉升——3 筆 holdout 觸發 `insufficient evidence for automatic promotion`。
- 不能代表真實分佈——資料是手寫示範資料（ratio 全在 0.8–1.37 的乾淨區間）。

**真實資料的補充驗證（SiP dataset, 4,227 筆）**：專案另外轉換了公開的 SiP effort estimation dataset（Jones & Cullum 2019, arXiv:1901.01621，一間軟體公司十年 12,299 筆任務，取 FINISHED 且落在 contract 範圍的 4,227 筆）。在這個規模上 evidence gate 通過（845 筆 holdout），但**沒有任何可 serving 的模型在 MAE 上贏過 naive estimate**（ridge 165.9 vs naive 152.7；連直接優化 MAE 的 median regression 也只能追平）——任務級估時本身就是條件中位數的近似。這個「模型輸了」的結果反而是專案最有力的證據：gates 用真實資料做出了正確決策。

## 6.5　為什麼目前不用深度學習？

1. **樣本量**：DNN 需要數千筆起跳；14 筆連線性模型都只能給方向。
2. **特徵形態**：5 個 tabular 特徵，樹模型與線性模型是文獻與實務上的正解；DNN 在小型表格資料上通常輸。
3. **Serving 成本**：本專案 runtime 連 scikit-learn 都刻意不裝（JSON 係數推論）；引入 PyTorch 違反 local-first 輕量原則。
4. **可解釋性**：使用者要知道「為什麼預測 129 分鐘」；線性貢獻分解直接給答案。

## 6.6　資料量不足時的正確工程策略（本專案的實際做法）

1. 選擇低變異、可解釋的模型（統計查表→線性），並保留 heuristic fallback。
2. 把工程投資放在**資料迴路**：logging、配對、匯出、驗證——讓每次使用都在生產訓練資料。
3. 用 gate 把「能力」與「上線」分開：serving 能力先做好（linear-json＋parity test），晉升等證據。
4. UI 誠實：樣本不足就顯示樣本不足；band 命名為 historical error band 而非 confidence interval。

# 第 7 章　模型比較與選擇

## 7.1　實際結果（2026-07-18, 14 rows, 5-fold CV, seed 42）

| 候選 | fold MAE mean±std | Pooled MAE | Median AE | RMSE | vs naive | 可 serving |
|---|---|---|---|---|---|---|
| elastic-net | 3.63 ± 1.34 | **3.77** | 3.22 | 4.87 | +73.3% | ✅ |
| ridge-regression | 4.47 ± 1.32 | 4.65 | 4.34 | 5.44 | +67.1% | ✅ |
| gradient-boosting | 8.58 ± 3.22 | 8.27 | 7.74 | 9.36 | +41.5% | ❌（需 sklearn runtime） |
| multiplier-table（production） | 8.57 ± 2.72 | 8.64 | 8.00 | 10.96 | +38.9% | ✅ |
| naive-estimate | 14.17 ± 3.33 | 14.14 | 9.00 | 18.79 | 基準 | ✅ |
| dummy-mean | 33.13 ± 13.29 | 33.75 | 29.18 | 41.43 | −138.7% | ✅ |

Holdout（11 train／3 eval）：multiplier-table MAE 4.33 vs baseline 7.33；duration-linear（elastic-net）5.54 vs 7.33，`sufficient_evidence: false`。

## 7.2　逐一解讀六個候選

- **Naive estimate**：零成本基準。MAE 14.14 代表「使用者平均低估／高估 14 分鐘」，這就是模型要吃下的空間。
- **DummyRegressor(mean)**：忽略所有輸入、永遠回訓練平均。MAE 33.75——比 naive 差 2.4 倍，證明這個問題「輸入非常有用」，任何模型必須以估時為核心特徵。
- **Multiplier table（production）**：每個 category 算 `mean(actual/estimated)`（clamp 0.75–1.45），乘上人工設定的 difficulty／priority／focus 修正。誠實定位：**統計查表＋規則**，不是學習型迴歸。優點：極可解釋、行為有界、冷啟動穩。
- **Ridge Regression**：L2 正則化線性迴歸。StandardScaler 後 α=1.0。能同時利用估時斜率與其他特徵，小樣本上係數被正則化壓穩。
- **ElasticNet**：L1+L2（α=0.1, l1_ratio=0.5）。L1 成分會把弱特徵係數推向 0（自動特徵篩選），在 14 筆上比 Ridge 略穩、略準。
- **Gradient Boosting**：100 棵深度 2 的樹。在 14 筆上只能切出高變異的階梯函數，且 serving 需要 sklearn runtime——被標記 `servable: false`，比較用途純粹是「證明樹模型在這個資料量不值得」。

## 7.3　關鍵概念解釋（面試常被追問）

- **Bias／Variance**：查表是高 bias 低 variance（假設「同 category 同比例」）；GBM 反之。14 筆時 variance 是主要敵人，所以偏向高 bias 陣營。
- **Overfitting**：模型背下訓練資料的噪音。訊號：訓練誤差 << 驗證誤差。本專案訓練殘差（category_mae ~7）明顯小於 CV 誤差，文件因此明示「訓練殘差低估真實誤差」。
- **Cross-validation**：資料切 k 份輪流當驗證集，讓每筆都被外樣本評估一次；小資料時比單一 holdout 穩。本專案 5-fold、row-level 誤差跨 fold 匯總。
- **Holdout**：訓練前先扣住一份不碰的資料做最終評估。訓練腳本 ≥10 筆時自動留 20%。
- **Time-based／Group split**：有時間順序或同群體資料時，random split 會洩漏未來／同人資訊。目前種子資料無 timestamp／user_id 無法做，DATA_CARD 明列為限制。
- **Feature scaling**：線性模型前置 StandardScaler，否則 estimated_minutes（數十～百）會壓過 0/1 特徵，正則化也會偏罰大尺度係數。
- **One-hot encoding**：category 轉成 0/1 欄位（`encode_features`）。**Unseen category** → 全零向量（等於「平均 category」）＋`out_of_distribution: true` 警示。
- **Regularization**：對大係數加懲罰（Ridge=L2 平方、Lasso=L1 絕對值、ElasticNet=兩者混合），小樣本防過擬合的第一道防線。
- **為什麼分數最低不直接上線**：(1) 選型與評估共用同一批 folds，贏家分數天然偏樂觀（selection optimism）；(2) 樣本量不足以分辨 3.77 與 4.65 是真差距還是抽樣噪音；(3) 上線價值 = 預期改善 × 確信度 − 切換風險，在確信度極低時期望值為負。所以 gate 說了算。

## 7.4　真實資料上的比較（SiP dataset, 4,227 筆, 5-fold CV）

| 候選 | Pooled MAE | Median AE | RMSE | vs naive |
|---|---|---|---|---|
| gradient-boosting | 151.79 | 101.03 | 223.71 | +3.1%（不可 serving） |
| naive-estimate | 156.71 | 60.00 | 259.71 | 基準 |
| multiplier-table | 158.78 | 82.00 | 243.12 | −1.3% |
| ridge-regression | 168.75 | 125.64 | 237.21 | −7.7% |
| elastic-net | 170.16 | 127.63 | 237.61 | −8.6% |
| dummy-mean | 216.38 | 191.13 | 280.33 | −38.1% |

三個必講的觀察：
1. **示範資料與真實資料的排名完全翻轉**——14 筆上 ElasticNet 大勝，4,227 筆上輸給 naive。這就是「小樣本排名是噪音」的活教材。
2. 線性模型 MAE 較差但 RMSE 較好（237 vs 260）：它們最小化平方誤差——**目標函數不匹配**，不是 bug。補充實驗用 QuantileRegressor 直接優化 MAE，也只能追平 naive（153.1 vs 152.9）。
3. 正式晉升被 baseline gate 拒絕：`Promotion rejected: candidate model_mae 165.86 does not beat baseline_mae 152.69`——audit log 有紀錄。

# 第 8 章　程式碼導讀(照真實 call chain)

> 讀法:每個小節按「接收什麼 → 做什麼 → 回傳什麼 → 為什麼存在 → 出錯怎辦 → 面試官可能追問」。

## 8.1　前端:Generate Plan 從哪裡開始

- **檔案**:`web-dashboard/src/App.tsx`
- **函式**:`generatePlan()`(約 1629 行)——組 payload(target_date、planning_mode、start/end hour、buffer)→ `POST ${API_BASE_URL}/schedules/generate` → 成功後刷新 schedule、analytics、predictions 狀態。
- **為什麼存在**:把「一鍵排程」收斂成單一 API 呼叫,前端不含任何排程邏輯。
- **出錯**:非 2xx → 顯示錯誤訊息;backend 503(scheduler 掛)會呈現 scheduler unavailable。
- **追問**:「為什麼不在前端排?」→ 排程需要全部任務＋預測＋鎖定項的一致快照,且演算法要被單元測試覆蓋,放前端等於放棄測試與資料一致性。

## 8.2　Backend route → service

- `app/api/schedules.py`:路由薄層——解析 body、注入 `get_current_user`、把 `user_id` 塞進 payload、呼叫 service。無商業邏輯。
- `app/services/schedules.py::generate_schedule()`(29–95 行):
  1. `task_service.list_tasks()` ＋ `fixed_event_service.list_fixed_events()`
  2. `prediction_service.predict_for_tasks()`(見 8.3)
  3. 組 scheduler payload(任務帶 `predicted_minutes`)→ `httpx.post` 到 scheduler `/schedule/generate`,timeout 8 秒
  4. `get_store().save_generated_schedule()` 存 MySQL
  5. `prediction_service.log_served_predictions()` 記 prediction log
- **出錯**:scheduler HTTP 錯誤 → 轉發原狀態碼;連線失敗 → 503 scheduler-service is unavailable(**排程沒有 fallback**——半份排程比沒有排程更糟,這是刻意決策)。
- **追問**:「為什麼預測失敗不擋排程、排程失敗卻直接 503?」→ 預測是排程的**輸入品質增強**(可用估時替代);排程是這個操作的**本體**(無法替代)。

## 8.3　Backend 呼叫 ml-service

- `app/services/predictions.py::predict_for_tasks()`(139–177 行)
  - 接收:user_id、target_date、tasks
  - 做:`build_ml_payload()`(含 analytics 的 partial actual_minutes)→ `httpx.post` 到 ml `/duration/predict`,timeout 8 秒 → 成功後對每筆套 `calibrate_minutes()`(per-user factor),raw 值存 `raw_predicted_minutes`,bounds 同步縮放
  - 回傳:`DurationPredictionResponse`(含 calibration_factor、samples)
  - 出錯:`httpx.RequestError`/`HTTPStatusError` → `build_fallback_predictions()`:直接用估時、`model_name="estimate-fallback"`、`fallback: true`、confidence 0.2
- `get_user_calibration()`(180–199 行):取該使用者最近 20 筆配對 log 的 actual/raw_predicted 中位數,至少 3 筆才啟用,clamp [0.5, 2.0]。**用 raw 而非 served 值算 ratio,校正才不會自我回饋。**

## 8.4　ml-service 內部(serving)

- `app/main.py::predict_task_durations()` → 對每個任務呼叫 `app/predict.py::predict_duration()`
- `load_duration_model()`(lru_cache):`model_registry.py::active_model_path()`(環境變數 → registry → 預設 artifact)→ JSON 載入。**壞 JSON/缺 key/schema major 不合 → 回 None → heuristic。**
- `calculate_predicted_minutes()`:artifact 存在 → `calculate_artifact_prediction()`(依 `model_type` 分派 multiplier 或 `linear_predict`);否則 heuristic。`actual_minutes>0` 時做 0.45 blend。最後 clamp 1–480。
- `calculate_factors()`:線性 → `linear_contributions()`(係數×標準化值,含 baseline,加總=未 clamp 預測);multiplier/heuristic → 逐步乘數增量;blend 另列一項。
- reliability 家族:`get_error_profile()`(category MAE＋sample count)→ `calculate_bounds()`/`calculate_reliability()`/`is_out_of_distribution()`。
- **追問**:「為什麼用 lru_cache 而不是每次讀檔?」→ artifact 讀取在熱路徑上;cache＋`/model/reload` 清空是最簡單的熱更新機制。

## 8.5　訓練端

- `training/train_duration_model.py::train_duration_model()`:load → **validate_rows()(contract gate)** → `split_rows()`(seeded shuffle,至少 10 筆時留 20% holdout)→ `build_category_multipliers()`(clamp 0.75–1.45)→ error profile ＋ sample counts → metadata(`artifact_meta.build_artifact_metadata()`:checksum、commit SHA、版本、bounds)→ 寫 artifact＋metrics → 選配 ClearML。
- `training/train_linear_model.py::train_linear_model()`:同前段流程,但 `fit_linear_artifact()` 用 StandardScaler＋Ridge/ElasticNet,把 scaler_mean/scale、coefficients、intercept、categories、feature_names 匯出成純 JSON(`model_type: "linear-json"`)。評估報 MAE/MedianAE/RMSE＋`sufficient_evidence`。
- `training/compare_models.py::compare_models()`:6 候選 × 5-fold;`select_candidate()` 只在 servable 候選中選 pooled MAE 最低者並記錄理由。
- `training/promote_duration_model.py::promote_duration_model()`:三道 gate(evidence→baseline→regression)→ 版本化複製 → `write_registry_atomic()`(temp＋os.replace)→ `append_audit_entry()`。`--dry-run` 只評估不落地。
- `training/rollback_duration_model.py::rollback_duration_model()`:找目標(預設最近 archived)→ `verify_artifact()` → 翻轉 stage → atomic 寫 → audit。
- **追問**:「training-serving skew 怎麼防?」→ 兩層:(1) encode/推論數學單一實作在 `app/data_contract.py`,訓練與 serving import 同一份;(2) `tests/test_training_serving_parity.py` 把 JSON 推論釘在 fitted sklearn pipeline 上(誤差 <0.01 分鐘)。

## 8.6　測試地圖(147 個)

| 區域 | 檔案(節選) | 保護什麼 |
|---|---|---|
| 資料契約 | `ml-service/tests/test_data_contract.py` | 空資料、缺欄、型態、範圍、重複、ratio 警告、encoding 順序 |
| Parity | `test_training_serving_parity.py` | sklearn vs JSON、endpoint vs reference、determinism、insufficient evidence、contract 拒訓 |
| Serving 降級 | `test_linear_serving.py` | 壞 JSON、schema 不合、缺 key → heuristic;OOD;bounds clamp;legacy artifact |
| Promotion | `test_promotion.py`＋`test_promotion_gates.py` | 三 gate、dry-run、audit、rollback 全路徑 |
| Backend ML | `test_predictions.py`、`test_prediction_logs.py`、`test_calibration.py` | fallback、logging、配對、校正數學、樣本充分性 |
| 隔離 | `test_user_isolation.py` | 跨使用者資料不可見 |
| 排程 | `scheduler-service/tests/` | 演算法單元測試 |

# 第 9 章　排程演算法導讀

檔案:`scheduler-service/app/algorithms/`;入口 `services/scheduler.py::generate_schedule()`。

## 9.1　Priority scoring(`priority_score.py`)

```python
score = priority*10 + deadline_urgency + focus_bonus(4)
        - difficulty*2 - planned_minutes/30
# deadline_urgency: 過期40 / 1天內30 / 3天內20 / 7天內10 / 其他5
# planned_minutes = predicted_minutes or estimated_minutes  <- ML 預測直接影響排程!
```

設計重點:ML 的預測值經由 `planned_minutes()` 進入評分(時間懲罰)與容量占用——這就是「預測服務」與「排程服務」的實際接點。

## 9.2　Topological sort(`topological_sort.py`)

任務可宣告依賴(先做 A 才能做 B)。Kahn 演算法:入度表＋佇列,`preferred_order`(分數排序)作為 tie-break,確保依賴滿足下仍照優先度排。循環依賴 → 這些任務被剔除並產生 warning。複雜度 O(V+E)。

## 9.3　Capacity selection = 0/1 Knapsack(`knapsack.py`)

- 容量 = 空檔總分鐘(扣 buffer),以 **5 分鐘為單位離散化**(`UNIT_MINUTES=5`)。
- DP:`dp[c] = (最佳總分, 選中任務 tuple)`,逆向掃容量防重複選取;同分取任務數多者。
- 複雜度 O(n × capacity/5);一天最多 288 單位、任務數十個,毫秒級。
- **為什麼不用貪婪**:貪婪按分數塞會被大任務卡位;DP 保證總分最優。**Trade-off**:5 分鐘離散化犧牲精度換 DP 表大小(ceil 取整可能高估任務占用最多 4 分鐘)。

## 9.4　Free-slot construction(`schedule_builder.py::build_free_slots`)

規劃視窗(start_hour–end_hour)減去固定行程與鎖定項:把 blockers 按開始時間排序,線性掃描切出空檔;相鄰 blocker 重疊時合併。O(m log m)。

## 9.5　放置與衝突避免(`build_schedule_items`)

拓撲序逐一以 `find_first_fitting_slot()`(first-fit)放入空檔;每放一個任務把該空檔切短並加 buffer。鎖定項(`locked_item_to_blocker`)在切空檔階段就被當成障礙物,**保證重排不會移動使用者鎖住的塊**。放不下的任務進 warnings(誠實告知,不硬塞)。

## 9.6　整體複雜度與取捨

score O(n) → topo O(V+E) → knapsack O(n·C) → slots O(m log m) → 放置 O(n·s)。全鏈路毫秒級。最大取捨:**first-fit 不做全域最優時段分配**(例如把高專注任務排早上)——目前 planning_mode 只影響參數,時段偏好屬 roadmap。

# 第 10 章　API 設計

## 10.1　分層:Public vs Internal

- **Public(backend, `/api/*`)**:有 auth、合約穩定(`docs/api.md`)。
- **Internal(scheduler `/schedule/*`、ml `/duration/*` `/model/*`)**:無 auth(Compose 內網信任邊界)、合約由 backend 適配。

## 10.2　關鍵設計逐項

- **Pydantic validation**:所有 request/response model 定義在 `app/schemas/`;範圍驗證(ge/le/gt)在邊界擋掉髒輸入 → 422。
- **HTTP status codes**:200 成功;201 建立;401 未認證(缺/壞 token,RFC 7235);404 不存在或不屬於你(防資源枚舉);409 衝突;422 驗證失敗;503 依賴服務不可用。
- **Authentication**:Bearer token;`Depends(get_current_user)` 注入使用者,service 層全部以 user_id 過濾。
- **Request ID**:`observability.py` middleware 為每請求產生 request id,回應 header 與結構化 log 都帶——三個服務同一套,跨服務追蹤靠它。
- **Liveness vs Readiness**:`/health` 回固定 `{status, service, version}`(活著);`/ready` 檢查依賴(backend 查 DB、ml 查 artifact 可載)→ 未就緒 503。Compose healthcheck 用它決定啟動順序。
- **Timeout 與 fallback**:backend 對兩個內部服務都是 8 秒;ml 失敗 → 估時 fallback;scheduler 失敗 → 503。
- **Idempotency**:讀取端點天然冪等;`/schedules/generate` 非冪等(每次產生新 run 存入歷史)——這是產品特性(歷史比較),不是缺陷;重複點擊由前端防抖。
- **Backward compatibility**:v0.58.0 的預測新欄位全部 optional-with-default,舊客戶端照常運作;`confidence` 保留原語意。

# 第 11 章　資料庫設計

MySQL 8.4;Alembic 遷移 6 版(`backend-api/alembic/versions/`);測試用 in-memory store 實作同一個 repository 介面。

## 11.1　八張表

| 表 | 用途 | 關鍵欄位/關聯 |
|---|---|---|
| `users` | 帳號 | PK id;email unique;password_hash(自描述格式,600k PBKDF2) |
| `tasks` | 任務 | FK user_id;estimated_minutes、priority、difficulty、requires_focus、category、status、deadline、dependency |
| `fixed_events` | 固定行程 | FK user_id;start/end time、weekday 或 date |
| `execution_logs` | 執行事件 | FK user_id、task_id;event_type(start/pause/complete/skip)、occurred_at |
| `schedule_runs` | 每次 Generate Plan | FK user_id;target_date、request payload、algorithm summary、title |
| `schedule_items` | 排程項 | FK schedule_run_id;task 或 fixed event、start/end、locked、manual 調整 |
| `schedule_templates` | 範本 | FK user_id;可重用的任務組 |
| `prediction_logs` | ML 監控核心 | FK user_id、task_id;model_name/version、predicted、raw_predicted、estimated、actual、target_date、actual_recorded_at |

## 11.2　設計要點

- **User data isolation**:每張業務表都有 user_id,service 層一律過濾;跨使用者存取回 404。
- **Soft delete**:任務刪除以狀態標記(保留 analytics 與外鍵一致性),排程歷史可整筆刪除。
- **Transaction**:schedule_runs＋schedule_items 同交易寫入,不會出現無項目的 run。
- **Index**:user_id＋target_date 複合查詢是熱路徑(儀表板每次載入);prediction_logs 以 user_id+task_id 配對。
- **Migration**:Alembic 順序遷移;容器啟動指令先 `alembic upgrade head` 再 uvicorn;`test_migrations.py` 驗證。
- **為什麼 MySQL**:關聯結構明確(8 表多外鍵)、單節點成熟穩定、Docker 官方映像＋named volume 即可持久化;相對 SQLite 提供真實的網路 DB 營運經驗(備份/restore 演練都在 `scripts/`),相對 PostgreSQL 純屬熟悉度選擇——兩者在本規模等價。

# 第 12 章　Docker 與部署

## 12.1　Compose 拓撲(`docker-compose.yml`)

- 5 個 service:mysql(named volume `mysql_data`)、backend-api、scheduler-service、ml-service、web-dashboard。
- **Image/Container**:image 是建置產物(分層、可快取),container 是 image 的執行實例;每次 `up --build` 重建變更層。
- **Port**:5173/8000/8100/8200 對外;MySQL 容器內 3306、host 3307(避開本機既有 MySQL)。
- **Healthcheck**:每服務打自己的 `/health`(mysql 用 mysqladmin ping);`depends_on: condition: service_healthy` 讓 backend 等 mysql 就緒、dashboard 等 backend。
- **啟動順序**:mysql → (scheduler, ml) → backend(先跑 alembic upgrade head)→ dashboard。
- **環境變數**:backend 以 `ORDOSTACK_*` 讀 DB DSN 與兩個內部服務 URL(`app/config.py`);`.env` 不進 git,`.env.example` 提供模板。
- **Docker network**:Compose 預設 bridge 網路 `ordostack_default`,服務以名字互相解析(`http://ml-service:8200`)。
- **MySQL persistence**:named volume `ordostack_mysql_data`;`docker compose down` 不刪資料,`down -v` 才會。

## 12.2　為什麼 local 用 Docker Compose

一鍵可重現(`docker compose up --build -d`)、依賴封裝(不污染主機 Python/Node)、與正式環境同構的網路與健康檢查語意、named volume 讓資料在重建後存活。

## 12.3　如果要正式上線,還缺什麼(誠實清單)

TLS 與網域、反向代理、secrets manager(目前 .env)、集中式 log/metrics(目前結構化 stdout)、多副本與 orchestration(K8s/ECS)、DB 託管與自動備援(目前 scripts 手動備份/驗證)、內部服務認證(`/model/reload` 目前只受內網保護)、CI/CD 部署管線(目前 CI 只到 runtime gate)。詳見 `docs/aws-deployment-plan.md`(規劃文件,未部署)。

# 第 13 章　MLOps Lifecycle 完整說明

## 13.1　生命週期總覽(全部對應實際程式)

| 階段 | 實作 | 檔案 |
|---|---|---|
| Data collection | 執行紀錄→配對→CSV 匯出 | `services/execution_logs.py`、`/api/ml/duration-feedback` |
| Validation | data contract 1.0.0 可執行驗證＋報告 | `app/data_contract.py`、`training/validate_dataset.py` |
| Training | seeded holdout、兩種 trainer | `train_duration_model.py`、`train_linear_model.py` |
| Experiment tracking | metrics JSON＋選配 ClearML(no-op 安全) | `duration_metrics.json`、`clearml_utils.py` |
| Evaluation | MAE/MedianAE/RMSE vs naive、6 候選 CV | `eval_metrics.py`、`compare_models.py` |
| Registry | local JSON registry、版本化 artifact | `model_registry.json`(本地)、`app/model_registry.py` |
| Promotion gate | evidence→baseline→regression 三道 | `promote_duration_model.py` |
| Deployment | hot reload(清 lru_cache) | `POST /model/reload` |
| Prediction logging | 每次出圖記錄 raw+calibrated | `log_served_predictions()` |
| Monitoring | rolling MAE＋sufficient_data 判定 | `/api/ml/prediction-accuracy`、MLOps view |
| Drift | **尚未實作**(需基準資料) | `FUTURE_ML_ROADMAP.md` |
| Rollback | 驗證後翻轉 registry | `rollback_duration_model.py` |
| Retraining trigger | 手動(資料量閾值見 runbook);自動化尚未實作 | `MLOPS_RUNBOOK.md` |

## 13.2　面試講法(串成一個故事)

> 「每一次使用者按 Generate Plan,系統就記下模型當下說了什麼(raw 和校正後的值都記);每一次任務完成,實際分鐘數就回來配對。這讓我有一個不斷成長的 labeled dataset 和一個誠實的線上評估:模型 rolling MAE vs 使用者自估 rolling MAE。訓練端一切從 data contract 開始——驗證不過就不訓練;訓練完的 artifact 記錄 checksum、commit、環境版本;晉升要過三道 gate,樣本不足會被明確拒絕;上線是熱載入,出事有 rollback,每個決策都在 audit log 裡。」

# 第 14 章　錯誤與降級策略

| 失效情境 | 偵測 | 系統行為 | 使用者看到 | 恢復 |
|---|---|---|---|---|
| ml-service 掛掉 | backend httpx 8s timeout/連線錯 | `build_fallback_predictions()`:預測=估時,`model_name=estimate-fallback`,`fallback:true` | 排程照常產生;MLOps 頁顯示 fallback 模型 | `docker compose restart ml-service` |
| scheduler 掛掉 | 同上 | **不 fallback**,回 503 detail=scheduler-service is unavailable | 錯誤提示,舊排程仍在 | restart;歷史資料無損 |
| MySQL 掛掉 | backend `/ready` 檢查失敗;操作拋錯 | backend 回 5xx;compose healthcheck 標 unhealthy | 儀表板載入失敗 | restart mysql;named volume 資料還在 |
| artifact JSON 損毀 | `load_duration_model()` try/except | 靜默降級 heuristic(`fallback:true`) | 預測仍有,reliability=insufficient-data | 重訓或 rollback+reload |
| artifact schema 不相容 | schema major 檢查 | 同上,拒載 | 同上 | 用相容版本重輸出 |
| unseen category | `is_out_of_distribution()` | global fallback(查表)或零向量(線性)+OOD 旗標 | 該筆標 out-of-distribution、樣本數 0 | 累積該類資料後重訓 |
| 預測超出合理範圍 | `clamp_minutes()` | 強制夾在 1–480 分鐘 | 不會看到 0 或 3000 分鐘 | — |
| migration 失敗 | 容器啟動即失敗(alembic 先跑) | backend 不會以壞 schema 服務 | 啟動失敗訊息 | 修 migration 再 up;上一版可回復 |
| model reload 失敗 | reload 後 metadata 取不到 | `/ready` 503;舊 cache 已清,下一請求走 fallback 鏈 | 服務降級但不中斷 | rollback registry 再 reload |
| registry 損毀 | `load_registry()` 容錯 | 落回預設 artifact 路徑 | 無感 | 重新 promote 重建 |

設計原則:**讀路徑永不中斷(層層 fallback),寫路徑寧缺勿假(排程/遷移直接失敗)**。

# 第 15 章　實際 Demo 講稿(5–8 分鐘)

前置(面試前一晚):`docker compose up --build -d` → `docker compose ps` 全 healthy → 準備一個已有任務與歷史的 demo 帳號;瀏覽器開 `http://localhost:5173`。

## 步驟 1(30s)　開場與健康狀態

- 點哪:終端機 `docker compose ps`。
- 畫面:五個服務 healthy。
- 說:「整套系統五個容器,全部本地。backend 是唯一對外 API,排程和 ML 是內部服務。」
- 可能追問:「為什麼 MySQL 是 3307?」→ host 埠避開本機既有 MySQL,容器內仍 3306。

## 步驟 2(60s)　任務與固定行程

- 點哪:Planner/Tasks 視圖,新增一個任務(給 category、估時、優先度、難度)。
- 說:「這些欄位就是 ML 的五個 input features,也是排程評分的輸入——一份資料兩處用。」

## 步驟 3(90s)　Generate Plan(核心)

- 點哪:Generate Plan 按鈕。
- 畫面:時間軸出現任務塊,避開固定行程;KPI 條顯示容量。
- 說:「這一鍵做了三件事:跟 ml-service 拿每個任務的預測分鐘;把任務+預測+行程交給 scheduler 做評分、拓撲排序、背包選擇、first-fit 放置;存進 MySQL 並記錄 prediction log。」
- 追問點:「排程演算法複雜度?」→ 第 9 章;「預測失敗怎辦?」→ 降級估時,排程照常。

## 步驟 4(60s)　預測解釋

- 點哪:MLOps 視圖的 Predictions for this date 表格。
- 畫面:estimate vs predicted、confidence/reliability。
- 說:「每筆預測有因素分解——例如 90 分鐘的 study 任務預測 129 分:基準 90、category 歷史 +24.8、專注 +6.2、難度 +4.6。界限是歷史誤差帶,不是統計區間;unseen category 會標 out-of-distribution。」

## 步驟 5(60s)　執行與配對

- 點哪:任務 start → complete(demo 可先偷跑一個)。
- 畫面:實際分鐘出現;Live accuracy 面板更新。
- 說:「完成的瞬間,實際時間回寫 prediction log 完成配對。注意這裡——樣本不足 10 筆時,系統顯示『樣本不足,暫無法評判模型』,不給假百分比。」

## 步驟 6(90s)　MLOps 迴圈(終端機)

- 點哪:終端機依序:
  `python ml-service/training/validate_dataset.py`
  `python ml-service/training/compare_models.py`
  `python ml-service/training/promote_duration_model.py --dry-run`
- 畫面:驗證 14/14、六模型比較表(ElasticNet 最低)、`Promotion rejected: insufficient evidence for automatic promotion: 3 evaluation rows (minimum 10)`。
- 說:「這就是我最想展示的:最好的模型『比較贏了』但 gate 拒絕自動上線,因為 3 筆 holdout 不是證據。系統的誠實是設計出來的。」

## 步驟 7(30s)　收尾

- 說:「整個迴圈——資料、驗證、訓練、比較、gate、部署、監控、回滾——都能在這台筆電上重現,147 個測試守著。」

## 如果 Demo 突然壞掉

- 畫面掛了 → 切終端:`curl localhost:8000/health` 逐服務診斷,順勢講 liveness/readiness 與降級設計:「這正好展示 fallback——ml-service 停掉,排程照常,預測變估時。」(可事先 `docker compose stop ml-service` 當彩蛋)
- 全掛 → 打開 `docs/images/` 截圖 + `model_comparison.json` 講數字;Demo 的每一步都有對應文件,故事不中斷。

# 第 16 章　常見面試問題與答案(52 題)

> 答案是「口語版」,可直接照講;括號內是可加碼的深度。

## A. 專案動機(3 題)

**Q1 為什麼做這個專案?**
「我常低估任務時間,一天結束計畫永遠沒做完。這個痛點剛好是個完美的 ML 練習場:每完成一個任務就自動產生一筆帶標籤的資料。我要的不是展示模型,而是練完整的 ML 系統:資料迴路、訓練、部署、監控、回滾。」

**Q2 為什麼不用現成的排程 App?**
「現成 App 不會告訴我『你這種類型的任務通常會超時 30%』。而且自己做才能控制整條資料管線——這是作品集專案,學習密度優先。」

**Q3 這個專案最困難的部分?**
「不是寫模型,是設計『資料不足時系統該說什麼』。讓 gate 拒絕、讓 UI 顯示樣本不足、讓 confidence 不冒充機率——誠實需要工程。」

## B. 系統架構(5 題)

**Q4 為什麼不用單體架構?微服務是否過度設計?**
「單機跑,單體其實可以,我承認。但拆開的理由是邊界:排程演算法、ML serving、產品 API 的變更頻率和依賴完全不同。拆開後 sklearn 永遠進不了 runtime、模型熱更新不動排程、每個服務可以獨立測試。成本是多兩個容器和 HTTP 呼叫——在這個規模我付得起。真要說,這是『刻意的學習型決策』,我能講出兩邊的代價。」

**Q5 服務之間怎麼通訊?為什麼不用 message queue?**
「同步 HTTP/JSON,8 秒 timeout。因為互動是請求-回應型(排程要立刻回給使用者),不是事件流。MQ 會引入不必要的營運複雜度;等到有『任務完成觸發自動重訓』這種非同步需求才值得。」

**Q6 backend 掛了怎麼辦?**
「backend 是單點,掛了前端就沒服務——單機系統我接受這點。資料安全由 MySQL volume 保證;compose healthcheck 會標 unhealthy,restart 即恢復,狀態都在 DB。」

**Q7 如果使用者增加到十萬人,怎麼調整?**
「分四步:(1) backend/scheduler/ml 都無狀態,水平擴多副本+load balancer;(2) MySQL 上讀寫分離與連線池,prediction_logs 最大就先分表;(3) 模型 per-user calibration 移到特徵而不是後處理,artifact 進物件儲存+CDN;(4) 監控從 rolling MAE 升級成分群監控。架構的分層讓這些是漸進演化,不是重寫。」

**Q8 為什麼排程結果存 DB 而預測不直接存?**
「排程是使用者資產(歷史、比較、鎖定);預測是模型輸出,存在 prediction_logs 是為了監控配對,不是產品資料。兩者生命週期不同。」

## C. Python / FastAPI(4 題)

**Q9 為什麼選 FastAPI?**
「Pydantic 驗證讓 request/response 合約自動成文件(OpenAPI);型別提示配 IDE 和測試;async 支援夠用;三個服務同框架,observability middleware 直接重用。」

**Q10 routes/services/repositories 分層的意義?**
「route 只做 HTTP 翻譯,service 是商業邏輯,repository 藏儲存細節。好處實測得到:同一套 service 測試跑 in-memory store,Docker 跑 MySQL,測試快又不用 mock 一堆 SQL。」

**Q11 依賴注入在哪裡用到?**
「`Depends(get_current_user)` 把 token 驗證從每個 route 抽走;store 用 `get_store()` 工廠依環境切 MySQL/in-memory。測試時 monkeypatch 這些注入點,不碰業務程式。」

**Q12 Pydantic 幫你擋過什麼?**
「priority=9 的手誤在進 service 之前就 422;ml-service 的 `estimated_minutes: gt=0` 讓除以零在邊界就不可能發生。驗證放邊界,內部程式就能假設資料乾淨。」

## D. React 串接(3 題)

**Q13 前端怎麼跟後端整合?**
「單一 `API_BASE_URL`,fetch 包一層 `requestJson` 統一帶 token 和錯誤處理;TypeScript 型別(如 `ApiPredictionAccuracy`)跟 backend schema 對齊,加欄位時 tsc 會逼我處理所有使用點。」

**Q14 狀態管理怎麼做?**
「useState + 少量 derived state,沒上 Redux。單頁儀表板的狀態就是『目前日期的各種資料快照』,fetch 後 setState 足夠;引 Redux 是為了工具而工具。」

**Q15 為什麼 UI 要顯示『樣本不足』而不是一直顯示準確率?**
「因為 2 筆配對算出的 95% 是謊言。backend 回 `sufficient_data` 和門檻,前端在門檻下顯示『樣本不足,暫無法評判模型』——監控的第一原則是不誤導自己。」

## E. REST API(3 題)

**Q16 你的 API 怎麼處理版本相容?**
「加法演進:新欄位一律 optional 有預設(這次 reliability/factors 全是),舊欄位語意不變(`confidence` 保留)。真要破壞性變更才開 /v2——目前沒需要。」

**Q17 404 和 403 怎麼選?**
「存取別人的資源回 404 而不是 403:不洩露『這個 ID 存在』。授權失敗和不存在,外部觀察應該不可區分。」

**Q18 幂等性怎麼考慮?**
「GET 全冪等;generate 刻意非冪等因為每次是新的 run(歷史功能);未來若加金流式操作才需要 idempotency key。知道哪裡『不需要』也是設計。」

## F. MySQL(4 題)

**Q19 為什麼用 MySQL 不用 SQLite/PostgreSQL?**
「SQLite 夠單機用,但我要練真實的網路 DB 營運:migration、備份/還原演練、healthcheck、named volume。MySQL vs PostgreSQL 在本規模等價,選熟悉的。重點是 repository 層隔離了這個選擇——測試根本不碰 MySQL。」

**Q20 migration 怎麼管理?**
「Alembic 六個版本,容器啟動先 `alembic upgrade head` 再起 uvicorn——服務永遠不會以舊 schema 運行。`test_migrations.py` 驗證鏈條完整。」

**Q21 怎麼防 SQL injection?**
「全部參數化查詢,沒有字串拼 SQL;輸入又先過 Pydantic。安全審計腳本(`scripts/security_audit.py`)是 CI 閘門之一。」

**Q22 prediction_logs 為什麼要存 raw 和 calibrated 兩個值?**
「per-user calibration 是用『actual/raw』的中位數算的。如果只存校正後的值,校正因子會吃到自己的輸出,正回饋失控。存 raw 是打斷回饋環的關鍵——這是我最得意的小設計之一。」

## G. Docker(3 題)

**Q23 healthcheck 和 depends_on 怎麼配合?**
「每個服務有 /health;compose 用 `condition: service_healthy` 排啟動順序:mysql 健康了 backend 才啟動(它要先跑 migration),backend 健康了 dashboard 才起。避免啟動競態。」

**Q24 資料會不會因為容器重建消失?**
「不會,MySQL 資料在 named volume `ordostack_mysql_data`;`down` 保留,`down -v` 才刪。備份腳本與還原驗證在 `scripts/backup_mysql.*`。」

**Q25 image 怎麼保持小?**
「runtime requirements 和 training requirements 分離是關鍵:sklearn 只在訓練環境,ml-service 的 image 只裝 FastAPI+stdlib 推論。這就是 JSON 係數匯出的部署紅利。」

## H. 排程演算法(4 題)

**Q26 排程的核心流程?**
「五步:priority scoring(優先度×10+期限緊迫度+專注加成−難度×2−時長/30)→ Kahn 拓撲排序處理依賴 → 0/1 背包在可用分鐘內選總分最大的任務組 → 固定行程和鎖定項切出空檔 → first-fit 放置+buffer。」

**Q27 為什麼用 DP 背包不用貪婪?**
「貪婪會被高分大任務卡位,留下塞不進的碎片。容量以 5 分鐘離散化後 DP 表最多 288 格,O(n×288) 毫秒級,買得起最優解。」

**Q28 循環依賴怎麼辦?**
「Kahn 排序做不完的節點就是環上的,這些任務被剔除並回傳 warning——寧可少排也不產生矛盾的計畫。」

**Q29 這個排程和 ML 在哪裡交會?**
「`planned_minutes = predicted_minutes or estimated_minutes`。預測值影響評分的時間懲罰和背包的容量占用——模型準,一天塞的量就真實。這也是為什麼預測要 clamp:一個 3000 分鐘的離譜預測會毀掉整天排程。」

## I. Machine Learning(6 題)

**Q30 為什麼不用神經網路?**
「三個理由:14 筆資料、5 個 tabular 特徵、需要可解釋。DNN 在這三點上全輸:樣本差三個數量級、文獻上小表格資料樹/線性更強、黑盒解釋要另做。等資料上千筆、加入文字特徵時才是 DNN 的題目——roadmap 有寫觸發條件。」

**Q31 只有 14 筆資料,這個模型有意義嗎?**
「示範資料上的數字沒有統計意義——系統到處標 insufficient evidence。所以我另外把 pipeline 拿到真實資料驗證:轉換了公開的 SiP 資料集,4,227 筆真實商業任務的估時與實際工時。結果非常誠實:evidence gate 通過了,但沒有模型贏過使用者自己的估時,baseline gate 把它們全擋下。這個專案有意義的從來不是 14 筆的 MAE,而是:資料迴路在生產真資料、pipeline 在 4,000 筆規模端到端可重現、而且 gates 在兩種資料規模都做出了正確決策。」

**Q32 Ridge/ElasticNet 比 production 好,為什麼沒直接替換?**
「這題我有兩層答案。第一層:14 筆示範資料上 ElasticNet 贏,但 3 筆 holdout 不構成證據,evidence gate 直接拒絕。第二層更有說服力:我後來在 4,227 筆真實 SiP 資料上重跑了整個比較——**排名完全翻轉**,ElasticNet 反而輸 naive 8.6%,正式晉升被 baseline gate 拒絕(audit log 有紀錄)。這證明當初不直接替換是對的:小樣本的排名就是噪音。serving 能力我全準備好了(JSON artifact+parity test),哪天模型真的贏了,晉升只是一個指令。」

**Q33 如何避免 data leakage?**
「四道防線:(1) data contract 明列禁用欄位(title/id);(2) holdout 在任何 fit 之前切;(3) 評估配對用 raw 預測,不用摻了 actual blend 或 calibration 的 served 值;(4) 已知風險誠實記錄——資料沒有 user_id/timestamp,無法做 group/time split,DATA_CARD 寫明這會讓 CV 偏樂觀。」

**Q34 為什麼使用 MAE?**
「單位是分鐘,使用者聽得懂『平均差 5 分鐘』;對離群值比 RMSE 穩健。但我不只看 MAE——Median AE 看典型情況,RMSE 看大誤差懲罰,三個一起才知道誤差分佈形狀。」

**Q35 confidence 是真正的機率嗎?**
「不是,我直說。它是『1 − category 歷史 MAE/估時』的規則分數,沒有經過 calibration。所以 v0.58 加了誠實的表達:歷史誤差帶(bounds)、reliability 標籤、樣本數;樣本 <3 一律 insufficient-data。真的 prediction interval 要等 100+ 筆殘差做 conformal——在 roadmap。」

## J. 模型評估與 Feature Engineering(4 題)

**Q36 你的 cross-validation 怎麼做的?**
「5-fold,shuffle+固定 seed。每 fold 所有候選重新 fit(包括查表的 multiplier 重算),在該 fold 的測試列上預測;row-level 誤差跨 fold 匯總算 pooled MAE/MedianAE/RMSE,也保留 per-fold MAE 看變異。」

**Q37 unseen category 怎麼處理?**
「查表:落回 global multiplier。線性:one-hot 全零=『平均 category』。兩者都會標 out_of_distribution:true、sample_count:0、reliability:insufficient-data——預測照給,但誠實標示這是外推。」

**Q38 為什麼要 StandardScaler?**
「estimated_minutes 是幾十到幾百,one-hot 是 0/1。不縮放,正則化會不公平地懲罰大尺度特徵的係數。縮放後係數還變成『每個標準差的影響分鐘數』,可解釋性更好。」

**Q39 特徵為什麼這麼少?會不會太簡單?**
「五個特徵是刻意的。每加一個特徵,14 筆資料的自由度就更透支。先讓小特徵集+資料迴路轉起來,特徵擴充(星期幾、時段、歷史滾動統計)等資料量到位——而且擴充時 data contract 會逼我同步 training 和 serving。」

## K. MLOps(5 題)

**Q40 training 和 serving 如何保持一致?**
「最強的一招:同一份程式。encode 和線性推論數學在 `app/data_contract.py`,訓練 import 它、serving 也 import 它,物理上不可能分岔。再加 parity test 把 JSON artifact 的預測釘在 fitted sklearn pipeline 上(<0.01 分)。skew 最常見的來源——兩份手寫的 preprocessing——在這裡不存在。」

**Q41 模型壞掉怎麼辦?**
「分層降級:artifact 壞 JSON/缺 key/schema 不合 → ml-service 內部降 heuristic;ml-service 整個掛 → backend 降估時 fallback。兩層都有測試。修復用 rollback CLI:驗證目標 artifact 後翻 registry,POST /model/reload 生效,全程 audit log。」

**Q42 為什麼需要 model registry?**
「三個回答:(1) 部署解耦——訓練產出候選,registry 決定誰在線上;(2) 歷史——每個版本的 artifact 和 metrics 都留著,rollback 才有對象;(3) 審計——誰在什麼時候上了什麼模型、憑什麼 metrics。我用 local JSON 實作了這三件事;換 MLflow/ClearML 是規模問題,概念相同。」

**Q43 promotion gate 具體怎麼設計?**
「三道,順序重要:先 evidence(≥10 筆 out-of-sample,否則明確輸出 insufficient evidence for automatic promotion)、再 baseline(要贏 naive)、再 regression(不能比現任差 5% 以上)。可以 --dry-run 預演;override 是顯式 flag 且被 audit 記錄——人可以否決 gate,但要留名。」

**Q44 如果要接 ClearML/MLflow,要改多少?**
「很少。訓練和晉升已經有 hook(`clearml_utils.py`,未設定時 no-op):track_training_run 記 experiment,register_promoted_model 記 model。切到 server 版只是設環境變數;pipeline 本身不依賴它——tracking 是加分,不是骨架。」

## L. 測試(3 題)

**Q45 測試策略是什麼?**
「三層:單元(演算法、契約、指標數學)、服務內整合(TestClient 打 API,in-memory store)、跨服務煙霧測試(Docker 起真的五個容器跑 e2e_smoke.py+browser_smoke.py)。147 個測試,重點覆蓋失效路徑:壞 artifact、掛掉的服務、gate 拒絕、rollback。」

**Q46 ML 部分怎麼測?最難測的是什麼?**
「可測性靠確定性:固定 seed 讓訓練可重現(同 seed 係數 bit 級相同);parity test 鎖 training-serving;promotion 測試覆蓋三 gate×通過/拒絕/override。最難的是『統計上對不對』——13 筆測不出來,所以我測的是『系統知不知道自己不知道』:insufficient evidence 的觸發路徑全有測試。」

**Q47 你怎麼決定測什麼、不測什麼?**
「按失效成本排:資料壞掉毀模型→contract 測試;skew 毀信任→parity;壞模型上線→gate;服務掛→fallback。UI 像素級變化成本低,用 visual regression 腳本粗篩就好。」

## M. Security(2 題)

**Q48 安全上做了什麼?**
「密碼 PBKDF2-HMAC-SHA256 600k 迭代、自描述格式可升級;Bearer token;所有查詢 user_id 隔離(有測試);參數化查詢;secrets 全在 .env 不進 git;依賴掃描(pip-audit/npm audit)在 CI 閘門,v0.57 剛清完九個 advisory;security_audit.py 每次 ponytail 都跑。」

**Q49 ml-service 沒有 auth,不怕嗎?**
「它只在 compose 內網,對外只有 backend。這是明確記錄的信任邊界。若要多機部署,/model/reload 和 /duration/predict 要加 service token——在 roadmap,而且我知道為什麼現在可以不做。」

## N. Scaling / Failure / Trade-off / 限制(3 題)

**Q50 這個專案最大的技術取捨是哪個?**
「JSON 係數匯出 vs pickle 整條 pipeline。pickle 零重實作但 runtime 要 sklearn、有版本和反序列化風險、artifact 不可讀;JSON 匯出 runtime 零依賴、artifact 可 diff 可審計,代價是只支援線性模型+要 parity test 保護。我選 JSON,因為現階段最好的候選就是線性,而部署簡單和可審計是我最看重的。樹模型真的贏的那天,再付 sklearn-in-runtime 的成本。」

**Q51 哪一部分是你真正做的?(AI 協作時代的必答題)**
「這個專案我用了 AI coding agent 協作,我的角色是:定義問題和驗收標準、審每一個設計決策(例如拒絕在 14 筆資料上宣稱模型有效)、驗證每個測試和指標。證明理解的方式很簡單:你現在可以關掉投影片問我任何一段——比如 promotion gate 為什麼 evidence 在 baseline 前面?因為 metrics 不可信時比較大小沒有意義。第 18 章有我的逐項貢獻標記表,我對『哪些是我的、哪些是協作的』完全透明。」

**Q52 這個專案現在最大的限制是什麼?**
「資料。14 筆示範資料意味著所有模型結論都是方向性的;沒有真實多使用者流量;drift 監控沒資格開。第二是單點 backend 和本機部署。但這些限制都被系統『知道』:gate 擋著、UI 標著、roadmap 寫著觸發條件——我認為誠實面對限制正是這個專案的價值。」

# 第 17 章　不知道答案時的誠實回答方式

面試被問倒是常態。以下模板讓「不知道」變成加分,前提是絕不裝懂。

## 17.1　四段式安全模板

1. **承認邊界**:「這個我沒有實際做過/沒有深入研究。」
2. **靠近已知**:「但它讓我聯想到我專案裡的 X——原理上應該類似……」
3. **給出推理**:「如果讓我猜,我會從 A 和 B 兩個方向想,因為……」
4. **收尾承諾**:「這是我的推測,不是經驗。如果這對這個職位重要,我回去會先讀 ___ 把它補起來。」

## 17.2　三種情境示範

- **完全沒聽過的名詞**(例:被問 feature store):「我沒用過 feature store 產品。我專案裡對應的問題是 training-serving 特徵一致,我用共用 data contract 模組解決;我理解 feature store 是把這件事平台化——線上線下同一份特徵定義加低延遲讀取。細節我需要查證。」
- **做過但忘了細節**:「我記得結論是 X,但推導細節我不確定,不想憑印象亂講。可以講我確定的部分……」
- **超出專案規模的問題**(例:十億級 QPS):「我的專案是單機規模,沒有這個量級的實戰。我能講的是原理層面的方向……,但實際數字我沒有第一手經驗。」

## 17.3　紅線

- 不編造數字、論文、工具名。
- 不把「聽過」說成「用過」。
- 被戳破一次的代價大於十次誠實的「不知道」。

# 第 18 章　個人貢獻確認表

> **請親自填寫**。此表刻意不預填「全部自己做」——AI 協作專案的可信度來自精確標記。
> 標記:A=我親自設計實作 / B=AI 協助完成但我完全理解並驗證 / C=我看過但尚未完全理解 / D=尚未實作 / E=我需要再練習

| # | 區塊 | 具體項目 | 標記(A–E) | 備註 |
|---|---|---|---|---|
| 1 | 產品 | 產品定位、MVP 範圍、Non-goals | ____ | |
| 2 | 架構 | 五服務切分與信任邊界 | ____ | |
| 3 | 前端 | App.tsx 六視圖與 generatePlan 流程 | ____ | |
| 4 | 後端 | routes→services→repositories 分層 | ____ | |
| 5 | 後端 | 驗證與 user 隔離(auth.py、dependencies.py) | ____ | |
| 6 | 排程 | priority_score 公式與權重 | ____ | |
| 7 | 排程 | topological_sort(Kahn) | ____ | |
| 8 | 排程 | knapsack DP 與 5 分鐘離散化 | ____ | |
| 9 | 排程 | build_free_slots/first-fit 放置 | ____ | |
| 10 | ML | data_contract.py(schema、驗證、encode、linear_predict) | ____ | |
| 11 | ML | train_duration_model.py(multiplier) | ____ | |
| 12 | ML | train_linear_model.py(JSON 匯出) | ____ | |
| 13 | ML | compare_models.py 六候選比較 | ____ | |
| 14 | ML | eval_metrics.py(MAE/MedianAE/RMSE/evidence) | ____ | |
| 15 | MLOps | promotion 三 gate＋audit＋dry-run | ____ | |
| 16 | MLOps | rollback CLI | ____ | |
| 17 | MLOps | serving 降級鏈(壞 artifact→heuristic→估時) | ____ | |
| 18 | MLOps | prediction logging＋配對＋calibration | ____ | |
| 19 | MLOps | reliability/bounds/factors 設計 | ____ | |
| 20 | DB | 8 張表 schema 與 Alembic 遷移 | ____ | |
| 21 | Docker | compose、healthcheck、volume | ____ | |
| 22 | 測試 | ml-service 63 測試 | ____ | |
| 23 | 測試 | backend 73 測試 | ____ | |
| 24 | 測試 | e2e/browser smoke | ____ | |
| 25 | 文件 | docs/ml 六件套(audit/data/model/experiment/runbook/roadmap) | ____ | |

# 第 19 章　七天面試準備計畫

> 每天 2–3 小時。原則:動手 > 閱讀;每天都要「改一個小東西+跑測試」,理解是改出來的。

## Day 1　跑起來+架構

- 讀:README、ARCHITECTURE.md、本手冊第 1–5 章。
- 做:`docker compose up --build -d` → `docker compose ps` → 五個 /health 都 curl 一次 → 完整點一輪 UI。
- 改:把某個 /health 回應加一個欄位,重建容器看變化,然後改回來。
- 練:30 秒/1 分鐘介紹各講 3 次(錄音聽)。
- 驗收:能不看圖畫出五服務架構與資料流向。

## Day 2　排程演算法

- 讀:scheduler-service/app/algorithms/ 全部五個檔案+第 9 章。
- 做:`python -m pytest scheduler-service/tests -q`;手算一個任務的 score 再用程式驗證。
- 改:把 focus_bonus 從 4 改成 10,跑測試看哪些壞了,理解為什麼,改回。
- 練:Q26–Q29。
- 驗收:能在白板寫出 score 公式和 knapsack DP 轉移式。

## Day 3　Backend 與資料庫

- 讀:services/schedules.py、services/predictions.py、repositories/、第 8、10、11 章。
- 做:`python -m pytest backend-api/tests -q`;用 curl 帶 token 打 /api/schedules/generate。
- 改:在 prediction-accuracy 回應加一個欄位(如 window 起始日),補測試,再移除。
- 練:Q9–Q22。
- 驗收:能講出 Generate Plan 的 8 步 call chain 不看小抄。

## Day 4　ML 訓練管線

- 讀:data_contract.py、train_linear_model.py、compare_models.py、eval_metrics.py、第 6–7 章。
- 做:依序跑 validate_dataset.py → compare_models.py → train_linear_model.py;打開三個輸出 JSON 逐欄看懂。
- 改:在 CSV 加一筆自己的真實任務資料,重跑比較,觀察數字變化;把 priority 改成 9 看 validation 擋下。
- 練:Q30–Q39。
- 驗收:能解釋 ElasticNet 每個係數的意義與 pooled MAE 的算法。

## Day 5　MLOps:gate/reload/rollback

- 讀:promote_duration_model.py、rollback_duration_model.py、app/predict.py、第 13–14 章。
- 做:dry-run 晉升看拒絕訊息 → --allow-insufficient-evidence 晉升 → curl /model/reload → rollback → 再 reload;全程看 promotion_audit.jsonl。
- 改:故意把 duration_model.json 改成壞 JSON,curl /duration/predict 確認 heuristic fallback,還原。
- 練:Q40–Q44。
- 驗收:能演示完整晉升→回滾迴圈並解釋每個 gate。

## Day 6　測試與品質閘門

- 讀:test_training_serving_parity.py、test_promotion_gates.py、test_linear_serving.py、第 16 章 L 節。
- 做:`python scripts/ponytail.py --include-compose-config`;`python scripts/e2e_smoke.py`。
- 改:寫一個新測試(例如:estimated_minutes=1440 邊界的預測仍在 bounds 內)。
- 練:Q45–Q49。
- 驗收:能說出 147 個測試分佈與三個最重要的失效路徑測試。

## Day 7　總演練

- 做:完整 Demo 演練 2 次(計時 8 分鐘內),一次故意 stop ml-service 練降級話術。
- 填:第 18 章貢獻表全部 25 項。
- 練:52 題快問快答(找人抽問或自問自答);第 17 章模板演練 3 個沒準備的問題。
- 驗收:Demo 流暢、貢獻表填完、C/E 標記項目列成考前清單。

# 第 20 章　名詞表(初學者友善)

| 名詞 | 白話解釋(以本專案為例) |
|---|---|
| regression(迴歸) | 預測連續數值的 ML 任務——這裡是「幾分鐘」,不是「會/不會超時」的分類 |
| feature(特徵) | 模型的輸入欄位:估時、類別、優先度、難度、需否專注 |
| label / target(標籤/目標) | 要學的答案:actual_minutes(實際花的分鐘) |
| baseline(基準) | 不用 ML 的對照組:直接拿使用者估時當預測。模型必須贏它才有存在價值 |
| MAE | 平均絕對誤差:預測差多少分鐘的平均。越小越好 |
| Median AE | 誤差的中位數:一半的預測差不到這個數;不被極端值拉動 |
| RMSE | 均方根誤差:先平方再平均開根號,大錯會被放大懲罰 |
| cross-validation(交叉驗證) | 資料輪流當考題:切 5 份,每份都當一次驗證集,分數更可信 |
| holdout | 訓練前先藏起來的一份資料,最後用來考模型 |
| overfitting(過擬合) | 模型背答案:訓練分數漂亮、新資料就爛。小資料時最大敵人 |
| regularization(正則化) | 給大係數加罰款(L1/L2),逼模型別把噪音當訊號 |
| StandardScaler | 把每個特徵縮到平均 0、標準差 1,讓正則化公平、係數可比較 |
| one-hot encoding | 把類別變成 0/1 欄位:study → [0,1],coding → [1,0] |
| calibration(校正) | 依某人的歷史「實際/預測」比例微調預測——你總是超時 20%,就幫你乘 1.2 |
| model drift(模型漂移) | 世界變了模型沒變:習慣改變後,舊模型的誤差悄悄上升 |
| model registry(模型註冊表) | 記錄「哪個版本在線上、歷史有哪些、各自成績」的帳本(本專案:local JSON) |
| artifact(產物) | 訓練輸出的檔案:這裡是含係數/查表+完整出處資訊的 duration_model.json |
| inference(推論) | 用訓練好的模型算預測(相對於 training) |
| fallback(降級) | 主要方案掛掉時的備援:壞 artifact→heuristic;ml-service 掛→用估時 |
| migration(遷移) | 資料庫結構的版本化變更腳本(Alembic),讓 schema 演進可重現、可回退 |
| repository layer | 把「怎麼存」藏在介面後:同一套邏輯可跑 MySQL 或記憶體(測試用) |
| dependency injection(依賴注入) | 函式要的東西由框架給(如 get_current_user),測試時好替換 |
| liveness | 「活著嗎」:/health,行程還在就 ok |
| readiness | 「能服務嗎」:/ready,還要檢查 DB/模型等依賴就緒 |
| idempotency(冪等) | 同一請求重複發,結果不變(GET 是;generate 刻意不是) |
| data contract(資料契約) | 訓練與 serving 共同遵守的欄位/範圍/編碼白紙黑字(data_contract.py) |
| training-serving skew | 訓練和上線的特徵處理不一致造成的隱形誤差;用共用程式+parity test 防 |
| promotion gate(晉升閘門) | 模型上線前的自動檢查:證據夠嗎?贏 baseline 嗎?比現任差嗎? |
| out-of-distribution(OOD) | 輸入落在訓練資料沒見過的區域(新類別/極端估時),預測是外推要小心 |

---

*本手冊由 repository 實際程式碼生成,對應 v0.58.0。重新生成 Word 檔:`python docs/interview/build_handbook.py`*
