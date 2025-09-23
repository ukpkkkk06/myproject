from sqlalchemy import Column, BigInteger, Integer, DateTime, Boolean, UniqueConstraint
from sqlalchemy.sql import func
from app.db.base import Base

class ErrorBook(Base):
    __tablename__ = "ERROR_BOOK"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False, index=True)
    question_id = Column(BigInteger, nullable=False, index=True)
    first_wrong_time = Column(DateTime)
    last_wrong_time = Column(DateTime)
    wrong_count = Column(Integer, nullable=False, default=0)
    next_review_time = Column(DateTime)
    mastered = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint("user_id", "question_id", name="uk_error_book_user_question"),
    )
