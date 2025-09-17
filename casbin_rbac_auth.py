from typing import List
from fastapi import Depends, HTTPException, status
import models
from auth import get_current_user
from casbin_config import get_casbin_enforcer
import casbin


# グローバルなエンフォーサーインスタンス
_enforcer = None


def get_enforcer() -> casbin.Enforcer:
    """Casbinエンフォーサーのシングルトンインスタンスを取得"""
    global _enforcer
    if _enforcer is None:
        _enforcer = get_casbin_enforcer()
    return _enforcer


def casbin_check_permission(username: str, resource: str, action: str) -> bool:
    """
    Casbinを使用して権限をチェック

    Args:
        username: ユーザー名
        resource: リソース名 (users, corporations, schools, inquiries)
        action: アクション (read, create, update, delete)

    Returns:
        bool: 権限がある場合True
    """
    enforcer = get_enforcer()
    return enforcer.enforce(username, resource, action)


def require_casbin_permission(resource: str, action: str):
    """
    Casbinで指定されたリソース・アクションへの権限をチェックする依存関数を生成

    Args:
        resource: 対象リソース
        action: 実行アクション

    Returns:
        依存関数
    """
    def permission_checker(current_user: models.User = Depends(get_current_user)):
        if not casbin_check_permission(current_user.username, resource, action):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required permission: {action} on {resource}"
            )
        return current_user

    return permission_checker


# 便利な依存関数群

# Users リソース
def require_users_read():
    """ユーザー情報読み取り権限をチェック"""
    return require_casbin_permission("users", "read")


def require_users_create():
    """ユーザー作成権限をチェック"""
    return require_casbin_permission("users", "create")


def require_users_update():
    """ユーザー更新権限をチェック"""
    return require_casbin_permission("users", "update")


def require_users_delete():
    """ユーザー削除権限をチェック"""
    return require_casbin_permission("users", "delete")


# Corporations リソース
def require_corporations_read():
    """法人情報読み取り権限をチェック"""
    return require_casbin_permission("corporations", "read")


def require_corporations_create():
    """法人作成権限をチェック"""
    return require_casbin_permission("corporations", "create")


def require_corporations_update():
    """法人更新権限をチェック"""
    return require_casbin_permission("corporations", "update")


def require_corporations_delete():
    """法人削除権限をチェック"""
    return require_casbin_permission("corporations", "delete")


# Schools リソース
def require_schools_read():
    """学校情報読み取り権限をチェック"""
    return require_casbin_permission("schools", "read")


def require_schools_create():
    """学校作成権限をチェック"""
    return require_casbin_permission("schools", "create")


def require_schools_update():
    """学校更新権限をチェック"""
    return require_casbin_permission("schools", "update")


def require_schools_delete():
    """学校削除権限をチェック"""
    return require_casbin_permission("schools", "delete")


# Inquiries リソース
def require_inquiries_read():
    """問い合わせ読み取り権限をチェック"""
    return require_casbin_permission("inquiries", "read")


def require_inquiries_create():
    """問い合わせ作成権限をチェック"""
    return require_casbin_permission("inquiries", "create")


def require_inquiries_update():
    """問い合わせ更新権限をチェック"""
    return require_casbin_permission("inquiries", "update")


def require_inquiries_delete():
    """問い合わせ削除権限をチェック"""
    return require_casbin_permission("inquiries", "delete")


# ロール確認ヘルパー関数
def get_user_roles(username: str) -> List[str]:
    """ユーザーが持つロールの一覧を取得"""
    enforcer = get_enforcer()
    return enforcer.get_roles_for_user(username)


def has_role(username: str, role: str) -> bool:
    """ユーザーが指定されたロールを持っているかチェック"""
    return role in get_user_roles(username)


def is_admin(username: str) -> bool:
    """ユーザーが管理者かどうかチェック"""
    return has_role(username, "admin")


def is_accounting(username: str) -> bool:
    """ユーザーが経理担当者かどうかチェック"""
    return has_role(username, "accounting")


# ポリシー管理関数
def add_role_for_user(username: str, role: str) -> bool:
    """ユーザーにロールを追加"""
    enforcer = get_enforcer()
    return enforcer.add_role_for_user(username, role)


def delete_role_for_user(username: str, role: str) -> bool:
    """ユーザーからロールを削除"""
    enforcer = get_enforcer()
    return enforcer.delete_role_for_user(username, role)


def add_permission_for_role(role: str, resource: str, action: str) -> bool:
    """ロールに権限を追加"""
    enforcer = get_enforcer()
    return enforcer.add_policy(role, resource, action)


def delete_permission_for_role(role: str, resource: str, action: str) -> bool:
    """ロールから権限を削除"""
    enforcer = get_enforcer()
    return enforcer.remove_policy(role, resource, action)