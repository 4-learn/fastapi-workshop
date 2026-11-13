from fastapi import APIRouter

from app.schemas.event import DetectionEvent
from app.services import alert_service, event_service

router = APIRouter()


# 合法的事件會自動開一筆告警
@router.post("/events")
async def receive_event(event: DetectionEvent, dry_run: bool = False):
    event_service.check_event_type(event)
    if dry_run:
        return {"status": "checked", "would_be_id": len(event_service.events) + 1}

    stored = event_service.save_event(event)
    alert = alert_service.open_alert(stored)
    await alert_service.notify_handler(alert)
    return {"status": "received", "event_id": stored["id"], "alert_id": alert["id"]}


@router.get("/events/{event_id}")
async def get_event(event_id: int):
    return event_service.get_event(event_id)


@router.get("/locations/{location}/events")
async def list_location_events(location: str, event_type: str = None, limit: int = 10):
    return event_service.list_location_events(location, event_type, limit)
