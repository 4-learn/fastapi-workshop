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


# --------------------------------------------------
# 交班摘要：Pandas 整理數字 → 組 prompt → LLM 寫成一段話
# --------------------------------------------------
UNRESOLVED = ["open", "pending_review", "escalated", "acknowledged"]  # 還沒結案的狀態


def build_handover_prompt(summary: dict, handler_role: str) -> str:
    """把統計數字組成要交給 LLM 的 prompt。只放統計，不放任何一筆事件的細節。"""
    types = "、".join(
        f"{name} {s['count']} 筆（平均信心值 {s['avg_confidence']}）"
        for name, s in summary["by_event_type"].items()
    )
    locations = "、".join(f"{name} {count} 筆" for name, count in summary["by_location"].items())
    statuses = "、".join(f"{name} {count} 筆" for name, count in summary["alerts_by_status"].items())
    return (
        f"你是{handler_role}的交班助理。請根據下面的統計寫一段交班摘要，三句話以內。\n"
        f"只能使用提供的數字，不要推測原因，不要加上沒有提供的資訊。\n"
        f"事件總數：{summary['total_events']}\n"
        f"事件類型：{types}\n"
        f"位置：{locations}\n"
        f"告警總數：{summary['total_alerts']}\n"
        f"告警狀態：{statuses}"
    )


def fake_llm_chunks(summary: dict) -> list[str]:
    """模擬 LLM 一次吐出一小段文字（正式環境換成真正的模型呼叫）"""
    statuses = summary["alerts_by_status"]
    unresolved = sum(statuses.get(s, 0) for s in UNRESOLVED)
    busiest = max(summary["by_location"], key=summary["by_location"].get)
    return [
        f"本班共收到 {summary['total_events']} 筆事件，",
        f"開了 {summary['total_alerts']} 筆告警，",
        f"其中 {unresolved} 筆還沒結案。",
        f"事件最多的位置是 {busiest}，",
        f"共 {summary['by_location'][busiest]} 筆。",
    ]


def fake_llm_summarize(summary: dict) -> str:
    """一般回應：全部生完才一次給"""
    return "".join(fake_llm_chunks(summary))


def build_handover(db: Session, handler_role: str, use_llm: bool = False) -> dict:
    summary = build_summary(db)

    prompt = None
    narrative = None
    if use_llm and summary["total_events"] > 0:
        prompt = build_handover_prompt(summary, handler_role)
        narrative = fake_llm_summarize(summary)

    return {"summary": summary, "prompt": prompt, "narrative": narrative}
