from typing import Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.user import UserCreate, UserRead, UserUpdate, UsersPage, UsersSimplePage, UserOut
from app.services import user_service

router = APIRouter()


@router.post("/users", response_model=UserRead)
def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    return user_service.create_user(db, payload)


@router.get("/users/simple", response_model=UsersSimplePage)
def list_users_simple(
    skip: int = 0,
    limit: int = 20,
    account: str | None = None,
    email: str | None = None,
    db: Session = Depends(get_db),
):
    return user_service.list_users_simple(db, skip=skip, limit=limit, account=account, email=email)


@router.get("/users/{user_id:int}", response_model=UserOut)
def get_user(user_id: int, db: Session = Depends(get_db)):
    return user_service.get_user(db, user_id)


@router.put("/users/{user_id:int}", response_model=UserOut)
def update_user(user_id: int, body: dict, db: Session = Depends(get_db)):
    return user_service.update_user(db, user_id, body)  # 如果已实现 UserUpdate，请替换


@router.delete("/users/{user_id:int}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user_service.delete_user(db, user_id)
    return {"code": 0, "message": "ok"}