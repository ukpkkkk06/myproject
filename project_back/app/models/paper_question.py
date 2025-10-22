from sqlalchemy import Column, BigInteger, Integer, Numeric
from app.db.base import Base

class PaperQuestion(Base):
    __tablename__ = "PAPER_QUESTION"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    paper_id = Column(BigInteger, index=True, nullable=False)
    question_id = Column(BigInteger, index=True, nullable=False)
    seq = Column(Integer, nullable=False)
    score = Column(Numeric(10,2), default=1)