from typing import Optional, List
from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime

class UserCreate(BaseModel):
    account: str
    email: Optional[EmailStr] = None
    nickname: Optional[str] = None

class UserRead(BaseModel):
    id: int
    account: str
    email: Optional[str] = None
    nickname: Optional[str] = None
    status: str
    last_login_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    nickname: Optional[str] = None
    status: Optional[str] = None

class UsersPage(BaseModel):
    total: int
    items: List[UserRead]

class LoginRequest(BaseModel):
    account: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"