from pathlib import Path

import pandas as pd

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "transactions.csv"


def get_user_history(user_id: int) -> dict:
    """用 Pandas 整理該使用者的歷史交易"""
    df = pd.read_csv(DATA_PATH)
    user_df = df[df["user_id"] == user_id]

    if user_df.empty:
        return {"tx_count": 0, "avg_amount": 0.0, "avg_risk_score": 0.0}

    return {
        "tx_count": int(len(user_df)),
        "avg_amount": round(float(user_df["amount"].mean()), 2),
        "avg_risk_score": round(float(user_df["risk_score"].mean()), 2),
    }
