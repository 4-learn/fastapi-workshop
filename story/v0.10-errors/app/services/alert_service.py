import asyncio

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import PROFILE
from app.errors import InvalidTransition, NotFound
from app.models import Alert, Event

# 告警狀態機：目前狀態 → {動作: 下一個狀態}
TRANSITIONS = {
    "open": {"ack": "acknowledged", "dismiss": "dismissed"},
    "acknowledged": {"resolve": "resolved", "dismiss": "dismissed"},
    "resolved": {},
    "dismissed": {},
}


async def notify_handler(alert_id: int, location: str, event_type: str):
    """通知值班的人。傳訊息很慢，這裡用等 2 秒來模擬。"""
    await asyncio.sleep(2)
    print(f"[通知 {PROFILE['handler_role']}] 告警 {alert_id}：{location} 發生 {event_type}")


def open_alert(db: Session, event: Event) -> Alert:
    alert = Alert(
        event_id=event.id,
        event_type=event.event_type,
        location=event.location,
        status="open",
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert


def list_alerts(db: Session, status: str = None) -> list:
    stmt = select(Alert).order_by(Alert.id)
    if status:
        stmt = stmt.where(Alert.status == status)
    return db.scalars(stmt).all()


def find_alert(db: Session, alert_id: int) -> Alert:
    alert = db.get(Alert, alert_id)
    if alert is None:
        raise NotFound(reason=f"找不到告警：{alert_id}", code="ALERT_NOT_FOUND")
    return alert


def change_status(db: Session, alert_id: int, action: str) -> Alert:
    alert = find_alert(db, alert_id)
    allowed = TRANSITIONS[alert.status]
    if action not in allowed:
        raise InvalidTransition(reason=f"狀態是 {alert.status} 的告警不能 {action}")
    alert.status = allowed[action]  # 改屬性，commit 的時候會寫回資料庫
    db.commit()
    db.refresh(alert)
    return alert
