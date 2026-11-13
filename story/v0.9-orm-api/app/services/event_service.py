from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import EVENT_TYPES
from app.models import Event
from app.schemas.event import DetectionEvent


def check_event_type(event: DetectionEvent):
    if event.event_type not in EVENT_TYPES:
        raise HTTPException(status_code=400, detail=f"不支援的事件類型：{event.event_type}")


def save_event(db: Session, event: DetectionEvent) -> Event:
    row = Event(**event.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)  # 拿回資料庫產生的 id
    return row


def get_event(db: Session, event_id: int) -> Event:
    row = db.get(Event, event_id)
    if row is None:
        raise HTTPException(status_code=404, detail=f"找不到事件：{event_id}")
    return row


def list_location_events(db: Session, location: str, event_type: str = None, limit: int = 10) -> list:
    stmt = select(Event).where(Event.location == location).order_by(Event.id)
    if event_type:
        stmt = stmt.where(Event.event_type == event_type)
    return db.scalars(stmt.limit(limit)).all()
