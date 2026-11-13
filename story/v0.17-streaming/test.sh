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

python reset_db.py
echo

echo "== 1. 還沒有任何事件就要串流 → 404（在開始串流之前就擋下來）"
show $URL/reports/handover/stream -H "$HANDLER"

echo "== 2. 送出 5 筆事件，處理其中兩筆告警（1 結案、2 誤報）"
while IFS= read -r line; do
  curl -s -o /dev/null -X POST $URL/events -H "$JSON" -H "$DEVICE" -d "$line"
done < $DATA
curl -s -o /dev/null -X POST $URL/alerts/1/ack -H "$HANDLER"
curl -s -o /dev/null -X POST $URL/alerts/1/resolve -H "$HANDLER"
curl -s -o /dev/null -X POST $URL/alerts/2/dismiss -H "$HANDLER"
echo "done"
echo

echo "== 3. 一般回應：整段一次出現"
curl -s "$URL/reports/handover?llm=true" -H "$HANDLER" | python -c "import json,sys; print(json.load(sys.stdin)['narrative'])"
echo

echo "== 4. 串流回應：每 0.5 秒出現一段"
curl -s -N $URL/reports/handover/stream -H "$HANDLER"
