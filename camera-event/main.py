from fastapi import FastAPI, Body
import json

app = FastAPI(title="Camera Event Search")

DATA_FILE = "camera_events.json"


@app.post("/camera-events/search")
def search_camera_events(payload: dict = Body(...)):
    # 1. 讀檔
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        events = json.load(f)

    camera_id = payload.get("camera_id")
    event_type = payload.get("event_type")

    # 2. 篩選事件
    results = []
    for event in events:
        if camera_id and event["camera_id"] != camera_id:
            continue
        if event_type and event["event_type"] != event_type:
            continue
        results.append(event)

    # 3. 回傳結果
    return {
        "query": payload,
        "results": results
    }

