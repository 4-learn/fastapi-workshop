from fastapi import FastAPI

from app.config import PROFILE
from app.routers import alerts, events

app = FastAPI(title="Alert Platform v0.7")

app.include_router(events.router)
app.include_router(alerts.router)


@app.get("/health")
async def health():
    return {"status": "ok", "version": "0.7", "customer": PROFILE["customer"]}
