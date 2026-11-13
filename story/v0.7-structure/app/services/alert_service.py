import asyncio

from fastapi import HTTPException

from app.config import PROFILE

# 告警狀態機：目前狀態 → {動作: 下一個狀態}
TRANSITIONS = {
    "open": {"ack": "acknowledged", "dismiss": "dismissed"},
    "acknowledged": {"resolve": "resolved", "dismiss": "dismissed"},
    "resolved": {},
    "dismissed": {},
}

alerts = []


async def notify_handler(alert: dict):
    """通知值班的人。傳訊息很慢，這裡用等 2 秒來模擬。"""
    await asyncio.sleep(2)
    print(f"[通知 {PROFILE['handler_role']}] 告警 {alert['id']}：{alert['location']} 發生 {alert['event_type']}")


def open_alert(event: dict) -> dict:
    alert = {
        "id": len(alerts) + 1,
        "event_id": event["id"],
        "event_type": event["event_type"],
        "location": event["location"],
        "status": "open",
    }
    alerts.append(alert)
    return alert


def list_alerts(status: str = None) -> list:
    if status:
        return [a for a in alerts if a["status"] == status]
    return alerts


def find_alert(alert_id: int) -> dict:
    for alert in alerts:
        if alert["id"] == alert_id:
            return alert
    raise HTTPException(status_code=404, detail=f"找不到告警：{alert_id}")


def change_status(alert_id: int, action: str) -> dict:
    alert = find_alert(alert_id)
    allowed = TRANSITIONS[alert["status"]]
    if action not in allowed:
        raise HTTPException(
            status_code=409,
            detail=f"狀態是 {alert['status']} 的告警不能 {action}",
        )
    alert["status"] = allowed[action]
    return alert
