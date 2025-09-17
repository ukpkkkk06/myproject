from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import jwt
from passlib.context import CryptContext
from app.core.config import settings

# 改为 pbkdf2_sha256，免 bcrypt 依赖
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def get_password_hash(plain: str) -> str:
    return pwd_context.hash(plain)

def create_access_token(sub: str | int, expires_minutes: Optional[int] = None) -> str:
    exp_minutes = expires_minutes or settings.JWT_EXPIRE_MINUTES
    expire = datetime.now(timezone.utc) + timedelta(minutes=exp_minutes)
    to_encode = {"sub": str(sub), "exp": expire}
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALG)