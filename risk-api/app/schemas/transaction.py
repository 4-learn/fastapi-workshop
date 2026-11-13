from datetime import datetime

from pydantic import BaseModel, Field


class TransactionRequest(BaseModel):
    user_id: int = Field(gt=0)
    amount: float = Field(gt=0)
    currency: str = Field(min_length=3, max_length=3)
    timestamp: datetime


class Decision(BaseModel):
    risk_score: float
    action: str
    reason: str


class DecisionEvent(BaseModel):
    event_type: str = "risk_decision"
    user_id: int
    tx_type: str
    risk_score: float
    action: str
    timestamp: datetime


class EvaluateResponse(BaseModel):
    decision: Decision
    event: DecisionEvent
