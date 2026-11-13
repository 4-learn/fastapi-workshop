import pandas as pd
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Alert, Event


def build_summary(db: Session) -> dict:
    """
    把資料庫裡累積的事件和告警整理成統計。

    Pandas 在這裡的角色：整理歷史，不是即時判斷。
    """
    events = db.scalars(select(Event)).all()
    alerts = db.scalars(select(Alert)).all()

    if not events:
        return {
            "total_events": 0,
            "by_event_type": {},
            "by_location": {},
            "total_alerts": 0,
            "alerts_by_status": {},
            "note": "no events yet",
        }

    # ORM 物件 → DataFrame：一筆事件一列，只拿統計要用的欄位
    df = pd.DataFrame([
        {"event_type": e.event_type, "location": e.location, "confidence": e.confidence}
        for e in events
    ])

    grouped = df.groupby("event_type").agg(
        count=("confidence", "count"),
        avg_confidence=("confidence", "mean"),
    )
    by_event_type = {
        event_type: {
            "count": int(row["count"]),
            "avg_confidence": round(float(row["avg_confidence"]), 2),
        }
        for event_type, row in grouped.iterrows()
    }

    by_location = {k: int(v) for k, v in df["location"].value_counts().sort_index().items()}

    alerts_by_status = {}
    if alerts:
        alert_df = pd.DataFrame([{"status": a.status} for a in alerts])
        alerts_by_status = {
            k: int(v) for k, v in alert_df["status"].value_counts().sort_index().items()
        }

    return {
        "total_events": len(df),
        "by_event_type": by_event_type,
        "by_location": by_location,
        "total_alerts": len(alerts),
        "alerts_by_status": alerts_by_status,
    }
