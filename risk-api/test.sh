#!/bin/bash
# 先在另一個終端機啟動 server（在 risk-api 資料夾裡）：uvicorn app.main:app --reload
# 再執行：bash test.sh

URL=http://localhost:8000/transactions
JSON="Content-Type: application/json"

echo "== 1. 低風險（user 456, amount 200）→ auto_approve"
curl -s -w "\nHTTP %{http_code}\n\n" -X POST $URL/purchase/evaluate -H "$JSON" \
  -d '{"user_id": 456, "amount": 200, "currency": "TWD", "timestamp": "2025-01-10T14:00:00"}'

echo "== 2. 中風險（user 123, amount 5000）→ require_review"
curl -s -w "\nHTTP %{http_code}\n\n" -X POST $URL/purchase/evaluate -H "$JSON" \
  -d '{"user_id": 123, "amount": 5000, "currency": "TWD", "timestamp": "2025-01-10T14:00:00"}'

echo "== 3. 高風險（user 123, amount 50000）→ auto_block"
curl -s -w "\nHTTP %{http_code}\n\n" -X POST $URL/purchase/evaluate -H "$JSON" \
  -d '{"user_id": 123, "amount": 50000, "currency": "TWD", "timestamp": "2025-01-10T14:00:00"}'

echo "== 4. 不支援的交易類型 → 400"
curl -s -w "\nHTTP %{http_code}\n\n" -X POST $URL/withdrawal/evaluate -H "$JSON" \
  -d '{"user_id": 123, "amount": 100, "currency": "TWD", "timestamp": "2025-01-10T14:00:00"}'

echo "== 5. 格式錯誤（amount 是負數、currency 不是 3 碼）→ 422"
curl -s -w "\nHTTP %{http_code}\n\n" -X POST $URL/purchase/evaluate -H "$JSON" \
  -d '{"user_id": 123, "amount": -1, "currency": "TW", "timestamp": "2025-01-10T14:00:00"}'
