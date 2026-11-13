#!/bin/bash
# 先在另一個終端機啟動 server：uvicorn main:app --reload
# 再執行：bash test.sh factory   或   bash test.sh care

TRACK=${1:-factory}
URL=http://localhost:8000
JSON="Content-Type: application/json"
DATA=../data/$TRACK.jsonl

FIRST=$(head -1 $DATA)
LOCATION=$(echo "$FIRST" | python3 -c "import json,sys; print(json.load(sys.stdin)['location'])")
TYPE=$(echo "$FIRST" | python3 -c "import json,sys; print(json.load(sys.stdin)['event_type'])")

echo "== 1. dry_run=true：只檢查，不存"
curl -s -X POST "$URL/events?dry_run=true" -H "$JSON" -d "$FIRST"
echo; echo

echo "== 2. 送出 $TRACK 的 5 筆事件"
while IFS= read -r line; do
  curl -s -X POST $URL/events -H "$JSON" -d "$line"
  echo
done < $DATA
echo

echo "== 3. GET /events/2"
curl -s $URL/events/2
echo; echo

echo "== 4. GET /events/99（不存在）"
curl -s $URL/events/99
echo; echo

echo "== 5. GET /locations/$LOCATION/events"
curl -s $URL/locations/$LOCATION/events
echo; echo

echo "== 6. GET /locations/$LOCATION/events?event_type=$TYPE&limit=1"
curl -s "$URL/locations/$LOCATION/events?event_type=$TYPE&limit=1"
echo
