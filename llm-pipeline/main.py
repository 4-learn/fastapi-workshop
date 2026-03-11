"""
LLM Pipeline Workshop

你正在設計一個 AI 助手能使用的 API 系統。
AI 不能直接碰 DB，只能透過你設計的 API。

任務：實作三種 pipeline endpoint
1. 推論型：POST /risk/evaluate
2. 摘要型：GET /users/{user_id}/summary
3. 任務型：POST /tasks/review
"""

from fastapi import FastAPI
from pydantic import BaseModel, Field
from datetime import datetime
from pathlib import Path
from uuid import uuid4
import pandas as pd


DATA_PATH = Path(__file__).parent / "events.csv"


# --------------------------------------------------
# TODO 1: 定義 Schema
# --------------------------------------------------

# RiskRequest: user_id
# RiskResult: user_id, risk_level, confidence, action, features

# SummaryResult: user_id, total_events, total_amount, avg_confidence, narrative

# TaskRequest: user_id, reason
# TaskResult: task_id, status, created_at


# --------------------------------------------------
# 模擬 AI（不用改，直接用）
# --------------------------------------------------
def fake_ai_predict(features: dict) -> dict:
    avg_conf = features.get("avg_confidence", 0.5)
    total = features.get("total_amount", 0)
    if total > 2000 and avg_conf < 0.7:
        return {"label": "high_risk", "confidence": 0.85}
    elif total > 1000:
        return {"label": "medium_risk", "confidence": 0.65}
    else:
        return {"label": "low_risk", "confidence": 0.92}


def fake_llm_summarize(data: dict) -> str:
    return (
        f"使用者 {data['user_id']} 共有 {data['total_events']} 筆交易，"
        f"總金額 {data['total_amount']}，"
        f"平均信心值 {data['avg_confidence']}。"
    )


# --------------------------------------------------
# TODO 2: 實作 Service
# --------------------------------------------------
def prepare_features(user_id: int) -> dict:
    """從 events.csv 整理使用者特徵"""
    # TODO: 讀 CSV、篩選 user、回傳 dict
    pass


def evaluate_risk(user_id: int):
    """
    Pipeline 1: 推論

    流程：prepare_features → fake_ai_predict → 防呆判斷 → 回傳
    防呆規則：
    - confidence >= 0.8 → auto_flag
    - confidence >= 0.6 → require_review
    - 其他 → defer
    """
    # TODO: 實作
    pass


def summarize_user(user_id: int, use_llm: bool = False):
    """
    Pipeline 2: 摘要

    流程：prepare_features → (optional) fake_llm_summarize → 回傳
    """
    # TODO: 實作
    pass


def create_review_task(user_id: int, reason: str):
    """
    Pipeline 3: 任務觸發

    流程：建立 task_id (uuid4) → 回傳 pending 狀態
    """
    # TODO: 實作
    pass


# --------------------------------------------------
# TODO 3: 完成 Endpoints
# --------------------------------------------------
app = FastAPI(title="LLM Pipeline Workshop")


# Pipeline 1: POST /risk/evaluate
# TODO


# Pipeline 2: GET /users/{user_id}/summary?llm=false
# TODO


# Pipeline 3: POST /tasks/review
# TODO
