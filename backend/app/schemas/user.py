from typing import Optional
from datetime import datetime
from pydantic import BaseModel
from backend.app.models.user import UserRole

class UserBase(BaseModel):
    email: str
    full_name: str
    phone: Optional[str] = None
    role: UserRole = UserRole.CITIZEN

class UserCreate(UserBase):
    password: str
    department_id: Optional[str] = None

class UserLogin(BaseModel):
    email: str
    password: str

class UserResponse(UserBase):
    id: str
    department_id: Optional[str] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class TokenPayload(BaseModel):
    sub: Optional[str] = None
    exp: Optional[int] = None
