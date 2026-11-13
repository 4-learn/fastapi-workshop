from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AlertOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    event_id: int
    event_type: str
    location: str
    status: str
    opened_at: datetime


class AlertHistoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    action: str
    from_status: str | None
    to_status: str
    at: datetime


class EscalateRequest(BaseModel):
    now: datetime  # 「現在幾點」由呼叫的人給：排程器會給真的時間，測試可以給固定的時間
