from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.orm import Session

from app.auth import verify_device_key, verify_handler_key
from app.database import get_db
from app.schemas.event import DetectionEvent, EventOut
from app.services import alert_service, event_service

router = APIRouter()


# 合法的事件會自動開一筆告警
# 只有設備的 key 可以送事件
# 資料庫的操作是同步的，所以這裡用 def；通知丟到背景，設備不用等
@router.post("/events", dependencies=[Depends(verify_device_key)])
def receive_event(
    event: DetectionEvent,
    background_tasks: BackgroundTasks,
    dry_run: bool = False,
    db: Session = Depends(get_db),
):
    event_service.check_event_type(event)
    if dry_run:
        return {"status": "checked"}

    row = event_service.save_event(db, event)
    alert = alert_service.open_alert(db, row)
    background_tasks.add_task(
        alert_service.notify_handler, alert.id, alert.location, alert.event_type
    )
    return {"status": "received", "event_id": row.id, "alert_id": alert.id}


@router.get(
    "/events/{event_id}",
    response_model=EventOut,
    dependencies=[Depends(verify_handler_key)],
)
def get_event(event_id: int, db: Session = Depends(get_db)):
    return event_service.get_event(db, event_id)


@router.get(
    "/locations/{location}/events",
    response_model=list[EventOut],
    dependencies=[Depends(verify_handler_key)],
)
def list_location_events(
    location: str,
    event_type: str = None,
    limit: int = 10,
    db: Session = Depends(get_db),
):
    return event_service.list_location_events(db, location, event_type, limit)
