from datetime import datetime, timedelta

# --------------------------------------------------
# 升級策略（Strategy pattern）
# 每個策略都是同樣的介面：給它告警、這種事件的規則、現在時間，回答「該不該升級」
# 要新增一種策略：寫一個 function，登記到 STRATEGIES，不用改其他程式
# --------------------------------------------------


def by_minutes(alert, rule: dict, now: datetime) -> bool:
    """放超過規定的分鐘數就升級"""
    limit = timedelta(minutes=rule["escalate_after_minutes"])
    return now - alert.opened_at > limit


def high_first(alert, rule: dict, now: datetime) -> bool:
    """嚴重程度是 high 的事件，只給一半的時間"""
    minutes = rule["escalate_after_minutes"]
    if rule["severity"] == "high":
        minutes = minutes / 2
    return now - alert.opened_at > timedelta(minutes=minutes)


STRATEGIES = {
    "by_minutes": by_minutes,
    "high_first": high_first,
}
