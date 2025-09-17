from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

import crud
import schemas
import models
from database import get_db
from auth import security
from authorization_manager import authorization_manager

router = APIRouter(
    prefix="/roles",
    tags=["roles"],
    responses={404: {"description": "Not found"}},
)


@router.get("/", response_model=List[schemas.Role], summary="ロール一覧取得", dependencies=[Depends(security)])
def read_roles(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(authorization_manager)
):
    """
    ロール一覧を取得します。
    管理者のみアクセス可能。
    """
    roles = crud.get_roles(db, skip=skip, limit=limit)
    return roles


@router.get("/{role_id}", response_model=schemas.Role, summary="ロール詳細取得", dependencies=[Depends(security)])
def read_role(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(authorization_manager)
):
    """
    指定IDのロール詳細を取得します。
    """
    db_role = crud.get_role(db, role_id=role_id)
    if db_role is None:
        raise HTTPException(status_code=404, detail="Role not found")
    return db_role


@router.post("/", response_model=schemas.Role, summary="ロール作成", dependencies=[Depends(security)])
def create_role(
    role: schemas.RoleCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(authorization_manager)
):
    """
    新規ロールを作成します。
    管理者のみ実行可能。
    """
    return crud.create_role(db=db, role=role)


@router.put("/{role_id}", response_model=schemas.Role, summary="ロール更新", dependencies=[Depends(security)])
def update_role(
    role_id: int,
    role: schemas.RoleUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(authorization_manager)
):
    """
    指定IDのロール情報を更新します。
    """
    db_role = crud.update_role(db, role_id=role_id, role=role)
    if db_role is None:
        raise HTTPException(status_code=404, detail="Role not found")
    return db_role


@router.delete("/{role_id}", summary="ロール削除", dependencies=[Depends(security)])
def delete_role(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(authorization_manager)
):
    """
    指定IDのロールを削除します。
    """
    success = crud.delete_role(db, role_id=role_id)
    if not success:
        raise HTTPException(status_code=404, detail="Role not found")
    return {"message": "Role deleted successfully"}


# ロール権限管理
@router.get("/{role_id}/permissions", summary="ロール権限一覧取得", dependencies=[Depends(security)])
def read_role_permissions(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(authorization_manager)
):
    """
    指定ロールの権限一覧を取得します。
    """
    db_role = crud.get_role(db, role_id=role_id)
    if db_role is None:
        raise HTTPException(status_code=404, detail="Role not found")

    permissions = crud.get_role_permissions(db, role_id=role_id)
    return {"role": db_role, "permissions": permissions}


@router.post("/{role_id}/permissions", summary="ロール権限追加", dependencies=[Depends(security)])
def add_role_permission(
    role_id: int,
    permission: schemas.RolePermissionCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(authorization_manager)
):
    """
    指定ロールに権限を追加します。
    """
    db_role = crud.get_role(db, role_id=role_id)
    if db_role is None:
        raise HTTPException(status_code=404, detail="Role not found")

    permission_result = crud.add_role_permission(db, role_id=role_id, permission=permission)
    return {"message": "Permission added successfully", "permission": permission_result}


@router.delete("/{role_id}/permissions/{permission_id}", summary="ロール権限削除", dependencies=[Depends(security)])
def remove_role_permission(
    role_id: int,
    permission_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(authorization_manager)
):
    """
    指定ロールから権限を削除します。
    """
    success = crud.remove_role_permission(db, role_id=role_id, permission_id=permission_id)
    if not success:
        raise HTTPException(status_code=404, detail="Permission not found")
    return {"message": "Permission removed successfully"}


# ユーザーロール管理
@router.get("/users/{user_id}/roles", response_model=List[schemas.Role], summary="ユーザーロール一覧取得", dependencies=[Depends(security)])
def read_user_roles(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(authorization_manager)
):
    """
    指定ユーザーのロール一覧を取得します。
    """
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    roles = crud.get_user_roles(db, user_id=user_id)
    return roles


@router.post("/users/{user_id}/roles/{role_id}", summary="ユーザーロール割り当て", dependencies=[Depends(security)])
def assign_user_role(
    user_id: int,
    role_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(authorization_manager)
):
    """
    指定ユーザーにロールを割り当てます。
    """
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    db_role = crud.get_role(db, role_id=role_id)
    if db_role is None:
        raise HTTPException(status_code=404, detail="Role not found")

    success = crud.assign_user_role(db, user_id=user_id, role_id=role_id)
    if not success:
        raise HTTPException(status_code=400, detail="Role assignment failed")

    return {"message": "Role assigned successfully"}


@router.delete("/users/{user_id}/roles/{role_id}", summary="ユーザーロール解除", dependencies=[Depends(security)])
def unassign_user_role(
    user_id: int,
    role_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(authorization_manager)
):
    """
    指定ユーザーからロールを解除します。
    """
    success = crud.unassign_user_role(db, user_id=user_id, role_id=role_id)
    if not success:
        raise HTTPException(status_code=404, detail="Role assignment not found")

    return {"message": "Role unassigned successfully"}


# Casbin ポリシー管理
@router.post("/sync-casbin", summary="Casbinポリシー同期", dependencies=[Depends(security)])
def sync_casbin_policies(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(authorization_manager)
):
    """
    データベースのロール・権限情報をCasbinと同期します。
    管理者のみ実行可能。
    """
    from casbin_config import sync_user_roles_to_casbin

    success = sync_user_roles_to_casbin()
    if success:
        return {"message": "Casbin policies synchronized successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to synchronize Casbin policies")


@router.get("/casbin-policies", summary="Casbinポリシー一覧取得", dependencies=[Depends(security)])
def read_casbin_policies(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(authorization_manager)
):
    """
    現在のCasbinポリシーを取得します。
    管理者のみアクセス可能。
    """
    from casbin_rbac_auth import get_enforcer

    enforcer = get_enforcer()
    policies = enforcer.get_policy()
    groupings = enforcer.get_grouping_policy()

    return {
        "policies": policies,
        "groupings": groupings,
        "total_policies": len(policies),
        "total_groupings": len(groupings)
    }