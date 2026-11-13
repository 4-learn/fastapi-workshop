from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.alert import AlertOut
from app.services import alert_service

router = APIRouter(prefix="/alerts")


@router.get("", response_model=list[AlertOut])
def list_alerts(status: str = None, db: Session = Depends(get_db)):
    return alert_service.list_alerts(db, status)


@router.get("/{alert_id}", response_model=AlertOut)
def get_alert(alert_id: int, db: Session = Depends(get_db)):
    return alert_service.find_alert(db, alert_id)


@router.post("/{alert_id}/{action}", response_model=AlertOut)
def change_alert_status(alert_id: int, action: str, db: Session = Depends(get_db)):
    return alert_service.change_status(db, alert_id, action)
