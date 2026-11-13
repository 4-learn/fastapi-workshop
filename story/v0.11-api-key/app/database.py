import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session

# 連線：從環境變數讀，沒設定就用課堂預設值
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://postgres:postgres@localhost:5432/events",
)
engine = create_engine(DATABASE_URL)


class Base(DeclarativeBase):
    pass


# 每個 request 拿一個 session，用完自動關掉
def get_db():
    with Session(engine) as session:
        yield session
