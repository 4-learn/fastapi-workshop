# Workshop 解答 – Error Handling

## 情境

你接手一個事件 API，錯誤處理很粗糙：不支援的 event_type 回 500、格式每次不同、下游系統不知道怎麼判斷成功或失敗。

---

## 任務 1：建立自訂 Exception

```python
class EventRejected(Exception):
    """事件被系統拒絕（格式正確但邏輯不接受）"""
    def __init__(self, reason: str, event_type: str = "unknown", code: str = "EVENT_REJECTED"):
        self.reason = reason
        self.event_type = event_type
        self.code = code


class EventNotFound(Exception):
    """事件對象不存在"""
    def __init__(self, reason: str, code: str = "NOT_FOUND"):
        self.reason = reason
        self.code = code
```

在 endpoint 拋出時指定 `code`：

```python
raise EventRejected(
    reason=f"Unsupported event type: {event_type}",
    event_type=event_type,
    code="EVENT_TYPE_NOT_SUPPORTED"
)

raise EventNotFound(
    reason=f"User {event.user_id} not found",
    code="USER_NOT_FOUND"
)
```

---

## 任務 2：註冊 Exception Handler

```python
from fastapi.responses import JSONResponse

@app.exception_handler(EventRejected)
async def handle_event_rejected(request, exc):
    return JSONResponse(
        status_code=400,
        content={
            "status": "rejected",
            "event_type": exc.event_type,
            "reason": exc.reason,
            "code": exc.code
        }
    )


@app.exception_handler(EventNotFound)
async def handle_event_not_found(request, exc):
    return JSONResponse(
        status_code=404,
        content={
            "status": "rejected",
            "reason": exc.reason,
            "code": exc.code
        }
    )
```

---

## 任務 3：覆寫 422 Handler

```python
from fastapi.exceptions import RequestValidationError

@app.exception_handler(RequestValidationError)
async def handle_validation_error(request, exc):
    return JSONResponse(
        status_code=422,
        content={
            "status": "rejected",
            "reason": "Event does not match schema",
            "code": "SCHEMA_INVALID",
            "details": exc.errors()
        }
    )
```

---

## 任務 4：測試三種錯誤情境

### Schema 錯誤（422）

```bash
curl -X POST http://127.0.0.1:8000/events/click \
  -H "Content-Type: application/json" \
  -d '{"user_id": "abc"}'
```

```json
{
  "status": "rejected",
  "reason": "Event does not match schema",
  "code": "SCHEMA_INVALID",
  "details": [...]
}
```

### 邏輯錯誤（400）

```bash
curl -X POST http://127.0.0.1:8000/events/unknown_action \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "timestamp": "2025-01-10T10:00:00",
    "payload": {"action": "test"}
  }'
```

```json
{
  "status": "rejected",
  "event_type": "unknown_action",
  "reason": "Unsupported event type: unknown_action",
  "code": "EVENT_TYPE_NOT_SUPPORTED"
}
```

### 正常事件（200）

```bash
curl -X POST http://127.0.0.1:8000/events/click \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "timestamp": "2025-01-10T10:00:00",
    "payload": {"action": "test"}
  }'
```

```json
{
  "status": "accepted",
  "event_type": "click",
  "event": {
    "user_id": 1,
    "timestamp": "2025-01-10T10:00:00",
    "payload": {"action": "test"}
  }
}
```

---

## 啟動方式

```bash
pip install fastapi uvicorn

uvicorn main:app --reload
```
