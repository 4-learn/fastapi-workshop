import json
import os
from pathlib import Path

# 設定檔：這個客戶有哪些事件類型
# 啟動時用環境變數選客戶：PROFILE=care uvicorn app.main:app --reload
PROFILE_NAME = os.getenv("PROFILE", "factory")
PROFILE_PATH = Path(__file__).parent.parent.parent / "profiles" / f"{PROFILE_NAME}.json"
PROFILE = json.loads(PROFILE_PATH.read_text(encoding="utf-8"))
EVENT_TYPES = PROFILE["event_types"]

# 通知要等幾秒（模擬外部訊息服務）。測試的時候設成 0，才不用每個測試都等
NOTIFY_SECONDS = float(os.getenv("NOTIFY_SECONDS", "2"))

# 告警升級策略：預設看設定檔，也可以用環境變數臨時換一種
ESCALATION_STRATEGY = os.getenv("ESCALATION_STRATEGY", PROFILE["escalation_strategy"])
