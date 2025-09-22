from sqlalchemy import Column, BigInteger, String, DateTime
from sqlalchemy.sql import func
from app.db.base import Base

class User(Base):
    __tablename__ = "USER"

    id = Column(BigInteger, primary_key=True, index=True)
    nickname = Column(String(50), nullable=True)
    account = Column(String(50), nullable=False, unique=True, index=True)
    email = Column(String(100), nullable=True, unique=True)
    status = Column(String(20), nullable=False, server_default="active")
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    last_login_at = Column(DateTime, nullable=True)
    password_hash = Column(String(255), nullable=True)