from sqlalchemy import Column, BigInteger, Integer, String, Text, DateTime
from sqlalchemy.dialects.mysql import JSON
from app.db.base import Base

class QuestionVersion(Base):
    __tablename__ = "QUESTION_VERSION"
    id = Column(BigInteger, primary_key=True)
    question_id = Column(BigInteger, index=True)
    version_no = Column(Integer, nullable=False)
    stem = Column(Text, nullable=False)
    options = Column(JSON)
    correct_answer = Column(String(255))
    explanation = Column(Text)
    is_active = Column(Integer, default=1)
    created_at = Column(DateTime)