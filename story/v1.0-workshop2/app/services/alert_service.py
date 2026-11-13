import asyncio
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import ESCALATION_STRATEGY, EVENT_TYPES, NOTIFY_SECONDS, PROFILE
from app.errors import InvalidTransition, NotFound
from app.models import Alert, AlertHistory, Event
from app.services.escalation import STRATEGIES

# 告警狀態機：目前狀態 → {動作: 下一個狀態}
TRANSITIONS = {
    "pending_review": {"confirm": "open", "dismiss": "dismissed"},
    "open": {"ack": "acknowledged", "dismiss": "dismissed", "escalate": "escalated"},
    "escalated": {"ack": "acknowledged", "dismiss": "dismissed"},
    "acknowledged": {"resolve": "resolved", "dismiss": "dismissed"},
    "resolved": {},
    "dismissed": {},
}

# 只有系統能做的動作，值班人員不能自己打 API 觸發
SYSTEM_ACTIONS = {"escalate"}


async def notify_handler(alert_id: int, location: str, event_type: str):
    """通知值班的人。傳訊息很慢，這裡用等幾秒來模擬。"""
    await asyncio.sleep(NOTIFY_SECONDS)
    print(f"[通知 {PROFILE['handler_role']}] 告警 {alert_id}：{location} 發生 {event_type}")


def open_alert(db: Session, event: Event, status: str = "open") -> Alert:
    alert = Alert(
        event_id=event.id,
        event_type=event.event_type,
        location=event.location,
        status=status,
        opened_at=event.occurred_at,
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)
    record_history(db, alert.id, "create", None, status, datetime.now())
    return alert


def record_history(db: Session, alert_id: int, action: str, from_status, to_status: str, at: datetime):
    db.add(AlertHistory(
        alert_id=alert_id,
        action=action,
        from_status=from_status,
        to_status=to_status,
        at=at,
    ))
    db.commit()


def list_history(db: Session, alert_id: int) -> list:
    find_alert(db, alert_id)  # 告警不存在就回 404
    stmt = select(AlertHistory).where(AlertHistory.alert_id == alert_id).order_by(AlertHistory.id)
    return db.scalars(stmt).all()


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


def change_status(db: Session, alert_id: int, action: str, at: datetime = None) -> Alert:
    alert = find_alert(db, alert_id)
    allowed = TRANSITIONS[alert.status]
    if action not in allowed:
        raise InvalidTransition(reason=f"狀態是 {alert.status} 的告警不能 {action}")

    from_status = alert.status
    alert.status = allowed[action]  # 改屬性，commit 的時候會寫回資料庫
    db.commit()
    db.refresh(alert)
    record_history(db, alert.id, action, from_status, alert.status, at or datetime.now())
    return alert


def escalate_overdue(db: Session, now: datetime) -> dict:
    """把放太久沒人接手的告警升級。「太久」怎麼算，交給設定檔選的策略決定。"""
    is_overdue = STRATEGIES[ESCALATION_STRATEGY]

    stmt = select(Alert).where(Alert.status == "open").order_by(Alert.id)
    open_alerts = db.scalars(stmt).all()

    escalated = []
    for alert in open_alerts:
        rule = EVENT_TYPES[alert.event_type]
        if is_overdue(alert, rule, now):
            change_status(db, alert.id, "escalate", at=now)  # 一樣走狀態機
            escalated.append(alert.id)

    return {"strategy": ESCALATION_STRATEGY, "checked": len(open_alerts), "escalated": escalated}
