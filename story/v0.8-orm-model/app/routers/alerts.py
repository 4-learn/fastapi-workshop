from fastapi import APIRouter

from app.services import alert_service

router = APIRouter(prefix="/alerts")


@router.get("")
async def list_alerts(status: str = None):
    return alert_service.list_alerts(status)


@router.get("/{alert_id}")
async def get_alert(alert_id: int):
    return alert_service.find_alert(alert_id)


@router.post("/{alert_id}/{action}")
async def change_alert_status(alert_id: int, action: str):
    return alert_service.change_status(alert_id, action)
