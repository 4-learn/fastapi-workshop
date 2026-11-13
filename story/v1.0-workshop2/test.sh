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
show() { curl -s -w "\nHTTP %{http_code}\n\n" "$@"; }

# 每條線挑兩筆事件：先發生的那筆放很久了，後發生的那筆嚴重程度是 high、才剛發生
if [ "$TRACK" = "care" ]; then
  LINES="2p;4p"; NOW="2026-03-02T05:21:30"
else
  LINES="1p;2p"; NOW="2026-03-02T09:27:00"
fi

python reset_db.py
echo

echo "== 1. 送出兩筆事件，開兩筆告警"
sed -n "$LINES" $DATA | while IFS= read -r line; do
  curl -s -X POST $URL/events -H "$JSON" -H "$DEVICE" -d "$line"
  echo
done
echo

echo "== 2. 兩筆告警都還沒有人接手"
curl -s $URL/alerts -H "$HANDLER" | python -c "
import json, sys
for a in json.load(sys.stdin):
    print(a['id'], a['event_type'], a['status'], a['opened_at'])"
echo

echo "== 3. 值班人員不能自己升級 → 409"
show -X POST $URL/alerts/1/escalate -H "$HANDLER"

echo "== 4. 現在是 $NOW：把放太久的告警升級"
show -X POST $URL/alerts/escalate-overdue -H "$JSON" -H "$HANDLER" -d "{\"now\": \"$NOW\"}"

echo "== 5. 再打一次：已經升級的不會重複升級"
show -X POST $URL/alerts/escalate-overdue -H "$JSON" -H "$HANDLER" -d "{\"now\": \"$NOW\"}"

echo "== 6. 升級的告警一樣可以接手、結案"
show -X POST $URL/alerts/1/ack -H "$HANDLER"
show -X POST $URL/alerts/1/resolve -H "$HANDLER"

echo "== 7. 告警 1 的完整經過（時間省略）"
curl -s $URL/alerts/1/history -H "$HANDLER" | python -c "
import json, sys
for h in json.load(sys.stdin):
    print(h['action'], ':', h['from_status'], '->', h['to_status'])"
