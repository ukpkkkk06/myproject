from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from app.core.security import verify_password, create_access_token, get_password_hash
from app.core.exceptions import AppException, ConflictException
from app.models.user import User

def login(db: Session, account: str, password: str) -> dict:
    # 规范化与校验
    account = (account or "").strip()
    password = (password or "").strip()
    if not account or not password or account.lower() == "string":
        raise AppException("账号或密码错误", code=400, status_code=400)

    user = db.query(User).filter(User.account == account).first()
    if not user or not user.password_hash:
        raise AppException("账号或密码错误", code=400, status_code=400)
    if not verify_password(password, user.password_hash):
        raise AppException("账号或密码错误", code=400, status_code=400)
    user.last_login_at = datetime.utcnow()
    db.add(user)
    db.commit()
    token = create_access_token(sub=user.id)
    return {"access_token": token, "token_type": "bearer"}

def register(db: Session, account: str, password: str, email: str | None = None, nickname: str | None = None) -> User:
    account = (account or "").strip()
    password = (password or "").strip()
    email = (email or None)
    nickname = (nickname or None)

    if not account:
        raise AppException("账号不能为空", code=422, status_code=422)
    if account.lower() == "string":
        raise AppException("账号不合法", code=422, status_code=422)
    if not password:
        raise AppException("密码不能为空", code=422, status_code=422)

    if db.query(User).filter(User.account == account).first():
        raise ConflictException("账号已存在")

    now = datetime.utcnow()
    user = User(
        account=account,
        password_hash=get_password_hash(password),
        email=email,
        nickname=nickname,
        status="ACTIVE",
        created_at=now,
        updated_at=now,
    )
    db.add(user)
    try:
        db.flush()  # 取得 user.id
    except IntegrityError as e:
        db.rollback()
        # 唯一约束冲突
        raise ConflictException("账号或邮箱已存在")

    # 校验默认角色是否存在（id=2 普通用户）
    role_exists = db.execute(text("SELECT 1 FROM ROLE WHERE id = :rid"), {"rid": 2}).first()
    if not role_exists:
        db.rollback()
        # 回滚已创建用户，保持一致性
        try:
            db.delete(user)
            db.commit()
        except Exception:
            db.rollback()
        raise AppException("默认角色不存在：id=2", code=500, status_code=500)

    # 分配默认角色：显式写入 created_at，避免 1364
    try:
        db.execute(
            text("INSERT INTO USER_ROLE (user_id, role_id, created_at) VALUES (:uid, :rid, :created_at)"),
            {"uid": user.id, "rid": 2, "created_at": now},
        )
        db.commit()
    except IntegrityError:
        db.rollback()
        # 回滚用户
        try:
            db.delete(user)
            db.commit()
        except Exception:
            db.rollback()
        raise ConflictException("用户角色已存在")
    except Exception:
        db.rollback()
        try:
            db.delete(user)
            db.commit()
        except Exception:
            db.rollback()
        raise AppException("分配默认角色失败", code=500, status_code=500)

    db.refresh(user)
    return user
