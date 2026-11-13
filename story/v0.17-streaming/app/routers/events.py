import io

import pandas as pd
from fastapi import APIRouter, BackgroundTasks, Depends, UploadFile
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.auth import verify_device_key, verify_handler_key
from app.database import get_db
from app.errors import EventRejected
from app.schemas.event import DetectionEvent, EventOut
from app.services import alert_service, event_service, ingest_service

router = APIRouter()

REQUIRED_COLUMNS = {"event_type", "location", "source", "confidence", "occurred_at"}


def notify_later(background_tasks: BackgroundTasks, alert):
    background_tasks.add_task(
        alert_service.notify_handler, alert.id, alert.location, alert.event_type
    )


# 只有設備的 key 可以送事件
@router.post("/events", dependencies=[Depends(verify_device_key)])
def receive_event(
    event: DetectionEvent,
    background_tasks: BackgroundTasks,
    dry_run: bool = False,
    db: Session = Depends(get_db),
):
    if dry_run:
        event_service.check_event_type(event)
        return {"status": "checked"}

    result = ingest_service.ingest(db, event)
    if result["notify"]:
        notify_later(background_tasks, result["alert"])
    return {
        "status": "received",
        "event_id": result["event_id"],
        "decision": result["decision"],
        "alert_id": result["alert"].id if result["alert"] else None,
    }


# 設備斷線期間的事件，恢復之後整批補傳（CSV）
@router.post("/events/upload", dependencies=[Depends(verify_device_key)])
def upload_events(
    file: UploadFile,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    # 1. 只收 CSV
    if not file.filename.endswith(".csv"):
        raise EventRejected(reason="只接受 .csv 檔", code="FILE_TYPE_NOT_SUPPORTED")

    # 2. 讀進記憶體，交給 Pandas
    #    這個 function 要用資料庫，所以是 def；def 裡不能 await，改用 file.file.read()
    content = file.file.read()
    df = pd.read_csv(io.BytesIO(content))

    # 3. 欄位不齊、沒有資料就整份拒收
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise EventRejected(reason=f"缺少欄位：{sorted(missing)}", code="CSV_COLUMNS_MISSING")
    if df.empty:
        raise EventRejected(reason="檔案沒有資料", code="CSV_EMPTY")

    # 4. 一列一列過合約、走跟單筆事件一樣的流程；不合格的列記下來，不影響其他列
    imported = 0
    rejected = []
    for index, row in df.iterrows():
        row_number = index + 1
        try:
            event = DetectionEvent(
                event_type=row["event_type"],
                location=row["location"],
                source=row["source"],
                confidence=float(row["confidence"]),
                occurred_at=row["occurred_at"],
            )
            result = ingest_service.ingest(db, event)
        except ValidationError as exc:
            first = exc.errors()[0]
            rejected.append({"row": row_number, "reason": f"{first['loc'][0]}：{first['msg']}"})
            continue
        except EventRejected as exc:
            rejected.append({"row": row_number, "reason": exc.reason})
            continue

        imported += 1
        if result["notify"]:
            notify_later(background_tasks, result["alert"])

    return {
        "filename": file.filename,
        "rows": len(df),
        "imported": imported,
        "rejected": rejected,
    }


@router.get(
    "/events/{event_id}",
    response_model=EventOut,
    dependencies=[Depends(verify_handler_key)],
)
def get_event(event_id: int, db: Session = Depends(get_db)):
    return event_service.get_event(db, event_id)


@router.get(
    "/locations/{location}/events",
    response_model=list[EventOut],
    dependencies=[Depends(verify_handler_key)],
)
def list_location_events(
    location: str,
    event_type: str = None,
    limit: int = 10,
    db: Session = Depends(get_db),
):
    return event_service.list_location_events(db, location, event_type, limit)
