from datetime import datetime

from pydantic import BaseModel, Field


class DetectionEvent(BaseModel):
    event_type: str = Field(min_length=1)
    location: str = Field(pattern=r"^[a-z]+_\d+$")
    source: str = Field(min_length=1)
    confidence: float = Field(strict=True, ge=0, le=1)
    occurred_at: datetime
    detail: dict = {}
