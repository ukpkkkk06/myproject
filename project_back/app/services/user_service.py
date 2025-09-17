from typing import Optional, Tuple, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import verify_password, get_password_hash
from datetime import datetime

def create_user(db: Session, payload: UserCreate) -> User:
    if db.query(User).filter(User.account == payload.account).first():
        raise HTTPException(status_code=400, detail="account 已存在")
    user = User(account=payload.account, email=payload.email, nickname=payload.nickname)
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="account 或 email 已存在")
    db.refresh(user)
    return user

def get_user_by_id(db: Session, user_id: int) -> User:
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="未找到用户")
    return user

def list_users(
    db: Session,
    skip: int = 0,
    limit: int = 20,
    account: Optional[str] = None,
    email: Optional[str] = None,
) -> Tuple[int, List[User]]:
    limit = max(1, min(limit, 100))
    q = db.query(User)
    if account:
        q = q.filter(User.account.like(f"%{account}%"))
    if email:
        q = q.filter(User.email.like(f"%{email}%"))
    total = q.count()
    items = q.order_by(User.id.desc()).offset(skip).limit(limit).all()
    return total, items

def update_user(db: Session, user_id: int, payload: UserUpdate) -> User:
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="未找到用户")
    if payload.email is not None:
        user.email = payload.email
    if payload.nickname is not None:
        user.nickname = payload.nickname
    if payload.status is not None:
        user.status = payload.status
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="email 已存在")
    db.refresh(user)
    return user

def delete_user(db: Session, user_id: int) -> None:
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="未找到用户")
    db.delete(user)
    db.commit()

def set_password(db: Session, user: User, plain: str) -> User:
    user.password_hash = get_password_hash(plain)
    db.commit(); db.refresh(user)
    return user

def authenticate_user(db: Session, account: str, password: str) -> Optional[User]:
    user = db.query(User).filter(User.account == account).first()
    if not user or not user.password_hash or not verify_password(password, user.password_hash):
        return None
    user.last_login_at = datetime.utcnow()
    db.commit(); db.refresh(user)
    return user