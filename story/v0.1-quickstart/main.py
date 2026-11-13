from fastapi import Body, FastAPI

app = FastAPI(title="Alert Platform v0.1")

# 收到的事件先放在記憶體裡，server 重開就會清空
events = []


@app.get("/health")
def health():
    return {"status": "ok", "version": "0.1"}


@app.post("/events")
def receive_event(event: dict = Body()):
    events.append(event)
    return {"status": "received", "count": len(events), "event": event}
