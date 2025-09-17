from typing import Optional
from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session  # ← 补充这一行

from app.db.session import get_db
from app.schemas.user import UserCreate, UserRead, UserUpdate, UsersPage
from app.services.user_service import (
    create_user as svc_create_user,
    get_user_by_id as svc_get_user,
    list_users as svc_list_users,
    update_user as svc_update_user,
    delete_user as svc_delete_user,
)
from app.api.deps import get_current_user

# 受保护
router = APIRouter(dependencies=[Depends(get_current_user)])


@router.post("/users", response_model=UserRead)
def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    return svc_create_user(db, payload)


@router.get("/users/{user_id}", response_model=UserRead)
def get_user(user_id: int, db: Session = Depends(get_db)):
    return svc_get_user(db, user_id)


@router.get("/users", response_model=UsersPage)
def list_users(
    skip: int = 0,
    limit: int = 20,
    account: Optional[str] = None,
    email: Optional[str] = None,
    db: Session = Depends(get_db),
):
    # 过滤占位字符串
    if account in ("undefined", "null", ""):
        account = None
    if email in ("undefined", "null", ""):
        email = None
    total, items = svc_list_users(db, skip=skip, limit=limit, account=account, email=email)
    return {"total": total, "items": items}


@router.put("/users/{user_id}", response_model=UserRead)
def update_user(user_id: int, payload: UserUpdate, db: Session = Depends(get_db)):
    return svc_update_user(db, user_id, payload)


@router.delete("/users/{user_id}", status_code=204)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    svc_delete_user(db, user_id)
    return Response(status_code=204)