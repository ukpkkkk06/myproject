from sqlalchemy import Column, BigInteger, Integer, String, DateTime, Boolean, Numeric
from app.db.base import Base

class UserAnswer(Base):
    __tablename__ = "USER_ANSWER"
    id = Column(BigInteger, primary_key=True)
    attempt_id = Column(BigInteger, index=True, nullable=False)
    user_id = Column(BigInteger, index=True, nullable=False)
    question_id = Column(BigInteger, index=True, nullable=False)
    paper_id = Column(BigInteger, index=True)
    user_answer = Column(String(1024))
    is_correct = Column(Boolean)
    score_obtained = Column(Numeric(10,2))
    time_spent_ms = Column(Integer)
    answer_time = Column(DateTime)
    first_flag = Column(Boolean, default=False, nullable=False)