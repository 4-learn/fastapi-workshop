from fastapi import Body, FastAPI

app = FastAPI(title="Alert Platform v0.2")

events = []


@app.get("/health")
def health():
    return {"status": "ok", "version": "0.2"}


# Body：整筆事件；Query：dry_run=true 只檢查、不存
@app.post("/events")
def receive_event(event: dict = Body(), dry_run: bool = False):
    event_id = len(events) + 1
    if dry_run:
        return {"status": "checked", "would_be_id": event_id}
    events.append({"id": event_id, **event})
    return {"status": "received", "id": event_id}


# Path：哪一筆事件
@app.get("/events/{event_id}")
def get_event(event_id: int):
    for e in events:
        if e["id"] == event_id:
            return e
    return {"error": f"找不到事件：{event_id}"}


# Path：哪個位置；Query：篩選條件
@app.get("/locations/{location}/events")
def list_location_events(location: str, event_type: str = None, limit: int = 10):
    results = []
    for e in events:
        if e.get("location") != location:
            continue
        if event_type and e.get("event_type") != event_type:
            continue
        results.append(e)
    return results[:limit]
