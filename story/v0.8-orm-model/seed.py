"""
v0.8：先確認資料表模型是對的（API 下一版才接上資料庫）

執行：PROFILE=factory python seed.py   或   PROFILE=care python seed.py
"""
import json
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import PROFILE, PROFILE_NAME
from app.database import Base, engine
from app.models import Alert, Event
from app.schemas.event import DetectionEvent

DATA_PATH = Path(__file__).parent.parent / "data" / f"{PROFILE_NAME}.jsonl"

# 教學用：每次執行都先刪掉再重建，輸出才會一樣
Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)
print("1. 建立資料表 detection_events、alerts")
print("---")

# 把這條線的 5 筆事件存進去，每筆事件開一筆告警
with Session(engine) as session:
    rows = []
    for line in DATA_PATH.read_text(encoding="utf-8").splitlines():
        event = DetectionEvent(**json.loads(line))  # 先過合約，再進資料庫
        row = Event(**event.model_dump())
        session.add(row)
        rows.append(row)
    session.commit()  # commit 之後，每個 row 才有資料庫產生的 id

    for row in rows:
        session.add(Alert(
            event_id=row.id,
            event_type=row.event_type,
            location=row.location,
            status="open",
        ))
    session.commit()
print("2. 新增 5 筆事件、5 筆告警")
print("---")

# 查詢：第一個位置的事件，照發生時間排
location = PROFILE["locations"][0]
with Session(engine) as session:
    stmt = select(Event).where(Event.location == location).order_by(Event.occurred_at)
    events = session.scalars(stmt).all()
    stmt = select(Alert).where(Alert.location == location).order_by(Alert.id)
    alerts = session.scalars(stmt).all()

print(f"3. {location} 的事件：")
for e in events:
    print(e.id, e.event_type, e.confidence, e.occurred_at, e.detail)
print("---")
print(f"4. {location} 的告警：")
for a in alerts:
    print(a.id, a.event_id, a.event_type, a.status)

engine.dispose()  # 用完把連線關掉
