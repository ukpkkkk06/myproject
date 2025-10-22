from sqlalchemy import Column, BigInteger, String, DateTime, Integer, Boolean  # 加入 Boolean
from sqlalchemy.sql import func
from app.db.base import Base

class Paper(Base):
    __tablename__ = "PAPER"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    is_public = Column(Boolean, default=False)
    status = Column(String(32), default="PRACTICE")
    created_by = Column(BigInteger)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())