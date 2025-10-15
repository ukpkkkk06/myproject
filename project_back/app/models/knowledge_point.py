from sqlalchemy import Column, BigInteger, Integer, String, Text, DateTime, ForeignKey, UniqueConstraint, text
from sqlalchemy.orm import relationship
from app.db.base import Base

class KnowledgePoint(Base):
    __tablename__ = "KNOWLEDGE_POINT"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, index=True)
    parent_id = Column(BigInteger, ForeignKey("KNOWLEDGE_POINT.id", ondelete="SET NULL", onupdate="CASCADE"), nullable=True, index=True)
    description = Column(Text, nullable=True)
    level = Column(Integer, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))

    __table_args__ = (UniqueConstraint("name", "parent_id", name="uk_kp_name_parent"),)

    parent = relationship("KnowledgePoint", remote_side=[id], backref="children")