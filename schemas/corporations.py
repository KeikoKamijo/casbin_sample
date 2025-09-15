from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


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


class CorporationWithUsers(Corporation):
    users: List['User'] = []

    class Config:
        from_attributes = True


class CorporationWithSchools(Corporation):
    schools: List['School'] = []

    class Config:
        from_attributes = True


# Forward references will be resolved when other schemas are imported
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .users import User
    from .schools import School