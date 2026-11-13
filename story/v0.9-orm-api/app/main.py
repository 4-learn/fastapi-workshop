from contextlib import asynccontextmanager

from fastapi import FastAPI

from app import models  # noqa: F401  讓 Base 認得所有資料表
from app.config import PROFILE
from app.database import Base, engine
from app.routers import alerts, events


# 啟動時建表（表已存在就跳過）
@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(engine)
    yield


app = FastAPI(title="Alert Platform v0.9", lifespan=lifespan)

app.include_router(events.router)
app.include_router(alerts.router)


@app.get("/health")
def health():
    return {"status": "ok", "version": "0.9", "customer": PROFILE["customer"]}
