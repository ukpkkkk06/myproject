from typing import Optional, Tuple, List
from datetime import datetime

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.user import User
from app.models.role import Role
from app.models.user_role import UserRole
from app.core.exceptions import AppException

from app.schemas.user import UserCreate, UserUpdate, UsersSimplePage, UserSimple
from app.core.security import verify_password, get_password_hash
from app.core.exceptions import NotFoundException, ConflictException, AppException

def create_user(db: Session, payload: UserCreate) -> User:
    # 账号/邮箱唯一性校验（数据库也应有唯一索引，双保险）
    if db.query(User).filter(User.account == payload.account).first():
        raise ConflictException("account 已存在")
    if payload.email and db.query(User).filter(User.email == payload.email).first():
        raise ConflictException("email 已存在")

    user = User(
        account=payload.account,
        email=payload.email,
        nickname=payload.nickname,
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ConflictException("account 或 email 已存在")
    db.refresh(user)
    return user


def get_user(db: Session, user_id: int) -> User:
    user = db.get(User, user_id)
    if not user:
        raise NotFoundException("用户不存在")
    return user


# 兼容旧调用名，内部委托给 get_user，避免重复实现
def get_user_by_id(db: Session, user_id: int) -> User:
    return get_user(db, user_id)


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


def list_users_simple(
    db: Session,
    skip: int = 0,
    limit: int = 20,
    account: str | None = None,
    email: str | None = None,
):
    limit = max(1, min(int(limit), 100))
    skip = max(0, int(skip))

    filters = []
    if account:
        filters.append(User.account.like(f"%{account}%"))
    if email:
        filters.append(User.email.like(f"%{email}%"))

    # 正确统计总数
    total = db.query(func.count(User.id)).filter(*filters).scalar() or 0

    # 取每个用户的最小 role_id 作为主角色
    min_role_sq = (
        db.query(UserRole.user_id, func.min(UserRole.role_id).label("role_id"))
        .group_by(UserRole.user_id)
        .subquery()
    )

    q = (
        db.query(
            User.id,
            User.account,
            User.status,
            Role.name.label("role"),
        )
        .outerjoin(min_role_sq, min_role_sq.c.user_id == User.id)
        .outerjoin(Role, Role.id == min_role_sq.c.role_id)
        .filter(*filters)
        .order_by(User.id.desc())
        .offset(skip)
        .limit(limit)
    )

    rows = q.all()
    items = [UserSimple(id=r.id, account=r.account, status=r.status or "", role=r.role) for r in rows]
    return {"total": total, "items": items}


def update_user(db: Session, user_id: int, payload: UserUpdate) -> User:
    user = db.get(User, user_id)
    if not user:
        raise NotFoundException("未找到用户")

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
        raise ConflictException("email 已存在")
    db.refresh(user)
    return user


def delete_user(db: Session, user_id: int) -> None:
    user = db.get(User, user_id)
    if not user:
        raise NotFoundException("用户不存在")
    db.delete(user)
    db.commit()


def set_password(db: Session, user: User, plain: str) -> User:
    if not plain:
        raise AppException("新密码不能为空")
    user.password_hash = get_password_hash(plain)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, account: str, password: str) -> Optional[User]:
    user = db.query(User).filter(User.account == account).first()
    if not user or not user.password_hash or not verify_password(password, user.password_hash):
        return None
    user.last_login_at = datetime.utcnow()
    db.commit()
    db.refresh(user)
    return user


def get_user_info(db: Session, user: User) -> dict:
    # 读取用户角色名称与代码
    rows = (
        db.query(Role.name, Role.code)
        .join(UserRole, UserRole.role_id == Role.id)
        .filter(UserRole.user_id == user.id)
        .all()
    )
    role_names = [r.name for r in rows] if rows else []
    role_codes = [r.code for r in rows] if rows else []
    is_admin = any(code == "ADMIN" for code in role_codes)
    return {
        "id": user.id,
        "account": user.account,
        "status": user.status or "",
        "roles": role_names,
        "role_codes": role_codes,
        "is_admin": is_admin,
    }