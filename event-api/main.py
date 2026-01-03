from fastapi import FastAPI, Query
from pydantic import BaseModel, Field
from typing import Any, Dict
from datetime import datetime

# --------------------------------------------------
# 建立 FastAPI 應用（系統邊界）
# --------------------------------------------------
app = FastAPI(
    title="Event API Workshop",
    description="Comprehensive Event-Oriented API Demo",
    version="1.0.0"
)

# --------------------------------------------------
# Schema：事件合約（Event Contract）
# --------------------------------------------------
class EventPayload(BaseModel):
    user_id: int = Field(gt=0, description="事件發生的使用者 ID，必須為正整數")
    timestamp: datetime = Field(description="事件發生時間（ISO 8601）")
    payload: Dict[str, Any] = Field(description="事件實際內容（自由結構）")


# --------------------------------------------------
# Event API：事件入口
# --------------------------------------------------
@app.post("/events/{event_type}")
def receive_event(
    event_type: str,
    event: EventPayload,
    debug: bool = Query(default=False)
):
    """
    事件型 API
    - event_type：事件身份（Path）
    - event：事件內容（Body，需通過 Schema + Validation）
    - debug：觀察條件（Query，不影響事件成立）
    """

    # 在這裡我們不做任何 business logic
    # 只示範「事件被系統正式接收」

    response = {
        "status": "accepted",
        "event_type": event_type,
        "user_id": event.user_id,
        "timestamp": event.timestamp.isoformat()
    }

    # debug 模式下，回傳完整事件內容
    if debug:
        response["payload"] = event.payload

    return response
