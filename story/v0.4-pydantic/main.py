import asyncio
from datetime import datetime

from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI(title="Alert Platform v0.4")

events = []


# 事件的合約：設備廠商照這個格式送
class DetectionEvent(BaseModel):
    event_type: str
    location: str
    source: str
    confidence: float = Field(strict=True)  # 嚴格模式：字串 "0.91" 不收
    occurred_at: datetime
    detail: dict = {}


async def notify_handler(event: dict):
    """通知值班的人。傳訊息很慢，這裡用等 2 秒來模擬。"""
    await asyncio.sleep(2)
    print(f"[通知] {event['location']} 發生 {event['event_type']}")


@app.get("/health")
async def health():
    return {"status": "ok", "version": "0.4"}


@app.post("/events")
async def receive_event(event: DetectionEvent, dry_run: bool = False):
    event_id = len(events) + 1
    if dry_run:
        return {"status": "checked", "would_be_id": event_id}
    stored = {"id": event_id, **event.model_dump()}
    events.append(stored)
    await notify_handler(stored)
    return {"status": "received", "id": event_id, "notified": True}


@app.get("/events/{event_id}")
async def get_event(event_id: int):
    for e in events:
        if e["id"] == event_id:
            return e
    return {"error": f"找不到事件：{event_id}"}


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
