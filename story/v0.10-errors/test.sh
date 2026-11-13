#!/bin/bash
# 先在另一個終端機啟動 server（選你的那條線）：
#   PROFILE=factory uvicorn app.main:app --reload
#   PROFILE=care uvicorn app.main:app --reload
# 再執行：bash test.sh factory   或   bash test.sh care

TRACK=${1:-factory}
URL=http://localhost:8000
JSON="Content-Type: application/json"
DATA=../data/$TRACK.jsonl
show() { curl -s -w "\nHTTP %{http_code}\n\n" "$@"; }

python reset_db.py
echo

echo "== 1. 送出前 3 筆事件：每筆自動開一筆告警"
head -3 $DATA | while IFS= read -r line; do
  curl -s -X POST $URL/events -H "$JSON" -d "$line"
  echo
done
echo

echo "== 2. 不支援的事件類型 → 400"
show -X POST $URL/events -H "$JSON" \
  -d '{"event_type": "coffee_spilled", "location": "aisle_01", "source": "camera_01", "confidence": 0.9, "occurred_at": "2026-03-02T09:00:00"}'

echo "== 2b. 格式不對（confidence 超過 1）→ 422"
show -X POST $URL/events -H "$JSON" \
  -d "$(head -1 $DATA | sed -E 's/"confidence": [0-9.]+/"confidence": 1.7/')"

echo "== 3. 告警 1：open → ack → resolve"
show -X POST $URL/alerts/1/ack
show -X POST $URL/alerts/1/resolve

echo "== 4. 告警 1 已經結案，再 ack 一次 → 409"
show -X POST $URL/alerts/1/ack

echo "== 5. 告警 2：還沒 ack 就 resolve → 409"
show -X POST $URL/alerts/2/resolve

echo "== 6. 告警 2：dismiss（誤報）"
show -X POST $URL/alerts/2/dismiss

echo "== 7. 告警 99 不存在 → 404"
show -X POST $URL/alerts/99/ack

echo "== 8. 還沒處理的告警：GET /alerts?status=open"
show "$URL/alerts?status=open"

