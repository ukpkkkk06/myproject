from typing import Optional, List
from pydantic import BaseModel, EmailStr, ConfigDict, Field
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

class RegisterRequest(BaseModel):
    account: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6, max_length=64)
    email: Optional[str] = None
    nickname: Optional[str] = None

class UserOut(BaseModel):
    id: int
    account: str
    email: Optional[str] = None
    nickname: Optional[str] = None
    status: Optional[str] = None

    class Config:
        from_attributes = True

class UserSimple(BaseModel):
    id: int
    account: str
    status: str
    role: Optional[str] = None  # 主角色名称，如“管理员/普通用户”

class UsersSimplePage(BaseModel):
    total: int
    items: List[UserSimple]

# 个人中心所需模型
class UserInfo(BaseModel):
    id: int
    account: str
    status: str
    roles: List[str] = []
    role_codes: List[str] = []
    is_admin: bool = False
    email: Optional[str] = None
    nickname: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    last_login_at: Optional[str] = None

    class Config:
        from_attributes = True

class UpdateNicknameRequest(BaseModel):
    nickname: str

class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str