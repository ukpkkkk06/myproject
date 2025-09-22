from sqlalchemy import Column, BigInteger, DateTime
from app.db.base import Base

class UserRole(Base):
    __tablename__ = "USER_ROLE"
    id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, nullable=False, index=True)
    role_id = Column(BigInteger, nullable=False, index=True)
    created_at = Column(DateTime, nullable=True)
