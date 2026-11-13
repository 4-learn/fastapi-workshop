# 防呆：模型（設備）負責算信心值，系統負責決定要不要吵醒值班的人
# 門檻值集中管理，不散落在 if/else 裡
THRESHOLDS = {
    "auto": 0.8,     # 以上：直接開告警、通知
    "review": 0.5,   # 以上：先開一筆「待確認」，人看過再決定
}


def decide(confidence: float) -> str:
    if confidence >= THRESHOLDS["auto"]:
        return "auto_alert"
    if confidence >= THRESHOLDS["review"]:
        return "require_review"
    return "log_only"  # 信心太低：只留紀錄，不開告警
