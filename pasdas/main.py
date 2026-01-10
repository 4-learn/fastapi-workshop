from fastapi import FastAPI
from services.event_summary import get_user_risk_summary

app = FastAPI(title="Event Summary API")


@app.get("/users/{user_id}/summary")
def user_summary(user_id: int):
    """
    使用者狀態查詢 API
    """
    return get_user_risk_summary(user_id)
