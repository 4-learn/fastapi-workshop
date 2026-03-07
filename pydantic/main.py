from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Pydantic Schema Workshop")


# 任務 1：建立事件 Schema
class TransactionEvent(BaseModel):
    user_id: int
    amount: float
    currency: str


# 任務 2：將 Schema 套用到 Endpoint
@app.post("/transaction")
def transaction(event: TransactionEvent):
    return {
        "status": "accepted",
        "event": event
    }
