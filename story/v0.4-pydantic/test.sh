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

echo "== 2. 欄位名稱拼錯（loction）→ 422"
post "$(echo "$FIRST" | sed 's/"location"/"loction"/')"

echo "== 3. confidence 是文字 \"high\" → 422"
post "$(echo "$FIRST" | sed -E 's/"confidence": [0-9.]+/"confidence": "high"/')"

echo "== 4. confidence 是加了引號的數字（嚴格模式）→ 422"
post "$(echo "$FIRST" | sed -E 's/"confidence": ([0-9.]+)/"confidence": "\1"/')"

echo "== 5. 少了 detail（有預設值）→ 200"
post "$(echo "$FIRST" | sed -E 's/, "detail": \{[^}]*\}//')"
