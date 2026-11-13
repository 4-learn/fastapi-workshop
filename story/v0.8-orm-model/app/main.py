from fastapi import FastAPI

from app.config import PROFILE
from app.routers import alerts, events

app = FastAPI(title="Alert Platform v0.8")

app.include_router(events.router)
app.include_router(alerts.router)


@app.get("/health")
async def health():
    return {"status": "ok", "version": "0.8", "customer": PROFILE["customer"]}
