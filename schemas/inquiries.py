from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class InquiryBase(BaseModel):
    title: str
    content: str
    status: Optional[str] = "pending"
    priority: Optional[str] = "normal"
    school_id: Optional[int] = None
    corporation_id: Optional[int] = None


class InquiryCreate(InquiryBase):
    user_id: int


class InquiryUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    school_id: Optional[int] = None
    corporation_id: Optional[int] = None
    assigned_to_id: Optional[int] = None


class InquiryAssign(BaseModel):
    assigned_to_id: int


class InquiryStatusUpdate(BaseModel):
    status: str
    resolved_at: Optional[datetime] = None


class Inquiry(InquiryBase):
    id: int
    user_id: int
    assigned_to_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime] = None

    class Config:
        from_attributes = True


