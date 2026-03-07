# Workshop 解答 – Pydantic Schema（系統合約）

## 情境

你正在設計一個 AI 推論 API，必須確保只有符合合約的事件才能進入系統。

---

## 任務 1：建立事件 Schema

### 問題

定義一個 Schema，描述「交易事件」。

### 解答

```python
from pydantic import BaseModel

class TransactionEvent(BaseModel):
    user_id: int
    amount: float
    currency: str
```

### 說明

- `user_id: int` — 必須是整數，不接受字串
- `amount: float` — 必須是數字，不接受 `"free"` 這種值
- `currency: str` — 必須存在，不能省略

> **金句：Schema 不是文件，是系統的拒收標準。**

---

## 任務 2：將 Schema 套用到 Endpoint

### 解答

```python
from fastapi import FastAPI

app = FastAPI()

@app.post("/transaction")
def transaction(event: TransactionEvent):
    return {
        "status": "accepted",
        "event": event
    }
```

### 說明

- 把 `TransactionEvent` 當作參數型別，FastAPI 自動做三件事：
  1. 驗證欄位是否存在
  2. 驗證型別是否正確
  3. 不合法就直接回傳 422，function 根本不會執行

---

## 任務 3：測試合法事件

### 測試指令

```bash
curl -X POST http://127.0.0.1:8000/transaction \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1001,
    "amount": 250.5,
    "currency": "USD"
  }'
```

### 預期輸出

```json
{
  "status": "accepted",
  "event": {
    "user_id": 1001,
    "amount": 250.5,
    "currency": "USD"
  }
}
```

---

## 任務 4：測試不合法事件

### 測試指令

```bash
curl -X POST http://127.0.0.1:8000/transaction \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "abc",
    "amount": "free"
  }'
```

### 預期輸出

HTTP 422 Unprocessable Entity：

```json
{
  "detail": [
    {
      "loc": ["body", "user_id"],
      "msg": "value is not a valid integer",
      "type": "type_error.integer"
    },
    {
      "loc": ["body", "amount"],
      "msg": "value is not a valid float",
      "type": "type_error.float"
    }
  ]
}
```

### 重點

- 事件沒有進入系統
- `transaction()` 根本沒有被執行
- 錯誤在邊界就被擋下

> **金句：Schema 擋在門口，handler 才能專心做事。**

---

## 觀念整理

| 觀念 | 說明 |
| --- | --- |
| Schema = 合約 | 定義什麼資料系統願意承認 |
| 不合法 = 拒收 | 回傳 422，function 不執行 |
| Swagger 連動 | Schema 寫好，文件自動產生 |
| Fail Fast | 問題在邊界解決，不在系統深處爆炸 |

> **終極金句：系統不需要修正錯誤資料，只需要決定收不收。**

---

## 啟動方式

```bash
pip install fastapi uvicorn

uvicorn main:app --reload
```

測試 API：`POST /transaction`，或直接開 Swagger UI (`/docs`)
