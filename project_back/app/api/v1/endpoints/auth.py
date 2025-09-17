from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.user import LoginRequest, Token
from app.core.security import create_access_token
from app.services.user_service import authenticate_user

router = APIRouter()

@router.post("/login", response_model=Token)
def login(body: LoginRequest, db: Session = Depends(get_db)):
    user = authenticate_user(db, body.account, body.password)
    if not user:
        raise HTTPException(status_code=400, detail="账号或密码错误")
    token = create_access_token(user.id)
    return {"access_token": token, "token_type": "bearer"}