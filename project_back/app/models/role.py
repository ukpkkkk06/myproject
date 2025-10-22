from sqlalchemy import Column, BigInteger, String, DateTime
from app.db.base import Base
from sqlalchemy.orm import relationship

class Role(Base):
    __tablename__ = "ROLE"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    code = Column(String(50), nullable=True)
    name = Column(String(100), nullable=True)
    description = Column(String(255), nullable=True)
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)

