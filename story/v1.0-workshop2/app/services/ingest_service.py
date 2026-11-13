from sqlalchemy.orm import Session

from app.schemas.event import DetectionEvent
from app.services import alert_service, event_service, guardrail


def ingest(db: Session, event: DetectionEvent) -> dict:
    """
    一筆事件進來要做的事：檢查類型 → 存事件 → 依信心值決定要不要開告警。

    單筆（POST /events）和整批上傳（POST /events/upload）都走這裡，規則只寫一次。
    回傳的 notify 是「要不要通知值班的人」，由 router 丟到背景去做。
    """
    event_service.check_event_type(event)
    row = event_service.save_event(db, event)  # 不管信心值多少，事件都留紀錄
    decision = guardrail.decide(event.confidence)

    if decision == "log_only":
        return {"event_id": row.id, "decision": decision, "alert": None, "notify": False}

    if decision == "require_review":
        alert = alert_service.open_alert(db, row, status="pending_review")
        return {"event_id": row.id, "decision": decision, "alert": alert, "notify": False}

    alert = alert_service.open_alert(db, row)
    return {"event_id": row.id, "decision": decision, "alert": alert, "notify": True}
