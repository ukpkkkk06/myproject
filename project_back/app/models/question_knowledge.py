from sqlalchemy import Column, BigInteger, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db.base import Base

class QuestionKnowledge(Base):
    __tablename__ = "QUESTION_KNOWLEDGE"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    question_id = Column(BigInteger, ForeignKey("QUESTION.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False, index=True)
    knowledge_id = Column(BigInteger, ForeignKey("KNOWLEDGE_POINT.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False, index=True)
    weight = Column(Integer, nullable=True)

    __table_args__ = (UniqueConstraint("question_id", "knowledge_id", name="uk_question_knowledge"),)

    question = relationship("Question", backref="knowledge_links")
    knowledge = relationship("KnowledgePoint", backref="question_links")