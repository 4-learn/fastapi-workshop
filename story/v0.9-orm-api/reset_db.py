"""
把資料表清空重建（測試前用，輸出才會跟講義一樣）

執行：python reset_db.py
"""
from app import models  # noqa: F401  讓 Base 認得所有資料表
from app.database import Base, engine

Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)
engine.dispose()
print("資料表已清空重建")
