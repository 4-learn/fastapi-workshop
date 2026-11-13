import asyncio
import json
import os
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

# --------------------------------------------------
# 設定檔：這個客戶有哪些事件類型
# 啟動時用環境變數選客戶：PROFILE=care uvicorn main:app --reload
# --------------------------------------------------
PROFILE_NAME = os.getenv("PROFILE", "factory")
PROFILE_PATH = Path(__file__).parent.parent / "profiles" / f"{PROFILE_NAME}.json"
PROFILE = json.loads(PROFILE_PATH.read_text(encoding="utf-8"))
EVENT_TYPES = PROFILE["event_types"]

# --------------------------------------------------
# 告警狀態機：目前狀態 → {動作: 下一個狀態}
# --------------------------------------------------
TRANSITIONS = {
    "open": {"ack": "acknowledged", "dismiss": "dismissed"},
    "acknowledged": {"resolve": "resolved", "dismiss": "dismissed"},
    "resolved": {},
    "dismissed": {},
}

app = FastAPI(title="Alert Platform v0.6")

events = []
alerts = []


class DetectionEvent(BaseModel):
    event_type: str = Field(min_length=1)
    location: str = Field(pattern=r"^[a-z]+_\d+$")
    source: str = Field(min_length=1)
    confidence: float = Field(strict=True, ge=0, le=1)
    occurred_at: datetime
    detail: dict = {}


async def notify_handler(alert: dict):
    """通知值班的人。傳訊息很慢，這裡用等 2 秒來模擬。"""
    await asyncio.sleep(2)
    print(f"[通知 {PROFILE['handler_role']}] 告警 {alert['id']}：{alert['location']} 發生 {alert['event_type']}")


def find_alert(alert_id: int) -> dict:
    for alert in alerts:
        if alert["id"] == alert_id:
            return alert
    raise HTTPException(status_code=404, detail=f"找不到告警：{alert_id}")


@app.get("/health")
async def health():
    return {"status": "ok", "version": "0.6", "customer": PROFILE["customer"]}


# --------------------------------------------------
# 事件：合法的事件會自動開一筆告警
# --------------------------------------------------
@app.post("/events")
async def receive_event(event: DetectionEvent, dry_run: bool = False):
    if event.event_type not in EVENT_TYPES:
        raise HTTPException(status_code=400, detail=f"不支援的事件類型：{event.event_type}")

    event_id = len(events) + 1
    if dry_run:
        return {"status": "checked", "would_be_id": event_id}

    stored = {"id": event_id, **event.model_dump()}
    events.append(stored)

    alert = {
        "id": len(alerts) + 1,
        "event_id": event_id,
        "event_type": event.event_type,
        "location": event.location,
        "status": "open",
    }
    alerts.append(alert)

    await notify_handler(alert)
    return {"status": "received", "event_id": event_id, "alert_id": alert["id"]}


@app.get("/events/{event_id}")
async def get_event(event_id: int):
    for e in events:
        if e["id"] == event_id:
            return e
    raise HTTPException(status_code=404, detail=f"找不到事件：{event_id}")


@app.get("/locations/{location}/events")
async def list_location_events(location: str, event_type: str = None, limit: int = 10):
    results = []
    for e in events:
        if e["location"] != location:
            continue
        if event_type and e["event_type"] != event_type:
            continue
        results.append(e)
    return results[:limit]


# --------------------------------------------------
# 告警
# --------------------------------------------------
@app.get("/alerts")
async def list_alerts(status: str = None):
    if status:
        return [a for a in alerts if a["status"] == status]
    return alerts


@app.get("/alerts/{alert_id}")
async def get_alert(alert_id: int):
    return find_alert(alert_id)


@app.post("/alerts/{alert_id}/{action}")
async def change_alert_status(alert_id: int, action: str):
    alert = find_alert(alert_id)
    allowed = TRANSITIONS[alert["status"]]

    if action not in allowed:
        raise HTTPException(
            status_code=409,
            detail=f"狀態是 {alert['status']} 的告警不能 {action}",
        )

    alert["status"] = allowed[action]
    return alert
