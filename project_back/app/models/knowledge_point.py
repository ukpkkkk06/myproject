from sqlalchemy import Column, BigInteger, Integer, String, Text, DateTime, ForeignKey, UniqueConstraint, text
from sqlalchemy.orm import relationship
from app.db.base import Base

class KnowledgePoint(Base):
    __tablename__ = "KNOWLEDGE_POINT"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, index=True)
    parent_id = Column(BigInteger, ForeignKey("KNOWLEDGE_POINT.id", ondelete="SET NULL", onupdate="CASCADE"), nullable=True, index=True)
    description = Column(Text, nullable=True)
    created_by = Column(BigInteger, ForeignKey("USER.id", ondelete="SET NULL", onupdate="CASCADE"), nullable=True, index=True)  # 🔥 添加创建者字段
    # 为向后兼容，数据库当前列名仍为 `level`，在模型中使用属性名 `depth` 映射到该列名
    depth = Column('level', Integer, nullable=True, comment="树形结构深度：1=学科 2=章节 3=知识点")
    # sort_order 尚未在数据库中创建，暂不要在模型中声明以避免查询时报错。
    created_at = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))

    __table_args__ = (UniqueConstraint("name", "parent_id", name="uk_kp_name_parent"),)

    parent = relationship("KnowledgePoint", remote_side=[id], backref="children")