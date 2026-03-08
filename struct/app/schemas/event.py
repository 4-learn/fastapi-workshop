from pydantic import BaseModel, Field
from typing import Dict, Any
from datetime import datetime

class EventPayload(BaseModel):
    user_id: int = Field(gt=0)
    timestamp: datetime
    payload: Dict[str, Any]
