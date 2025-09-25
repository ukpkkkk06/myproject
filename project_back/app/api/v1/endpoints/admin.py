from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Body, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.role import Role
from app.models.user_role import UserRole
from app.services import user_service

router = APIRouter()

def _is_admin(db: Session, me: User) -> bool:
    rows = (
        db.query(Role.code)
        .join(UserRole, UserRole.role_id == Role.id)
        .filter(UserRole.user_id == me.id)
        .all()
    )
    return any((r.code or "").upper() == "ADMIN" for r in rows)

class AdminRoleItem(BaseModel):
    code: str
    name: Optional[str] = None

class AdminUserDetail(BaseModel):
    id: int
    account: str
    nickname: Optional[str] = None
    email: Optional[str] = None
    status: Optional[str] = None
    roles: List[AdminRoleItem] = []
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    last_login_at: Optional[str] = None

@router.get("/admin/users/{uid:int}", response_model=AdminUserDetail)
def admin_get_user(uid: int, db: Session = Depends(get_db), me: User = Depends(get_current_user)):
    if not _is_admin(db, me):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权限")
    u = db.get(User, uid)
    if not u:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")
    role_rows = (
        db.query(Role.code, Role.name)
        .join(UserRole, UserRole.role_id == Role.id)
        .filter(UserRole.user_id == u.id)
        .all()
    )
    return AdminUserDetail(
        id=u.id,
        account=u.account,
        nickname=u.nickname,
        email=u.email,
        status=u.status,
        roles=[AdminRoleItem(code=r.code, name=r.name) for r in role_rows],
        created_at=u.created_at.isoformat() if u.created_at else None,
        updated_at=u.updated_at.isoformat() if u.updated_at else None,
        last_login_at=u.last_login_at.isoformat() if u.last_login_at else None,
    )

@router.put("/admin/users/{uid:int}")
def admin_update_user(
    uid: int,
    body: dict = Body(...),
    db: Session = Depends(get_db),
    me: User = Depends(get_current_user),
):
    if not _is_admin(db, me):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权限")
    # 直接复用 user_service.update_user，支持 nickname/email/status
    user_service.update_user(db, uid, body)
    return {"code": 0, "message": "ok"}

class AdminResetPasswordRequest(BaseModel):
    password: str = Field(..., min_length=6, max_length=64)

@router.put("/admin/users/{uid:int}/password")
def admin_reset_password(
    uid: int,
    body: AdminResetPasswordRequest,
    db: Session = Depends(get_db),
    me: User = Depends(get_current_user),
):
    if not _is_admin(db, me):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权限")
    u = db.get(User, uid)
    if not u:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")
    user_service.set_password(db, u, body.password)
    return {"code": 0, "message": "ok"}