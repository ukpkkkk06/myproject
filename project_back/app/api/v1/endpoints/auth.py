from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.services import auth_service, user_service
from app.schemas.user import LoginRequest, Token, RegisterRequest, UserOut, UserInfo

router = APIRouter()

@router.post("/login", response_model=Token)
def login(body: LoginRequest, db: Session = Depends(get_db)):
    return auth_service.login(db, body.account, body.password)

@router.post("/register", response_model=UserOut)
def register(body: RegisterRequest, db: Session = Depends(get_db)):
    user = auth_service.register(db, body.account, body.password, body.email, body.nickname)
    return user

@router.get("/me", response_model=UserInfo)
def me(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return user_service.get_user_info(db, current_user)