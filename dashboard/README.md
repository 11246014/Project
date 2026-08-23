# WearWise 後台數據儀表板

負責人：前端1
用途：將匿名化的使用者偏好資料整理成統計圖表，提供給品牌商 / 代理商參考。

## 執行方式

```bash
pip install -r requirements.txt
streamlit run app.py
```

執行後會開啟瀏覽器，網址預設為 `http://localhost:8501`。

## 這一版的架構

目前畫面資料來自 `mock_data.py` 的 `MOCK_EVENTS`——**一筆一筆的原始事件**
（模擬 `recommendation_events` 資料表的每一列），不是已經算好的統計總和。

所有的圖表、KPI 數字、洞察摘要，都是 `app.py` 用 pandas 對這份原始資料
**即時計算**出來的。這樣設計的好處：

- 側邊欄的「事件來源」「日期範圍」篩選才能真正生效（選了會重新計算，不是套用寫死的數字）
- **建議跟後端1討論**：不用讓後端1自己寫 GROUP BY 統計邏輯，
  只要開一支「回傳原始事件列表」的 API 即可，例如：

  ```
  GET /analytics/events
  → 回傳去識別化後的 recommendation_events 全部（或近期）資料列
  ```

  統計、篩選的邏輯都放在這支 Streamlit 程式裡處理，後端1的工作量會小很多，
  也不用每次前端想加一種新篩選條件，就要麻煩後端1改一次 API 邏輯。

## 之後串接後端1的真實 API 時

打開 `app.py`，找到「資料來源」區塊：

```python
events_df = pd.DataFrame(MOCK_EVENTS)
```

改成：

```python
import requests

API_BASE = "https://your-ngrok-url.ngrok-free.app"  # 後端1的 ngrok 網址
events_df = pd.DataFrame(requests.get(f"{API_BASE}/analytics/events").json())
```

其餘統計、篩選、圖表程式碼完全不用改，因為欄位名稱已經對齊
（`created_at`、`source`、`usage`、`features`、`device_type`、`budget_bucket`、
`os`、`age_range`、`usage_scope`、`top_brand`、`top_platform`）。

## 檔案說明

- `app.py`：主程式，畫面與統計邏輯都在這裡
- `mock_data.py`：假資料產生器，用固定亂數種子（seed=42）產生 180 筆模擬事件，
  每次執行結果一致，方便展示與除錯；串接真實 API 後可以刪除或保留作為離線展示備用
- `.streamlit/config.toml`：深色主題設定，配色對齊 Flutter App
- `requirements.txt`：Python 套件需求
