from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.routers import transactions
from app.routers.transactions import UnsupportedTxType

app = FastAPI(title="Transaction Risk API")
app.include_router(transactions.router)


@app.exception_handler(UnsupportedTxType)
async def handle_unsupported_tx_type(request: Request, exc: UnsupportedTxType):
    return JSONResponse(
        status_code=400,
        content={
            "status": "rejected",
            "event_type": exc.tx_type,
            "reason": f"Unsupported transaction type: {exc.tx_type}",
        },
    )
