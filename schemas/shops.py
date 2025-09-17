from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ShopBase(BaseModel):
    name: str
    address: Optional[str] = None
    manager_name: Optional[str] = None
    business_hours: Optional[str] = None
    is_active: bool = True
    corporation_id: int


class ShopCreate(ShopBase):
    pass


class ShopUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    manager_name: Optional[str] = None
    business_hours: Optional[str] = None
    is_active: Optional[bool] = None
    corporation_id: Optional[int] = None


class Shop(ShopBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ShopWithCorporations(Shop):
    pass