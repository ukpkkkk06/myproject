from sqlalchemy import Column, Integer, ForeignKey, String, Boolean, DateTime
from sqlalchemy.sql import func
from app.db.base import Base

class Question(Base):
    __tablename__ = "QUESTION"

    id = Column(Integer, primary_key=True, autoincrement=True)
    current_version_id = Column(Integer, ForeignKey("QUESTION_VERSION.id"), nullable=True)
    type = Column(String(32), nullable=False)
    difficulty = Column(Integer, nullable=True)
    language_code = Column(String(16), nullable=True)
    source_type = Column(String(32), nullable=True)
    audit_status = Column(String(32), nullable=False, default="PENDING")
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())