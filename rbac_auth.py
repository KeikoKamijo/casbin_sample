from typing import List
from fastapi import Depends, HTTPException, status
import models
from auth import get_current_user


def require_roles(allowed_roles: List[str]):
    """
    指定されたロールのいずれかを持つユーザーのみアクセス許可する依存関数を生成

    Args:
        allowed_roles: 許可されたロール名のリスト

    Returns:
        依存関数
    """
    def role_checker(current_user: models.User = Depends(get_current_user)):
        if not current_user.role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User has no assigned role"
            )

        if current_user.role.name not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {', '.join(allowed_roles)}"
            )

        return current_user

    return role_checker


def require_admin():
    """管理者ロールのみアクセス許可"""
    return require_roles(["admin"])


def require_accounting():
    """経理ロールのみアクセス許可"""
    return require_roles(["accounting"])


def require_admin_or_accounting():
    """管理者または経理ロールのみアクセス許可"""
    return require_roles(["admin", "accounting"])


def has_role(user: models.User, role_name: str) -> bool:
    """
    ユーザーが指定されたロールを持っているかチェック

    Args:
        user: チェック対象のユーザー
        role_name: ロール名

    Returns:
        bool: ロールを持っている場合True
    """
    return user.role and user.role.name == role_name


def is_admin(user: models.User) -> bool:
    """ユーザーが管理者かどうかチェック"""
    return has_role(user, "admin")


def is_accounting(user: models.User) -> bool:
    """ユーザーが経理担当者かどうかチェック"""
    return has_role(user, "accounting")