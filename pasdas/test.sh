#!/bin/bash

cd "$(dirname "$0")"
source venv/bin/activate

echo "=== 測試 Service Function ==="
echo

echo "User 123:"
python3 -c "from services.event_summary import get_user_risk_summary; import json; print(json.dumps(get_user_risk_summary(123), indent=2))"
echo

echo "User 456:"
python3 -c "from services.event_summary import get_user_risk_summary; import json; print(json.dumps(get_user_risk_summary(456), indent=2))"
echo

echo "User 999 (不存在):"
python3 -c "from services.event_summary import get_user_risk_summary; import json; print(json.dumps(get_user_risk_summary(999), indent=2))"
echo

echo "=== 測試完成 ==="
