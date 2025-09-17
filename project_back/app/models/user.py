from sqlalchemy import Column, BigInteger, String, DateTime, text
from sqlalchemy.sql import func
from app.db.base import Base

class User(Base):
    __tablename__ = "USER"  # 与表名完全一致
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    nickname = Column(String(100), nullable=True)
    account = Column(String(64), nullable=False, unique=True)
    email = Column(String(255), nullable=True, unique=True)
    status = Column(String(32), nullable=False, server_default=text("'ACTIVE'"))
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    last_login_at = Column(DateTime, nullable=True)
    password_hash = Column(String(255), nullable=True)
    role = Column(String(20), nullable=False, default="USER")