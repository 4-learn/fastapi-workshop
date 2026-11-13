from fastapi import HTTPException

from app.config import EVENT_TYPES
from app.schemas.event import DetectionEvent

events = []


def check_event_type(event: DetectionEvent):
    if event.event_type not in EVENT_TYPES:
        raise HTTPException(status_code=400, detail=f"不支援的事件類型：{event.event_type}")


def save_event(event: DetectionEvent) -> dict:
    stored = {"id": len(events) + 1, **event.model_dump()}
    events.append(stored)
    return stored


def get_event(event_id: int) -> dict:
    for e in events:
        if e["id"] == event_id:
            return e
    raise HTTPException(status_code=404, detail=f"找不到事件：{event_id}")


def list_location_events(location: str, event_type: str = None, limit: int = 10) -> list:
    results = []
    for e in events:
        if e["location"] != location:
            continue
        if event_type and e["event_type"] != event_type:
            continue
        results.append(e)
    return results[:limit]
