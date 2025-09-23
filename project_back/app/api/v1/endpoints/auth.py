from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.services import auth_service, user_service
from app.schemas.user import LoginRequest, Token, UserInfo, UpdateNicknameRequest, ChangePasswordRequest

router = APIRouter()

# 登录：/api/v1/login
@router.post("/login", response_model=Token)
def login(body: LoginRequest, db: Session = Depends(get_db)):
    return auth_service.login(db, body.account, body.password)

# 兼容：/api/v1/auth/login
@router.post("/auth/login", response_model=Token)
def login_compat(body: LoginRequest, db: Session = Depends(get_db)):
    return auth_service.login(db, body.account, body.password)

# 当前用户信息
@router.get("/me", response_model=UserInfo)
def me(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return user_service.get_user_info(db, current_user)

@router.put("/me/nickname", response_model=UserInfo)
def me_update_nickname(
    body: UpdateNicknameRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return user_service.update_nickname(db, current_user, body.nickname)

@router.put("/me/password")
def me_change_password(
    body: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user_service.change_password(db, current_user, body.old_password, body.new_password)
    return {"code": 0, "message": "密码已更新"}