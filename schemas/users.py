from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    corporation_id: Optional[int] = None
    role_id: Optional[int] = None


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    corporation_id: Optional[int] = None
    role_id: Optional[int] = None


# Forward reference for Role
class RoleForUser(BaseModel):
    id: int
    name: str
    description: Optional[str] = None

    class Config:
        from_attributes = True


class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    role: Optional[RoleForUser] = None

    class Config:
        from_attributes = True