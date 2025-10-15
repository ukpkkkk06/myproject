from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.role import Role
from app.models.user_role import UserRole
from app.services import user_service
from app.schemas.user import AdminUpdateUserRequest
import tracemalloc

router = APIRouter()

try:
    router  # 复用已有 router
except NameError:
    from fastapi import APIRouter
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
    body: AdminUpdateUserRequest,
    db: Session = Depends(get_db),
    me: User = Depends(get_current_user),
):
    if not _is_admin(db, me):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权限")
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

@router.get("/admin/mem/stats", tags=["admin"])
def mem_stats():
    traced = tracemalloc.is_tracing()
    current_kb = peak_kb = None
    if traced:
        current, peak = tracemalloc.get_traced_memory()
        current_kb = round(current / 1024, 2)
        peak_kb = round(peak / 1024, 2)
    return {"traced": traced, "current_kb": current_kb, "peak_kb": peak_kb}

@router.get("/admin/mem/top", tags=["admin"])
def mem_top(limit: int = Query(20, ge=1, le=200)):
    if not tracemalloc.is_tracing():
        return {"traced": False, "items": []}
    snapshot = tracemalloc.take_snapshot()
    stats = snapshot.statistics("lineno")[:limit]
    items = []
    for s in stats:
        tb = s.traceback[0] if s.traceback else None
        items.append({
            "file": str(tb) if tb else None,
            "size_kb": round(s.size / 1024, 2),
            "count": s.count,
        })
    return {"traced": True, "items": items}

@router.post("/admin/mem/reset-peak", tags=["admin"])
def mem_reset_peak():
    if tracemalloc.is_tracing():
        tracemalloc.reset_peak()
    return {"ok": True}