from datetime import datetime
from sqlalchemy.orm import Session
from app.models.user import User
from app.core.security import verify_password, create_access_token
from app.core.exceptions import AppException

def login(db: Session, account: str, password: str) -> dict:
    account = (account or "").strip()
    password = (password or "").strip()
    if not account or not password:
        raise AppException("账号或密码不能为空", code=422, status_code=422)

    user = db.query(User).filter(User.account == account).first()
    if not user or not verify_password(password, user.password_hash or ""):
        raise AppException("账号或密码错误", code=401, status_code=401)
    if (user.status or "").upper() != "ACTIVE":
        raise AppException("账号未激活或已禁用", code=403, status_code=403)

    token = create_access_token(str(user.id))  # 只传 subject，避免 "sub" 被二次包裹

    user.last_login_at = datetime.utcnow()
    user.updated_at = datetime.utcnow()
    db.add(user)
    db.commit()

    return {"access_token": token, "token_type": "bearer"}
