from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


# 進來的事件（設備送的）
class DetectionEvent(BaseModel):
    event_type: str = Field(min_length=1)
    location: str = Field(pattern=r"^[a-z]+_\d+$")
    source: str = Field(min_length=1)
    confidence: float = Field(strict=True, ge=0, le=1)
    occurred_at: datetime
    detail: dict = {}


# 出去的事件（從資料庫讀出來的）
class EventOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)  # 可以直接吃 ORM 物件

    id: int
    event_type: str
    location: str
    source: str
    confidence: float
    occurred_at: datetime
    detail: dict
