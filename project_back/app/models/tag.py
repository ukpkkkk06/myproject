from sqlalchemy import Column, BigInteger, String, DateTime, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from app.db.base import Base

class Tag(Base):
    __tablename__ = "TAG"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(128), nullable=False)
    type = Column(String(64))
    parent_id = Column(BigInteger)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())   # 保留 created_at
    # 移除 updated_at，避免 ORM 选择不存在的列

class QuestionTag(Base):
    __tablename__ = "QUESTION_TAG"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    # 注意外键目标表名需与实际表一致（大写）
    question_id = Column(BigInteger, ForeignKey("QUESTION.id"), nullable=False, index=True)
    tag_id = Column(BigInteger, ForeignKey("TAG.id"), nullable=False, index=True)

    __table_args__ = (
        UniqueConstraint("question_id", "tag_id", name="uk_question_tag"),
    )
