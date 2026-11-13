from datetime import datetime

from sqlalchemy import JSON, DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


# 資料表模型：一個 class = 一張表
class Event(Base):
    __tablename__ = "detection_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    event_type: Mapped[str] = mapped_column(String(50))
    location: Mapped[str] = mapped_column(String(50))
    source: Mapped[str] = mapped_column(String(50))
    confidence: Mapped[float] = mapped_column(Float)
    occurred_at: Mapped[datetime] = mapped_column(DateTime)
    detail: Mapped[dict] = mapped_column(JSON)


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    event_id: Mapped[int] = mapped_column(Integer)
    event_type: Mapped[str] = mapped_column(String(50))
    location: Mapped[str] = mapped_column(String(50))
    status: Mapped[str] = mapped_column(String(20))
