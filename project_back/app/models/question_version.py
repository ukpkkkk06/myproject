from sqlalchemy import Column, Integer, BigInteger, ForeignKey, String, Text, JSON, Boolean, DateTime
from sqlalchemy.sql import func
from app.db.base import Base

class QuestionVersion(Base):
    __tablename__ = "QUESTION_VERSION"

    id = Column(Integer, primary_key=True, autoincrement=True)
    question_id = Column(Integer, ForeignKey("QUESTION.id"), nullable=False)
    version_no = Column(Integer, nullable=False)
    stem = Column(Text, nullable=False)
    options = Column(JSON, nullable=True)
    correct_answer = Column(String(255), nullable=True)
    explanation = Column(Text, nullable=True)
    change_note = Column(String(255), nullable=True)
    created_by = Column(Integer, ForeignKey("USER.id"), nullable=True)  # 缺失补上
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    # 如果你后来加了 updated_at，可再补：
    # updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())