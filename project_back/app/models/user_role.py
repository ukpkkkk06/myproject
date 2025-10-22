from sqlalchemy import Column, BigInteger, DateTime, UniqueConstraint, func
from app.db.base import Base

class UserRole(Base):
    __tablename__ = "USER_ROLE"  # 注意大小写与实际表一致
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False, index=True)
    role_id = Column(BigInteger, nullable=False, index=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    __table_args__ = (
        UniqueConstraint("user_id", "role_id", name="uq_user_role_user_role"),
    )
