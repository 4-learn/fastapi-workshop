from fastapi import APIRouter

from app.schemas.transaction import DecisionEvent, EvaluateResponse, TransactionRequest
from app.services.history_service import get_user_history
from app.services.risk_service import calculate_risk, decide

router = APIRouter(prefix="/transactions")

SUPPORTED_TX_TYPES = {"purchase", "refund", "transfer"}


class UnsupportedTxType(Exception):
    def __init__(self, tx_type: str):
        self.tx_type = tx_type


@router.post("/{tx_type}/evaluate", response_model=EvaluateResponse)
def evaluate_transaction(tx_type: str, tx: TransactionRequest):
    if tx_type not in SUPPORTED_TX_TYPES:
        raise UnsupportedTxType(tx_type)

    history = get_user_history(tx.user_id)      # 階段 3：Pandas 歷史分析
    risk_score = calculate_risk(tx.amount, history)  # 階段 4：風險評分
    decision = decide(risk_score)                # 階段 5：決策防呆

    event = DecisionEvent(
        user_id=tx.user_id,
        tx_type=tx_type,
        risk_score=decision.risk_score,
        action=decision.action,
        timestamp=tx.timestamp,
    )
    return EvaluateResponse(decision=decision, event=event)
