#!/bin/bash
# 先在另一個終端機啟動 server：uvicorn main:app --reload
# 再執行：bash test.sh factory   或   bash test.sh care

TRACK=${1:-factory}
URL=http://localhost:8000
JSON="Content-Type: application/json"
DATA=../data/$TRACK.jsonl

FIRST=$(head -1 $DATA)

echo "== 1. 送出一筆事件（通知要 2 秒），同時打 /health"
curl -s -X POST $URL/events -H "$JSON" -d "$FIRST" &
sleep 0.5
echo "/health 花了幾秒："
curl -s -o /dev/null -w "%{time_total}\n" $URL/health
wait
echo; echo

echo "== 2. 送出事件本身花了幾秒"
curl -s -o /dev/null -w "%{time_total}\n" -X POST $URL/events -H "$JSON" -d "$FIRST"
