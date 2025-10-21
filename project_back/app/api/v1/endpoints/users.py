from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.schemas.user import UserCreate, UserRead, UserUpdate, UsersPage, UsersSimplePage, UserOut
from app.services import user_service
from app.models.user import User

router = APIRouter()


def require_admin(me: User = Depends(get_current_user)):
    """要求管理员权限"""
    if not getattr(me, "is_admin", False):
        raise HTTPException(status_code=403, detail="需要管理员权限")
    return me


@router.post("/users", response_model=UserRead)
def create_user(
    payload: UserCreate, 
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)  # 仅管理员可创建用户
):
    """创建用户 - 仅管理员可用"""
    return user_service.create_user(db, payload)


@router.get("/users/simple", response_model=UsersSimplePage)
def list_users_simple(
    skip: int = 0,
    limit: int = 20,
    account: str | None = None,
    email: str | None = None,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)  # 仅管理员可查看用户列表
):
    """查看用户列表 - 仅管理员可用"""
    return user_service.list_users_simple(db, skip=skip, limit=limit, account=account, email=email)


@router.get("/users/{user_id:int}", response_model=UserOut)
def get_user(
    user_id: int, 
    db: Session = Depends(get_db),
    me: User = Depends(get_current_user)  # 需要登录
):
    """查看用户详情 - 管理员可查看所有用户,普通用户只能查看自己"""
    # 检查权限:管理员可以查看任何用户,普通用户只能查看自己
    is_admin = getattr(me, "is_admin", False)
    if not is_admin and me.id != user_id:
        raise HTTPException(status_code=403, detail="无权限访问该用户信息")
    
    return user_service.get_user(db, user_id)


@router.put("/users/{user_id:int}", response_model=UserOut)
def update_user(
    user_id: int, 
    body: dict, 
    db: Session = Depends(get_db),
    me: User = Depends(get_current_user)  # 需要登录
):
    """修改用户信息 - 管理员可修改所有用户,普通用户只能修改自己"""
    # 检查权限:管理员可以修改任何用户,普通用户只能修改自己
    is_admin = getattr(me, "is_admin", False)
    if not is_admin and me.id != user_id:
        raise HTTPException(status_code=403, detail="无权限修改该用户信息")
    
    return user_service.update_user(db, user_id, body)


@router.delete("/users/{user_id:int}")
def delete_user(
    user_id: int, 
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)  # 仅管理员可删除用户
):
    """删除用户 - 仅管理员可用"""
    # 防止删除自己
    if admin.id == user_id:
        raise HTTPException(status_code=400, detail="不能删除自己的账号")
    
    user_service.delete_user(db, user_id)
    return {"code": 0, "message": "ok"}