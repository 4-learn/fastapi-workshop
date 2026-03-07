# Workshop 解答 – Validation 與防呆邏輯

## 情境

你正在維護一個交易系統，Schema 已定義完成，但系統仍不斷收到金額為 0、金額為負、幣別亂填的事件。你必須在不修改 Business Logic 的情況下，讓系統具備防呆能力。

---

## 任務 1：加入數值防呆

### 問題

修改 `TransactionEvent`，讓 `amount` 必須大於 0。

### 解答

```python
from pydantic import BaseModel, Field

class TransactionEvent(BaseModel):
    user_id: int
    amount: float = Field(gt=0)
    currency: str
```

### 說明

- `Field(gt=0)` 表示 greater than 0
- `0` 或負數會在進入 function 前被拒絕
- 不需要在 Business Logic 裡寫 `if amount < 0`

---

## 任務 2：測試錯誤事件（結構正確但不合理）

### 測試指令

```bash
curl -X POST http://127.0.0.1:8000/transaction \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1001,
    "amount": -10,
    "currency": "USD"
  }'
```

### 預期輸出

HTTP 422：

```json
{
  "detail": [
    {
      "loc": ["body", "amount"],
      "msg": "ensure this value is greater than 0",
      "type": "value_error.number.not_gt"
    }
  ]
}
```

### 重點

- 結構完全正確（int、float、str 都對）
- 但邏輯不合理（金額為負）
- function 根本沒有被執行

> **金句：結構正確 ≠ 事件合理。**

---

## 任務 3：加入 Optional 欄位

### 問題

加入 `note` 欄位，可以不傳。

### 解答

```python
from typing import Optional

class TransactionEvent(BaseModel):
    user_id: int
    amount: float = Field(gt=0)
    currency: str = Field(min_length=3, max_length=3)
    note: Optional[str] = None
```

### 說明

- `Optional[str] = None` 表示可以不傳，預設為 `None`
- 不影響事件是否成立
- `currency` 加上 `min_length=3, max_length=3` 擋掉亂填的幣別代碼

---

## 任務 4：測試合法事件（含 Optional）

### 測試指令

```bash
curl -X POST http://127.0.0.1:8000/transaction \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1001,
    "amount": 100,
    "currency": "USD",
    "note": "first transaction"
  }'
```

### 預期輸出

```json
{
  "status": "accepted",
  "event": {
    "user_id": 1001,
    "amount": 100,
    "currency": "USD",
    "note": "first transaction"
  }
}
```

---

## 完整解答程式碼

```python
from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import Optional

app = FastAPI()

class TransactionEvent(BaseModel):
    user_id: int
    amount: float = Field(gt=0)
    currency: str = Field(min_length=3, max_length=3)
    note: Optional[str] = None

@app.post("/transaction")
def create_transaction(event: TransactionEvent):
    return {
        "status": "accepted",
        "event": event
    }
```

---

## 啟動方式

```bash
pip install fastapi uvicorn

uvicorn main:app --reload
```

測試 API：`POST /transaction`
