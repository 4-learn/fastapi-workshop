"""
API 自動測試

執行：PROFILE=factory pytest -v   或   PROFILE=care pytest -v
測試用的資料庫是 events_test，不會動到平常用的 events。
"""
import json
import os
from pathlib import Path

os.environ["NOTIFY_SECONDS"] = "0"  # 要在 import app 之前設定：測試不用真的等通知

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.config import PROFILE_NAME
from app.database import Base, get_db
from app.main import app

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+psycopg://postgres:postgres@localhost:5432/events_test",
)
test_engine = create_engine(TEST_DATABASE_URL)


# 把 get_db 換成「連到測試資料庫」的版本
def get_test_db():
    with Session(test_engine) as session:
        yield session


app.dependency_overrides[get_db] = get_test_db


# 每個測試開始前：清空資料表，從乾淨的狀態開始
@pytest.fixture
def client():
    Base.metadata.drop_all(test_engine)
    Base.metadata.create_all(test_engine)
    with TestClient(app) as c:
        yield c


# 這條線的 5 筆事件：信心值依序是 高、高、中、高、低
DATA_PATH = Path(__file__).parent.parent / "data" / f"{PROFILE_NAME}.jsonl"
EVENTS = [json.loads(line) for line in DATA_PATH.read_text(encoding="utf-8").splitlines()]
HIGH, MEDIUM, LOW = EVENTS[0], EVENTS[2], EVENTS[4]

DEVICE = {"X-API-Key": "dev-device"}
HANDLER = {"X-API-Key": "dev-handler"}


# --------------------------------------------------
# 入口
# --------------------------------------------------
def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["customer"] == PROFILE_NAME


def test_event_without_key(client):
    r = client.post("/events", json=HIGH)
    assert r.status_code == 401
    assert r.json()["code"] == "API_KEY_MISSING"


def test_unknown_event_type(client):
    r = client.post("/events", json={**HIGH, "event_type": "coffee_spilled"}, headers=DEVICE)
    assert r.status_code == 400
    assert r.json()["code"] == "EVENT_TYPE_NOT_SUPPORTED"


# --------------------------------------------------
# 防呆：信心值決定要不要開告警
# --------------------------------------------------
def test_high_confidence_opens_alert(client):
    r = client.post("/events", json=HIGH, headers=DEVICE)
    assert r.json() == {"status": "received", "event_id": 1, "decision": "auto_alert", "alert_id": 1}
    assert client.get("/alerts/1", headers=HANDLER).json()["status"] == "open"


def test_medium_confidence_needs_review(client):
    r = client.post("/events", json=MEDIUM, headers=DEVICE)
    assert r.json()["decision"] == "require_review"
    assert client.get("/alerts/1", headers=HANDLER).json()["status"] == "pending_review"


def test_low_confidence_is_log_only(client):
    r = client.post("/events", json=LOW, headers=DEVICE)
    assert r.json()["alert_id"] is None
    assert client.get("/alerts", headers=HANDLER).json() == []
    assert client.get("/events/1", headers=HANDLER).status_code == 200  # 事件還是有留紀錄


# --------------------------------------------------
# 狀態機
# --------------------------------------------------
def test_ack_then_resolve(client):
    client.post("/events", json=HIGH, headers=DEVICE)
    assert client.post("/alerts/1/ack", headers=HANDLER).json()["status"] == "acknowledged"
    assert client.post("/alerts/1/resolve", headers=HANDLER).json()["status"] == "resolved"


def test_resolve_before_ack(client):
    client.post("/events", json=HIGH, headers=DEVICE)
    r = client.post("/alerts/1/resolve", headers=HANDLER)
    assert r.status_code == 409
    assert r.json()["code"] == "INVALID_TRANSITION"


def test_confirm_pending_review(client):
    client.post("/events", json=MEDIUM, headers=DEVICE)
    assert client.post("/alerts/1/ack", headers=HANDLER).status_code == 409  # 還沒確認不能接手
    assert client.post("/alerts/1/confirm", headers=HANDLER).json()["status"] == "open"
    assert client.post("/alerts/1/ack", headers=HANDLER).json()["status"] == "acknowledged"


def test_missing_alert(client):
    r = client.post("/alerts/99/ack", headers=HANDLER)
    assert r.status_code == 404
    assert r.json()["code"] == "ALERT_NOT_FOUND"


# --------------------------------------------------
# 升級與流水帳
# --------------------------------------------------
LATER = "2026-03-03T00:00:00"  # 比所有事件都晚很多


def test_escalate_overdue(client):
    client.post("/events", json=HIGH, headers=DEVICE)
    r = client.post("/alerts/escalate-overdue", json={"now": LATER}, headers=HANDLER)
    assert r.json()["escalated"] == [1]
    assert client.get("/alerts/1", headers=HANDLER).json()["status"] == "escalated"


def test_not_overdue_yet(client):
    client.post("/events", json=HIGH, headers=DEVICE)
    r = client.post("/alerts/escalate-overdue", json={"now": HIGH["occurred_at"]}, headers=HANDLER)
    assert r.json()["escalated"] == []


def test_handler_cannot_escalate(client):
    client.post("/events", json=HIGH, headers=DEVICE)
    r = client.post("/alerts/1/escalate", headers=HANDLER)
    assert r.status_code == 409
    assert r.json()["code"] == "SYSTEM_ACTION_ONLY"


def test_history(client):
    client.post("/events", json=HIGH, headers=DEVICE)
    client.post("/alerts/1/ack", headers=HANDLER)
    history = client.get("/alerts/1/history", headers=HANDLER).json()
    assert [h["action"] for h in history] == ["create", "ack"]
    assert [h["to_status"] for h in history] == ["open", "acknowledged"]
