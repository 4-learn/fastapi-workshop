import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase

# 連線：從環境變數讀，沒設定就用課堂預設值
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://postgres:postgres@localhost:5432/events",
)
engine = create_engine(DATABASE_URL)


class Base(DeclarativeBase):
    pass
