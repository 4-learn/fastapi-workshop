from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app import models  # noqa: F401  讓 Base 認得所有資料表
from app.config import PROFILE
from app.database import Base, engine
from app.errors import AuthError, EventRejected, InvalidTransition, NotFound
from app.routers import alerts, events, reports


# 啟動時建表（表已存在就跳過）
@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(engine)
    yield


app = FastAPI(title="Alert Platform v1.0", lifespan=lifespan)



# --------------------------------------------------
# Exception Handlers：所有錯誤都回同一種格式
# --------------------------------------------------
def rejected(status_code: int, reason: str, code: str, **extra):
    return JSONResponse(
        status_code=status_code,
        content={"status": "rejected", "reason": reason, "code": code, **extra},
    )


@app.exception_handler(EventRejected)
async def handle_event_rejected(request, exc):
    return rejected(400, exc.reason, exc.code)


@app.exception_handler(NotFound)
async def handle_not_found(request, exc):
    return rejected(404, exc.reason, exc.code)


@app.exception_handler(InvalidTransition)
async def handle_invalid_transition(request, exc):
    return rejected(409, exc.reason, exc.code)


@app.exception_handler(AuthError)
async def handle_auth_error(request, exc):
    return rejected(exc.status_code, exc.reason, exc.code)


@app.exception_handler(RequestValidationError)
async def handle_validation_error(request, exc):
    details = [{"loc": e["loc"], "msg": e["msg"]} for e in exc.errors()]
    return rejected(422, "事件不符合格式", "SCHEMA_INVALID", details=details)


app.include_router(events.router)
app.include_router(alerts.router)
app.include_router(reports.router)


# 不需要 key：誰都可以確認服務還活著
@app.get("/health")
def health():
    return {"status": "ok", "version": "1.0", "customer": PROFILE["customer"]}
