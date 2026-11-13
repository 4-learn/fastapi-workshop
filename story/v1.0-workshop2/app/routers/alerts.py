from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.orm import Session

from app.auth import verify_handler_key
from app.database import get_db
from app.errors import InvalidTransition
from app.schemas.alert import AlertHistoryOut, AlertOut, EscalateRequest
from app.services import alert_service

# 這個 router 底下所有 endpoint 都要值班人員的 key
router = APIRouter(prefix="/alerts", dependencies=[Depends(verify_handler_key)])


@router.get("", response_model=list[AlertOut])
def list_alerts(status: str = None, db: Session = Depends(get_db)):
    return alert_service.list_alerts(db, status)


@router.get("/{alert_id}", response_model=AlertOut)
def get_alert(alert_id: int, db: Session = Depends(get_db)):
    return alert_service.find_alert(db, alert_id)


@router.get("/{alert_id}/history", response_model=list[AlertHistoryOut])
def get_alert_history(alert_id: int, db: Session = Depends(get_db)):
    return alert_service.list_history(db, alert_id)


# 排程器每分鐘打一次：把放太久的告警升級
@router.post("/escalate-overdue")
def escalate_overdue(body: EscalateRequest, db: Session = Depends(get_db)):
    return alert_service.escalate_overdue(db, body.now)


@router.post("/{alert_id}/{action}", response_model=AlertOut)
def change_alert_status(
    alert_id: int,
    action: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    if action in alert_service.SYSTEM_ACTIONS:
        raise InvalidTransition(reason=f"{action} 只能由系統執行", code="SYSTEM_ACTION_ONLY")

    alert = alert_service.change_status(db, alert_id, action)
    if action == "confirm":  # 人確認是真的，這時候才通知
        background_tasks.add_task(
            alert_service.notify_handler, alert.id, alert.location, alert.event_type
        )
    return alert
