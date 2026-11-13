#!/bin/bash
# 先在另一個終端機啟動 server：uvicorn main:app --reload
# 再執行：bash test.sh factory   或   bash test.sh care

TRACK=${1:-factory}
URL=http://localhost:8000
JSON="Content-Type: application/json"
DATA=../data/$TRACK.jsonl

echo "== 1. GET /health"
curl -s $URL/health
echo; echo

echo "== 2. 送出 $TRACK 的前兩筆事件"
head -2 $DATA | while IFS= read -r line; do
  curl -s -X POST $URL/events -H "$JSON" -d "$line"
  echo
done
