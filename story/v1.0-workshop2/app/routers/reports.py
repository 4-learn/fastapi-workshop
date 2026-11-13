import asyncio

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.auth import verify_handler_key
from app.config import PROFILE
from app.database import get_db
from app.errors import NotFound
from app.services import report_service

router = APIRouter(prefix="/reports", dependencies=[Depends(verify_handler_key)])


@router.get("/summary")
def summary(db: Session = Depends(get_db)):
    return report_service.build_summary(db)


# 交班摘要：?llm=true 才請 LLM 寫成一段話
@router.get("/handover")
def handover(llm: bool = False, db: Session = Depends(get_db)):
    return report_service.build_handover(db, PROFILE["handler_role"], use_llm=llm)


# 串流版：LLM 生一段就送一段（SSE 格式：data: 內容 + 空行）
@router.get("/handover/stream")
def handover_stream(db: Session = Depends(get_db)):
    # 串流一開始，狀態碼 200 就送出去了，所以要在開始之前先檢查
    summary = report_service.build_summary(db)
    if summary["total_events"] == 0:
        raise NotFound(reason="還沒有任何事件，沒有東西可以摘要", code="NO_EVENTS")

    chunks = report_service.fake_llm_chunks(summary)

    async def generate():
        for chunk in chunks:
            await asyncio.sleep(0.5)  # 模擬 LLM 慢慢生成
            yield f"data: {chunk}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")
