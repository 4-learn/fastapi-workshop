#!/bin/bash
# 先在另一個終端機啟動 server（選你的那條線）：
#   PROFILE=factory uvicorn app.main:app --reload
#   PROFILE=care uvicorn app.main:app --reload
# 再執行：bash test.sh factory   或   bash test.sh care

TRACK=${1:-factory}
URL=http://localhost:8000
DEVICE="X-API-Key: dev-device"
HANDLER="X-API-Key: dev-handler"
CSV=../data/${TRACK}_backfill.csv
show() { curl -s -w "\nHTTP %{http_code}\n\n" "$@"; }

python reset_db.py
echo

echo "== 1. 補傳 4 列：2 列合格、2 列不合格"
show -F "file=@$CSV" $URL/events/upload -H "$DEVICE"

echo "== 2. 合格的 2 列跟單筆事件走一樣的流程：一筆 open、一筆 pending_review"
show $URL/alerts -H "$HANDLER"

echo "== 3. 少一個欄位的檔案 → 400"
cut -d, -f1-4 $CSV > /tmp/no_time.csv
show -F "file=@/tmp/no_time.csv" $URL/events/upload -H "$DEVICE"

echo "== 4. 只有標題列的檔案 → 400"
head -1 $CSV > /tmp/empty.csv
show -F "file=@/tmp/empty.csv" $URL/events/upload -H "$DEVICE"

echo "== 5. 不是 CSV → 400"
show -F "file=@test.sh" $URL/events/upload -H "$DEVICE"

echo "== 6. 值班人員的 key 不能上傳 → 403"
show -F "file=@$CSV" $URL/events/upload -H "$HANDLER"
