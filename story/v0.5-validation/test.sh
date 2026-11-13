#!/bin/bash
# 先在另一個終端機啟動 server：uvicorn main:app --reload
# 再執行：bash test.sh factory   或   bash test.sh care

TRACK=${1:-factory}
URL=http://localhost:8000
JSON="Content-Type: application/json"
DATA=../data/$TRACK.jsonl

FIRST=$(head -1 $DATA)
post() { curl -s -w "\nHTTP %{http_code}\n\n" -X POST "$URL/events?dry_run=true" -H "$JSON" -d "$1"; }

echo "== 1. 合法事件 → 200"
post "$FIRST"

echo "== 2. confidence = 1.7 → 422"
post "$(echo "$FIRST" | sed -E 's/"confidence": [0-9.]+/"confidence": 1.7/')"

echo "== 3. confidence = -0.2 → 422"
post "$(echo "$FIRST" | sed -E 's/"confidence": [0-9.]+/"confidence": -0.2/')"

echo "== 4. location 格式不對（Lobby）→ 422"
post "$(echo "$FIRST" | sed -E 's/"location": "[^"]+"/"location": "Lobby"/')"

echo "== 5. source 是空字串 → 422"
post "$(echo "$FIRST" | sed -E 's/"source": "[^"]+"/"source": ""/')"
