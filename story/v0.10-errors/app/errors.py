# 自訂 Exception：service 只說「發生什麼事」，回什麼 HTTP 狀態碼交給 main.py 的 handler 決定


class EventRejected(Exception):
    """事件格式正確，但系統不接受"""
    def __init__(self, reason: str, code: str = "EVENT_REJECTED"):
        self.reason = reason
        self.code = code


class NotFound(Exception):
    """要找的東西不存在"""
    def __init__(self, reason: str, code: str = "NOT_FOUND"):
        self.reason = reason
        self.code = code


class InvalidTransition(Exception):
    """告警目前的狀態不能做這個動作"""
    def __init__(self, reason: str, code: str = "INVALID_TRANSITION"):
        self.reason = reason
        self.code = code
