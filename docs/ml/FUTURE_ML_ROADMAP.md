# Future ML Roadmap — 尚未實作，且現在不該實作

> 本文件列出「聽起來很酷但目前沒有資料基礎」的功能。每項都寫清楚缺什麼、何時才值得做。
> **這些功能目前皆不存在於程式碼中**；任何對外介紹不得宣稱已完成。

## 判斷原則

現階段（14 筆 curated demo 資料、單機 local-first）唯一正確的 ML 投資是：把資料收集迴路做誠實、把 serving 做可靠。模型升級全部等資料。

## 1. Prediction interval / conformal prediction

- **需要 label**: 既有 target 即可
- **需要 features**: 既有 + 至少 100–200 筆真實配對殘差
- **目前缺少**: 足量殘差樣本（現有 band 只是訓練殘差 MAE）
- **何時值得**: paired predictions ≥ 100
- **離線評估**: coverage rate（宣稱 80% 區間實際涵蓋率應 ≈ 80%）
- **風險**: 樣本不足時區間假準；**誤導性指標**: 只報平均寬度不報 coverage

## 2. Drift monitoring（真正的統計檢定）

- **需要**: 穩定基準期資料（≥ 200 筆）＋當期窗口
- **目前缺少**: 基準資料；現在只能顯示 warning 不能宣稱「偵測到 drift」
- **何時值得**: 連續 4 週每週 ≥ 30 筆配對
- **離線評估**: 注入已知分佈變化的回放測試
- **風險**: 小樣本 KS/PSI 檢定天天誤報；**誤導性指標**: 無多重檢定校正的 p-value

## 3. Transformer/embedding 處理任務標題

- **需要 label**: 大量 (title, actual_minutes) 配對（≥ 數千筆）
- **目前缺少**: 資料量差 2–3 個數量級；title 目前被 data contract 列為禁用欄位（隱私＋過擬合）
- **何時值得**: 多使用者、萬筆級資料且完成去識別化管線
- **離線評估**: 與 tabular baseline 的 MAE 差異＋分群公平性
- **風險**: 記憶特定標題、隱私外洩；**誤導性指標**: 只看整體 MAE 不看 per-user 泛化

## 4. 任務完成機率分類（會不會做完）

- **需要 label**: 「排入計畫但未完成」的明確負樣本——需先定義 skip/rollover 語意
- **目前缺少**: 負樣本定義與記錄（execution log 有 skip 事件但語意未清理）
- **何時值得**: 每位活躍使用者 ≥ 200 筆計畫項目結果
- **離線評估**: AUC＋calibration curve
- **風險**: 自我實現預言（預測不會完成→排程降權→真的沒完成）；**誤導性指標**: 不平衡資料上的 accuracy

## 5. RL / Contextual Bandit 自動排程

- **需要 label**: 排程方案的 reward（滿意度、完成率、重排率）
- **目前缺少**: reward 訊號完全不存在；排程好壞目前無 ground truth
- **何時值得**: 先有 A/B 基礎設施與 ≥ 千次「排程→結果」迴圈
- **離線評估**: off-policy evaluation（IPS/DR）
- **風險**: 極易過度干預使用者；**誤導性指標**: 模擬環境 reward
- **註**: 現行 scheduler 的規則式演算法（priority scoring + topological sort + capacity）可解釋、可預期，是正確的 baseline。

## 6. 即時自動重新訓練／全自動 promotion

- **需要**: 穩定的 evidence gate 歷史（多次人工晉升皆無回歸）＋自動化 rollback 演練
- **目前缺少**: 資料量使 evidence gate 永遠拒絕，自動化沒有意義
- **何時值得**: 每週自然新增 ≥ 50 筆配對、連續 3 次人工晉升順利
- **風險**: 壞資料自動進 production；**誤導性指標**: 「自動化率」

## 7. Production ClearML Server / AWS 部署

- **目前狀態**: ClearML 為 optional no-op 整合（`clearml_utils.py`）；AWS 僅存在規劃文件（`docs/aws-deployment-plan.md`）
- **目前缺少**: 多人需求、預算、secrets 管理（本專案規則：不用付費 API、完全本地）
- **何時值得**: 出現第二位真實使用者之後
- **風險**: 過早雲端化燒錢並拖慢迭代

## 8. 多使用者推薦／排程滿意度預測

- **需要 label**: 滿意度回饋 UI 與資料表（不存在）
- **何時值得**: 有滿意度收集功能且 ≥ 500 筆評分
- **風險**: 用 proxy metric（如「沒被改動」）冒充滿意度
