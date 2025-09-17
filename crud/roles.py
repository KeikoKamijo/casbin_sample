from sqlalchemy.orm import Session
import models
from schemas.roles import RoleCreate, RoleUpdate, RolePermissionCreate


def get_role(db: Session, role_id: int):
    """ロール詳細取得"""
    return db.query(models.Role).filter(models.Role.id == role_id).first()


def get_roles(db: Session, skip: int = 0, limit: int = 100):
    """ロール一覧取得"""
    return db.query(models.Role).offset(skip).limit(limit).all()


def create_role(db: Session, role: RoleCreate):
    """新規ロール作成"""
    db_role = models.Role(**role.dict())
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return db_role


def update_role(db: Session, role_id: int, role: RoleUpdate):
    """ロール情報更新"""
    db_role = get_role(db, role_id)
    if not db_role:
        return None

    update_data = role.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_role, key, value)

    db.commit()
    db.refresh(db_role)
    return db_role


def delete_role(db: Session, role_id: int):
    """ロール削除"""
    db_role = get_role(db, role_id)
    if db_role:
        db.delete(db_role)
        db.commit()
        return True
    return False


# ロール権限管理
def get_role_permissions(db: Session, role_id: int):
    """ロール権限一覧取得"""
    # TODO: ロール権限テーブルから取得
    # 現在はCasbinから取得する想定
    from casbin_rbac_auth import get_enforcer

    enforcer = get_enforcer()
    policies = enforcer.get_policy()

    # ロール名を取得
    role = get_role(db, role_id)
    if not role:
        return []

    # 該当ロールのポリシーをフィルタ
    role_policies = []
    for policy in policies:
        if len(policy) >= 3:
            # subject, object, action の形式
            subject, obj, action = policy[0], policy[1], policy[2]
            # ここではユーザー固有のポリシーではなく、ロール固有のポリシーを想定
            # 実装時に適切に調整が必要
            pass

    return role_policies


def add_role_permission(db: Session, role_id: int, permission: RolePermissionCreate):
    """ロール権限追加"""
    # TODO: ロール権限テーブルに追加し、Casbinも更新
    role = get_role(db, role_id)
    if not role:
        return None

    # 現在はスタブ
    return {
        "role_id": role_id,
        "resource": permission.resource,
        "action": permission.action,
        "message": "Permission would be added (stub)"
    }


def remove_role_permission(db: Session, role_id: int, permission_id: int):
    """ロール権限削除"""
    # TODO: ロール権限テーブルから削除し、Casbinも更新
    return True


# ユーザーロール管理
def get_user_roles(db: Session, user_id: int):
    """ユーザーロール一覧取得"""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user or not user.role:
        return []

    return [user.role]


def assign_user_role(db: Session, user_id: int, role_id: int):
    """ユーザーロール割り当て"""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    role = get_role(db, role_id)

    if not user or not role:
        return False

    user.role_id = role_id
    db.commit()

    # Casbinポリシーも更新
    from casbin_config import sync_user_roles_to_casbin
    sync_user_roles_to_casbin()

    return True


def unassign_user_role(db: Session, user_id: int, role_id: int):
    """ユーザーロール解除"""
    user = db.query(models.User).filter(models.User.id == user_id).first()

    if not user or user.role_id != role_id:
        return False

    user.role_id = None
    db.commit()

    # Casbinポリシーも更新
    from casbin_config import sync_user_roles_to_casbin
    sync_user_roles_to_casbin()

    return True