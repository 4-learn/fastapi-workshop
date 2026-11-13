import pandas as pd
from pathlib import Path

DATA_PATH = Path(__file__).parent.parent / "data" / "events.csv"


def get_user_risk_summary(user_id: int) -> dict:
    """
    從事件資料中整理使用者的歷史行為摘要
    """

    # 1. 從 Event Store 讀取資料
    df = pd.read_csv(DATA_PATH)

    # 2. 篩選指定使用者的交易事件（login 不算交易）
    user_df = df[(df["user_id"] == user_id) & (df["event_type"] == "transaction")]

    # 3. 若沒有歷史資料，回傳安全結構
    if user_df.empty:
        return {
            "user_id": user_id,
            "total_events": 0,
            "total_amount": 0,
            "avg_confidence": None,
            "note": "no historical events"
        }

    # 4. 使用 Pandas 整理摘要
    return {
        "user_id": user_id,
        "total_events": int(len(user_df)),
        "total_amount": float(user_df["amount"].sum()),
        "avg_confidence": round(float(user_df["confidence"].mean()), 2)
    }
