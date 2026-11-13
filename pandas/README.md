# Workshop 解答 – 設計一個「事件查詢 API」

## 情境

你正在維護一個 AI 風險系統。系統每天會收到大量 transaction events，並已經全部記錄在 `events.csv` 中。

使用者透過 API 問你：

> 「我最近的交易狀況如何？」

---

## 題目一：判斷是否需要查歷史

### 問題

1. 這是一個即時事件嗎？
2. 是否需要查 DB / Event Store？
3. 是否適合用 Pandas？

### 解答

| 問題                          | 解答      |
| ----------------------------- | --------- |
| 這是即時事件嗎？              | ❌ 不是   |
| 是否需要查 DB / Event Store？ | ✅ 需要   |
| 是否適合用 Pandas？           | ✅ 適合   |

### 說明

使用者問的是「一段時間的狀態」，不是「現在發生什麼事」，所以一定要查歷史事件。

> **金句：使用者問的是「狀態」，不是事件。**

---

## 題目二：設計 Service Function

### 問題

設計一個 service function：

```python
def get_user_risk_summary(user_id: int):
    ...
```

需求：
- 從 `events.csv` 讀取資料
- 篩選指定 user，而且只算交易（`event_type == "transaction"`）
- 回傳：交易次數、總金額、平均 confidence（取到小數第二位）

### 解答

```python
import pandas as pd
from pathlib import Path

DATA_PATH = Path(__file__).parent.parent / "data" / "events.csv"


def get_user_risk_summary(user_id: int) -> dict:
    """
    從事件資料中整理使用者的歷史行為摘要
    """

    # 1. 從 Event Store 讀取資料
    df = pd.read_csv(DATA_PATH)

    # 2. 篩選指定使用者的交易事件（login 不算交易）
    user_df = df[(df["user_id"] == user_id) & (df["event_type"] == "transaction")]

    # 3. 若沒有歷史資料，回傳安全結構
    if user_df.empty:
        return {
            "user_id": user_id,
            "total_events": 0,
            "total_amount": 0,
            "avg_confidence": None,
            "note": "no historical events"
        }

    # 4. 使用 Pandas 整理摘要
    return {
        "user_id": user_id,
        "total_events": int(len(user_df)),
        "total_amount": float(user_df["amount"].sum()),
        "avg_confidence": round(float(user_df["confidence"].mean()), 2)
    }
```

### 預期輸出

```json
{
  "user_id": 123,
  "total_events": 3,
  "total_amount": 2500.0,
  "avg_confidence": 0.79
}
```

### 重點說明

- Pandas **只處理歷史**
- DataFrame **只存在於 service 內部**
- 回傳的是「摘要結果」，不是 DataFrame
- CSV 在這裡代表 **Event Store / DB**

> **金句：Service 可以用 Pandas，但回傳給 API 的只能是「結論」。**

---

## 題目三：思考題

### Q1：為什麼這段邏輯不該寫在 FastAPI router？

**解答：**

- Router 是 request / response 邊界
- 不該承擔資料分析責任
- 否則會造成：
  - handler 過肥
  - 責任混亂
  - 難以測試

> **金句：Router 是櫃檯，不是研究室。**

---

### Q2：如果 event 只有一筆，還需要 Pandas 嗎？

**解答：**

- ❌ 不需要
- 單一事件沒有趨勢、沒有比較
- Pandas 的價值來自「多筆」

> **金句：沒有歷史，就沒有 DataFrame 的價值。**

---

### Q3：哪些情況不該讓使用者直接查 event？

**解答：**

- 涉及隱私或敏感資料
- raw event 難以理解
- 容易被誤解
- 不利於系統演進（schema 會變）

正確做法：

> **金句：使用者只能看到「系統整理過的觀點」。**

---

## 總結

1. 使用者問的是「狀態」，不是事件
2. Event 先進 DB，不會直接變 DataFrame
3. Pandas 是歷史整理工具
4. Service 才能用 Pandas
5. API 只負責把結果送出去

> **終極金句：FastAPI 不記得事情，系統才記得。**

---

## 啟動方式

```bash
# 建立虛擬環境
python3 -m venv venv
source venv/bin/activate

# 安裝套件
pip install pandas fastapi uvicorn

# 啟動 API
uvicorn main:app --reload
```

測試 API：`GET /users/123/summary`
