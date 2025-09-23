from sqlalchemy import Column, BigInteger, String, Integer, DateTime, Boolean
from app.db.base import Base

class Question(Base):
    __tablename__ = "QUESTION"
    id = Column(BigInteger, primary_key=True)
    current_version_id = Column(BigInteger, index=True)
    type = Column(String(32), nullable=False)
    difficulty = Column(Integer)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)