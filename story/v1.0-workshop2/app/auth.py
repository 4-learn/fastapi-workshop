import os

from fastapi import Header

from app.errors import AuthError

# 兩種角色，兩把 key。正式環境一定要用環境變數設定，不要把真的 key 寫進程式碼
DEVICE_API_KEY = os.getenv("DEVICE_API_KEY", "dev-device")      # 設備：只能送事件
HANDLER_API_KEY = os.getenv("HANDLER_API_KEY", "dev-handler")   # 值班人員：查詢、處理告警

KEY_ROLES = {DEVICE_API_KEY: "device", HANDLER_API_KEY: "handler"}


def check_role(x_api_key: str | None, role: str):
    if x_api_key is None:
        raise AuthError(401, "缺少 API Key", "API_KEY_MISSING")
    if x_api_key not in KEY_ROLES:
        raise AuthError(403, "API Key 錯誤", "API_KEY_INVALID")
    if KEY_ROLES[x_api_key] != role:
        raise AuthError(403, "這把 API Key 不能做這件事", "ROLE_NOT_ALLOWED")


def verify_device_key(x_api_key: str | None = Header(default=None)):
    check_role(x_api_key, "device")


def verify_handler_key(x_api_key: str | None = Header(default=None)):
    check_role(x_api_key, "handler")
