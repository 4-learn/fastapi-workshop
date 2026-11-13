#!/bin/bash
# 先在另一個終端機啟動 server（這一版不用選 PROFILE，一台 server 服務兩個客戶）：
#   uvicorn app.main:app --reload
# 再執行：bash test.sh

URL=http://localhost:8000
JSON="Content-Type: application/json"
FD="X-API-Key: dev-factory-device"
FH="X-API-Key: dev-factory-handler"
CD="X-API-Key: dev-care-device"
CH="X-API-Key: dev-care-handler"
show() { curl -s -w "\nHTTP %{http_code}\n\n" "$@"; }

python reset_db.py
echo

echo "== 1. 一台 server，兩個客戶"
show $URL/health

echo "== 2. 兩個客戶各送一筆事件：事件屬於誰，由 key 決定"
show -X POST $URL/events -H "$JSON" -H "$FD" -d "$(head -1 ../data/factory.jsonl)"
show -X POST $URL/events -H "$JSON" -H "$CD" -d "$(head -1 ../data/care.jsonl)"

echo "== 3. 工廠的設備送健康線的事件 → 400"
show -X POST $URL/events -H "$JSON" -H "$FD" -d "$(head -1 ../data/care.jsonl)"

echo "== 4. 各自只看得到自己的告警"
show $URL/alerts -H "$FH"
show $URL/alerts -H "$CH"

echo "== 5. 工廠的值班主管想處理健康線的告警（id 2）→ 404"
show -X POST $URL/alerts/2/ack -H "$FH"

echo "== 6. 健康線的值班護理師處理自己的告警 → 200"
show -X POST $URL/alerts/2/ack -H "$CH"

echo "== 7. 幫事件 1 補上影像"
show -F "file=@../data/sample.png" $URL/events/1/image -H "$FD"

echo "== 8. 不是影像檔 → 400"
show -F "file=@test.sh" $URL/events/1/image -H "$FD"

echo "== 9. 健康線的設備想幫工廠的事件補影像 → 404"
show -F "file=@../data/sample.png" $URL/events/1/image -H "$CD"

echo "== 10. 事件 1 現在有影像路徑"
show $URL/events/1 -H "$FH"

echo "== 11. 統計也是各看各的"
curl -s $URL/reports/summary -H "$CH" | python -c "import json,sys; d=json.load(sys.stdin); print(d['total_events'], d['by_event_type'], d['alerts_by_status'])"
