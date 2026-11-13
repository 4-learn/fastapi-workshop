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

echo "== 1. 送出 5 筆事件：信心值決定要不要開告警"
while IFS= read -r line; do
  curl -s -X POST $URL/events -H "$JSON" -H "$DEVICE" -d "$line"
  echo
done < $DATA
echo

echo "== 2. 待確認的告警：GET /alerts?status=pending_review"
show "$URL/alerts?status=pending_review" -H "$HANDLER"

echo "== 3. 待確認的告警不能直接 ack → 409"
show -X POST $URL/alerts/3/ack -H "$HANDLER"

echo "== 4. 人看過是真的：confirm → open（這時候才通知）"
show -X POST $URL/alerts/3/confirm -H "$HANDLER"

echo "== 5. 已經是 open 了，不能再 confirm → 409"
show -X POST $URL/alerts/3/confirm -H "$HANDLER"

echo "== 6. 信心值太低的第 5 筆：事件有留紀錄"
show $URL/events/5 -H "$HANDLER"

echo "== 7. 全部的告警（只有 4 筆，第 5 筆事件沒有開）"
show $URL/alerts -H "$HANDLER"
