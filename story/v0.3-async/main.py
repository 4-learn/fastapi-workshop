import asyncio

from fastapi import Body, FastAPI

app = FastAPI(title="Alert Platform v0.3")

events = []


async def notify_handler(event: dict):
    """通知值班的人。傳訊息很慢，這裡用等 2 秒來模擬。"""
    await asyncio.sleep(2)  # 用 await，等待時讓出 event loop
    print(f"[通知] {event.get('location')} 發生 {event.get('event_type')}")


@app.get("/health")
async def health():
    return {"status": "ok", "version": "0.3"}


@app.post("/events")
async def receive_event(event: dict = Body(), dry_run: bool = False):
    event_id = len(events) + 1
    if dry_run:
        return {"status": "checked", "would_be_id": event_id}
    stored = {"id": event_id, **event}
    events.append(stored)
    await notify_handler(stored)
    return {"status": "received", "id": event_id, "notified": True}


@app.get("/events/{event_id}")
async def get_event(event_id: int):
    for e in events:
        if e["id"] == event_id:
            return e
    return {"error": f"找不到事件：{event_id}"}


@app.get("/locations/{location}/events")
async def list_location_events(location: str, event_type: str = None, limit: int = 10):
    results = []
    for e in events:
        if e.get("location") != location:
            continue
        if event_type and e.get("event_type") != event_type:
            continue
        results.append(e)
    return results[:limit]
