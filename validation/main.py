from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import Optional

app = FastAPI()

class TransactionEvent(BaseModel):
    user_id: int
    amount: float = Field(gt=0)
    currency: str = Field(min_length=3, max_length=3)
    note: Optional[str] = None

@app.post("/transaction")
def create_transaction(event: TransactionEvent):
    return {
        "status": "accepted",
        "event": event
    }
