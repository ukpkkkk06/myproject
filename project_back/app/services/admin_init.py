import os
import logging
from sqlalchemy.orm import Session
from sqlalchemy import or_
from datetime import datetime
from sqlalchemy.exc import IntegrityError

from app.models.user import User
from app.models.role import Role
from app.models.user_role import UserRole
from app.core.security import get_password_hash

logger = logging.getLogger(__name__)

ADMIN_ROLE_CODE = "ADMIN"
DEFAULT_ROLE_CODE = "USER"


def _get_or_create_role(db: Session, code: str, name: str, description: str | None = None) -> Role:
    """
    并发安全创建角色：
    - 先查；无则插入；
    - 如并发导致唯一键冲突，回滚并重查返回。
    """
    role = db.query(Role).filter(Role.code == code).first()
    if role:
        return role

    now = datetime.utcnow()
    role = Role(
        code=code,
        name=name,
        description=description or name,
        created_at=now,
        updated_at=now,
    )
    db.add(role)
    try:
        db.flush()
        return role
    except IntegrityError:
        # 另一并发事务已创建，回滚当前挂起的插入并重查
        db.rollback()
        existing = db.query(Role).filter(Role.code == code).first()
        if existing:
            return existing
        # 意外情况：仍不存在，则抛出以便上层记录
        raise


def _ensure_user_role(db: Session, user_id: int, role_id: int) -> None:
    """确保用户-角色关联存在。并发下重复创建将被唯一键拒绝，此时忽略即可。"""
    exists = db.query(UserRole).filter(
        UserRole.user_id == user_id,
        UserRole.role_id == role_id,
    ).first()
    if exists:
        return
    try:
        db.add(UserRole(user_id=user_id, role_id=role_id, created_at=datetime.utcnow()))
        db.flush()
    except IntegrityError:
        db.rollback()
        # 并发情况下，另一事务已插入，忽略即可
        return


def init_admin_from_env(db: Session) -> None:
    """
    从环境变量读取管理员初始化配置, 若管理员不存在则创建; 若已存在则不修改密码。

    环境变量:
    - ADMIN_INIT_ENABLED: 是否启用, 默认 1(启用)。设为 0/false/off 关闭
    - ADMIN_ACCOUNT: 管理员账号, 默认 admin
    - ADMIN_PASSWORD: 管理员初始密码, 为空则跳过初始化(出于安全考虑)
    - ADMIN_EMAIL: 管理员邮箱(可选)
    - ADMIN_NICKNAME: 管理员昵称, 默认 "管理员"
    """
    enabled = str(os.getenv("ADMIN_INIT_ENABLED", "1")).lower() in ("1", "true", "yes", "on")
    if not enabled:
        logger.info("[admin-init] disabled by ADMIN_INIT_ENABLED")
        return

    account = os.getenv("ADMIN_ACCOUNT", "admin").strip() or "admin"
    password = os.getenv("ADMIN_PASSWORD", "").strip()
    email = (os.getenv("ADMIN_EMAIL", "") or None)
    nickname = (os.getenv("ADMIN_NICKNAME", "管理员") or "管理员")

    if not password:
        logger.warning("[admin-init] ADMIN_PASSWORD is empty, skip initialize for safety")
        return

    # 确保角色存在（并发安全）
    admin_role = _get_or_create_role(db, ADMIN_ROLE_CODE, "管理员", "系统管理员, 拥有全部权限")
    user_role = _get_or_create_role(db, DEFAULT_ROLE_CODE, "普通用户", "基础权限用户")

    # 查找账号是否存在
    user = db.query(User).filter(User.account == account).first()
    if not user:
        # 创建管理员用户（并发安全）
        try:
            user = User(
                account=account,
                email=email,
                nickname=nickname,
                status="ACTIVE",
                password_hash=get_password_hash(password),
            )
            db.add(user)
            db.flush()
        except IntegrityError:
            db.rollback()
            # 并发下另一事务已创建，重查取回
            user = db.query(User).filter(User.account == account).first()
            if not user:
                raise
        # 绑定角色: ADMIN + USER（并发安全）
        _ensure_user_role(db, user.id, admin_role.id)
        _ensure_user_role(db, user.id, user_role.id)
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            # 再尝试一次仅确保关系存在
            user = db.query(User).filter(User.account == account).first()
            if user:
                _ensure_user_role(db, user.id, admin_role.id)
                _ensure_user_role(db, user.id, user_role.id)
                db.commit()
        logger.info("[admin-init] admin user created: %s", account)
        return

    # 已存在: 确保拥有管理员角色, 但不修改密码
    _ensure_user_role(db, user.id, admin_role.id)
    _ensure_user_role(db, user.id, user_role.id)
    db.commit()
    logger.info("[admin-init] admin user exists, ensure roles attached: %s", account)
