# 前端介面與使用者功能改善計畫

> **日期:** 2026-07-08
> **依據:** 對 `web-dashboard/src/App.tsx`（2632 行）、`styles.css`、`i18n.ts` 的逐行審視
> **定位:** OrdoStack 從 Demo MVP 走向可日用產品的前端路線圖

## 現況評估

值得肯定的地方：功能面完整（任務 CRUD、固定行程、排程生成/歷史/比較/匯出、執行紀錄、分析、i18n），aria 標籤覆蓋率高，空狀態有文案，錯誤有 alert banner 加 Retry。這是一個「功能都在」的 MVP。

真正的問題不是缺功能，而是三類結構性缺陷：**誠實性、時間感、操作成本**。

## 核心問題（依嚴重度排序）

### 1. 誠實性：介面顯示編造的數字（🔴 最嚴重）

一個以「估時 vs 實際」為核心價值的產品，自己的儀表板卻在編數字，這會從根本破壞用戶信任：

- `planScore = 82 + 排程任務數*4 - 跳過數*6`（上限 98）——「AI review / Plan quality」分數是**拼湊公式**，與計畫品質無關。
- ~~model panel 寫死 `v0.5.0` / `v0.2.0`~~（本次已修正：改顯示真實模型名稱與版本）。
- 預測信心值（`confidence`）後端有回傳，前端完全沒用。
- 通知鈴鐺與 Command palette 按鈕是 `disabled` 的死按鈕；固定行程列的 `MoreHorizontal` 按鈕沒有 onClick。
- 未生成排程時的 fallback 時間軸把任務**假裝排在 09:00/10:45/13:30/15:00**——用戶看到的「排程」其實是裝飾品，和真排程視覺上無法區分。

**方向：** 每個數字都要能回答「這是怎麼算的」。Plan score 改為由真實訊號構成（排程覆蓋率、依賴滿足、預測與估時偏差、跳過原因），或乾脆先移除；fallback 時間軸必須明確標示「未排程預覽」；死按鈕移除或實作。

### 2. 時間感：時間軸是清單，不是時間軸（🟡）

對排程工具而言「現在幾點、還剩多少時間」是第一級資訊：

- 區塊高度與時長無關，60 分鐘和 15 分鐘看起來一樣大。
- 區塊之間的空檔（可自由運用的時間）完全不可見——但這正是排程器最有價值的輸出。
- ~~沒有「現在」指示~~（本次已加：當前時段高亮 + Now 標籤，每分鐘更新）。
- 進行中任務沒有計時器；底部「Current focus」只有標題，沒有已進行時間。
- 「Next fixed event」顯示 `fixedEvents[0]`，不是真正「下一個」（未按當前時間過濾排序）。

**方向：** 時間軸改為按比例的時段呈現（CSS grid rows = 分鐘數），空檔顯示為可點擊的「+ 安排任務」區；進行中任務顯示經過時間並於超過預估時變色。

### 3. 操作成本：每個動作都太重（🟡)

- 任何變更（勾完成、改狀態、移動 15 分鐘）都觸發 `loadDashboardData()` **全量重載**（8 個 API 請求），畫面閃爍、捲動位置丟失、慢。
- 移動排程項目只能每次 ±15 分鐘按按鈕，移 2 小時要按 8 次。
- 刪除用 `window.confirm`（本次補上防呆，MVP 可接受）；成熟做法是「先刪 + Undo toast」，成本更低也更安全。
- 有搜尋、有篩選，但沒有鍵盤快捷鍵~~（本次已加 Alt+←/→/T/G）~~，Command palette 是死按鈕。

**方向：** mutation 改 optimistic update 或至少限定範圍 refetch（只刷新 tasks + analytics）；排程項目支援拖曳；刪除改 Undo 模式。

### 4. 架構：2632 行單檔 App.tsx（🟡，工程面）

40+ 個 `useState` 在同一個元件，所有 fetch 內聯，任何小改動都要動同一個檔案。這不影響今天的用戶，但決定了上面所有改善的成本曲線。

**方向（漸進、不重寫）：**

```
src/
├── api/client.ts          # fetch 封裝 + auth header（已有雛形邏輯，抽出）
├── features/
│   ├── tasks/             # TaskList, TaskForm, useTasks()
│   ├── schedule/          # Timeline, HistoryPanel, useSchedule()
│   ├── events/            # FixedEventList + form
│   ├── analytics/         # OverviewStrip, InsightPanel
│   └── auth/              # AuthPanel, useAuth()
├── i18n.ts
└── App.tsx                # 佈局與組裝（目標 < 300 行）
```

每次抽一個 feature、跑一次 build + browser smoke，五步完成，不做大爆炸重寫。

### 5. 預測價值不可見（🟡，和 ML 產品價值直接相關）

任務列的「estimate 90m | predicted 118m | actual 0m」是三個灰字，用戶不會注意到模型在說「你低估了 31%」。

**方向：** predicted 與 estimate 偏差超過閾值時顯示帶方向的徽章（如 `▲ +28m`，tooltip 顯示信心值與理由），完成後顯示「預測誤差 vs 估時誤差」讓模型價值被看見。這是把 ml-service 從後台黑盒變成產品賣點的關鍵一步。

## 分階段路線圖

| 階段 | 項目 | 狀態 |
| --- | --- | --- |
| **P0（0.52.0 交付）** | 刪除確認防呆（任務/固定行程） | ✅ |
| | 誠實 model panel（真實模型名稱/版本、演算法數） | ✅ |
| | 「現在」時段高亮 + Now 標籤（每分鐘更新） | ✅ |
| | 鍵盤快捷鍵 Alt+←/→（換日）、Alt+T（今日）、Alt+G（生成） | ✅ |
| **P1（0.53.0 交付）** | 移除死按鈕；fallback 時間軸標示「未排程預覽」 | ✅ |
| | Plan score 改為真實排程涵蓋率（scheduled/selected） | ✅ |
| | 真正的「下一個固定行程」（依當前時間計算） | ✅ |
| | 側邊欄六視圖導覽（Today/Tasks/Schedule/Analytics/MLOps/Settings） | ✅ |
| | 編輯風設計系統（ink/warm/canvas tokens、display 字體、方角、髮絲線） | ✅ |
| | MLOps 視圖呈現 confidence 與 fallback 說明 | ✅ |
| **P1（未完，下一輪）** | 進行中任務經過時間計時器 | ⏳ |
| | 任務列預測偏差徽章（confidence 已在 MLOps 視圖呈現） | ⏳ |
| | mutation 範圍化 refetch（去掉全量重載） | ⏳ |
| | App.tsx 分模組（5 步漸進） | ⏳ |
| **P2（產品化階段）** | 按比例時間軸 + 空檔可視化 + 拖曳調整 | ⏳ |
| | 刪除改 Undo toast；Command palette 實作 | ⏳ |
| | 週視圖；多日規劃 | ⏳ |
| | 行動裝置佈局（目前 1433 行的 media query 只是縮排版） | ⏳ |
| | 新用戶 onboarding（空帳號第一次看到的引導流程） | ⏳ |

## 設計原則（給後續所有前端決策）

1. **誠實優先**：寧可顯示「—」也不顯示編造的數字。這個產品的核心承諾是「讓估時誠實」，介面必須以身作則。
2. **時間是一等公民**：任何畫面都應能在一秒內回答「現在幾點、我該做什麼、還剩多久」。
3. **操作可逆**：優先 Undo 而非 confirm；優先 optimistic 而非整頁重載。
4. **鍵盤可完成**：高頻操作（換日、生成、勾完成）都要有快捷鍵。
5. **漸進重構**：每次抽一個模組，永遠保持 build 綠燈與 smoke 通過。

## 驗證方式

- P0 項目：`npm run build` + Docker runtime + `python scripts/browser_smoke.py`，視覺基線重建後 `python scripts/visual_regression.py` 通過。
- P1 起：為抽出的模組補 component 測試（可引入 Vitest，與 Vite 同生態、零額外設定成本）。
