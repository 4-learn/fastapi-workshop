"""
AI Guardrail Workshop

任務：
1. 定義 Prediction 和 DecisionResponse schema
2. 實作 evaluate() — 根據 confidence 決定行動
3. 實作 to_event() — 把決策轉成事件
4. 用 /evaluate endpoint 測試三種情境
"""

from fastapi import FastAPI
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


# --------------------------------------------------
# TODO 1: 定義 AI 輸出結構
# --------------------------------------------------
class Prediction(BaseModel):
    label: str
    confidence: float = Field(ge=0.0, le=1.0)


# TODO: 定義 RiskLevel enum (HIGH, MEDIUM, LOW)


# TODO: 定義 Action enum (AUTO_BLOCK, REQUIRE_REVIEW, DEFER)


# TODO: 定義 DecisionResponse model
#   - prediction: str
#   - confidence: float
#   - risk_level: RiskLevel
#   - action: Action
#   - reason: str


# TODO: 定義 DecisionEvent model（把決策記成事件）
#   - event_type: str = "ai_decision"
#   - source_event_id: str
#   - prediction, confidence, risk_level, action
#   - timestamp: datetime


# --------------------------------------------------
# TODO 2: 實作 Guardrail Service
# --------------------------------------------------
THRESHOLDS = {
    "auto": 0.9,
    "review": 0.6,
}


def evaluate(prediction: Prediction):
    """
    根據 prediction.confidence 回傳 DecisionResponse

    規則：
    - >= 0.9 → AUTO_BLOCK, HIGH
    - >= 0.6 → REQUIRE_REVIEW, MEDIUM
    - < 0.6  → DEFER, LOW
    """
    # TODO: 實作
    pass


def to_event(source_event_id: str, decision) -> dict:
    """把 DecisionResponse 轉成 DecisionEvent"""
    # TODO: 實作
    pass


# --------------------------------------------------
# TODO 3: 完成 endpoint
# --------------------------------------------------
app = FastAPI(title="AI Guardrail Workshop")


class EventBody(BaseModel):
    event_id: str
    prediction: Prediction


@app.post("/evaluate")
def evaluate_prediction(body: EventBody):
    # TODO:
    # 1. 呼叫 evaluate() 取得決策
    # 2. 呼叫 to_event() 轉成事件
    # 3. 回傳 decision + event
    pass
