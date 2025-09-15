from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List


class SchoolBase(BaseModel):
    name: str
    code: str
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None


class SchoolCreate(SchoolBase):
    corporation_ids: Optional[List[int]] = []


class SchoolUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None
    corporation_ids: Optional[List[int]] = None


class School(SchoolBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

