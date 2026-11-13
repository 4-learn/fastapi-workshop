from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth import verify_handler_key
from app.database import get_db
from app.services import report_service

router = APIRouter(prefix="/reports", dependencies=[Depends(verify_handler_key)])


@router.get("/summary")
def summary(db: Session = Depends(get_db)):
    return report_service.build_summary(db)
