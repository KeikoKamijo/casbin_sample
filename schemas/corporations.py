from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class CorporationBase(BaseModel):
    name: str
    code: str
    description: Optional[str] = None


class CorporationCreate(CorporationBase):
    pass


class CorporationUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class Corporation(CorporationBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

