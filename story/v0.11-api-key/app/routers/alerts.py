from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth import verify_handler_key
from app.database import get_db
from app.schemas.alert import AlertOut
from app.services import alert_service

# 這個 router 底下所有 endpoint 都要值班人員的 key
router = APIRouter(prefix="/alerts", dependencies=[Depends(verify_handler_key)])


@router.get("", response_model=list[AlertOut])
def list_alerts(status: str = None, db: Session = Depends(get_db)):
    return alert_service.list_alerts(db, status)


@router.get("/{alert_id}", response_model=AlertOut)
def get_alert(alert_id: int, db: Session = Depends(get_db)):
    return alert_service.find_alert(db, alert_id)


@router.post("/{alert_id}/{action}", response_model=AlertOut)
def change_alert_status(alert_id: int, action: str, db: Session = Depends(get_db)):
    return alert_service.change_status(db, alert_id, action)
