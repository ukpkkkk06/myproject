from sqlalchemy import Column, BigInteger, Integer, String, DateTime, Numeric
from sqlalchemy.sql import func
from app.db.base import Base

class ExamAttempt(Base):
    __tablename__ = "EXAM_ATTEMPT"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, index=True, nullable=False)
    paper_id = Column(BigInteger, index=True, nullable=False)
    attempt_index = Column(Integer, default=1)
    start_time = Column(DateTime, nullable=False)
    submit_time = Column(DateTime)
    total_score = Column(Numeric(10,2))
    calculated_accuracy = Column(Numeric(6,4))
    status = Column(String(32), default="IN_PROGRESS")
    duration_seconds = Column(Integer)
    created_at = Column(DateTime, nullable=False, server_default=func.now())