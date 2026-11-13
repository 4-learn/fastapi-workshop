from app.schemas.transaction import Decision

# 門檻集中管理：< 0.3 自動通過，0.3 ~ 0.7（含）人工審核，> 0.7 自動擋下
APPROVE_BELOW = 0.3
BLOCK_ABOVE = 0.7


def calculate_risk(amount: float, history: dict) -> float:
    """
    規則（模擬 AI）：
    - 基礎分 = amount / 10000（金額越大風險越高）
    - 如果歷史平均 risk_score > 0.5，加 0.2
    - 如果交易次數 < 3（新用戶），加 0.1
    - 上限 1.0
    """
    score = amount / 10000
    if history["avg_risk_score"] > 0.5:
        score += 0.2
    if history["tx_count"] < 3:
        score += 0.1
    return round(min(score, 1.0), 2)


def decide(risk_score: float) -> Decision:
    """決策防呆：把分數轉成系統行動"""
    if risk_score < APPROVE_BELOW:
        return Decision(risk_score=risk_score, action="auto_approve", reason="低風險，自動通過")
    if risk_score <= BLOCK_ABOVE:
        return Decision(risk_score=risk_score, action="require_review", reason="中風險，轉人工審核")
    return Decision(risk_score=risk_score, action="auto_block", reason="高風險，自動擋下")
