from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class RoleBase(BaseModel):
    name: str
    description: Optional[str] = None


class RoleCreate(RoleBase):
    pass


class RoleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class Role(RoleBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ロール権限関連のスキーマ
class RolePermissionBase(BaseModel):
    resource: str  # users, corporations, shops, inquiries
    action: str    # read, create, update, delete


class RolePermissionCreate(RolePermissionBase):
    pass


class RolePermissionUpdate(BaseModel):
    resource: Optional[str] = None
    action: Optional[str] = None


class RolePermission(RolePermissionBase):
    id: int
    role_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ロール with 権限情報
class RoleWithPermissions(Role):
    permissions: list[RolePermission] = []

    class Config:
        from_attributes = True