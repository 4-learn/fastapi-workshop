import json
import os
from pathlib import Path

# 設定檔：這個客戶有哪些事件類型
# 啟動時用環境變數選客戶：PROFILE=care uvicorn app.main:app --reload
PROFILE_NAME = os.getenv("PROFILE", "factory")
PROFILE_PATH = Path(__file__).parent.parent.parent / "profiles" / f"{PROFILE_NAME}.json"
PROFILE = json.loads(PROFILE_PATH.read_text(encoding="utf-8"))
EVENT_TYPES = PROFILE["event_types"]
