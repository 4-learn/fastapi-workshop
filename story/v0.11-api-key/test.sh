#!/bin/bash
# 先在另一個終端機啟動 server（選你的那條線）：
#   PROFILE=factory uvicorn app.main:app --reload
#   PROFILE=care uvicorn app.main:app --reload
# 再執行：bash test.sh factory   或   bash test.sh care

TRACK=${1:-factory}
URL=http://localhost:8000
JSON="Content-Type: application/json"
DEVICE="X-API-Key: dev-device"
HANDLER="X-API-Key: dev-handler"
DATA=../data/$TRACK.jsonl
FIRST=$(head -1 $DATA)
show() { curl -s -w "\nHTTP %{http_code}\n\n" "$@"; }

python reset_db.py
echo

echo "== 1. /health 不用 key"
show $URL/health

echo "== 2. 送事件沒帶 key → 401"
show -X POST $URL/events -H "$JSON" -d "$FIRST"

echo "== 3. 送事件帶錯的 key → 403"
show -X POST $URL/events -H "$JSON" -H "X-API-Key: guess" -d "$FIRST"

echo "== 4. 設備的 key 送事件 → 200"
show -X POST $URL/events -H "$JSON" -H "$DEVICE" -d "$FIRST"

echo "== 5. 設備的 key 想處理告警 → 403"
show -X POST $URL/alerts/1/ack -H "$DEVICE"

echo "== 6. 值班人員的 key 想送事件 → 403"
show -X POST $URL/events -H "$JSON" -H "$HANDLER" -d "$FIRST"

echo "== 7. 值班人員的 key 處理告警 → 200"
show -X POST $URL/alerts/1/ack -H "$HANDLER"

echo "== 8. 值班人員的 key 查告警 → 200"
show $URL/alerts -H "$HANDLER"
