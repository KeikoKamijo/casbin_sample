from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
import models
from auth import get_current_user
from casbin_config import get_casbin_enforcer
from database import get_db


def verify_corporation_access(corporation_id: int):
    """法人アクセス権限を検証する依存関数ファクトリー"""

    def _verify_access(
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user)
    ) -> models.User:
        """
        ユーザーが指定された法人にアクセス権限を持つかチェック
        - ユーザーの所属法人IDとリクエストされた法人IDが一致する場合のみ許可
        """
        # ユーザーの所属法人IDとリクエスト法人IDが一致するかチェック
        if current_user.corporation_id != corporation_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: You can only access your own corporation's data"
            )

        # Casbinでの追加権限チェック（将来的な拡張用）
        enforcer = get_casbin_enforcer()

        # ユーザーに法人読み取り権限があるかチェック
        subject = f"user:{current_user.id}"
        object_name = f"corporation:{corporation_id}"
        action = "read"

        # 基本権限（所属法人チェック）が通った場合、Casbinでの追加チェック
        # 今回は所属法人チェックが主要な制御なので、Casbinは補助的に使用
        if not enforcer.enforce(subject, object_name, action):
            # 所属法人メンバーとしての基本権限を動的に追加
            enforcer.add_grouping_policy(f"user:{current_user.id}", "corporation_member")
            enforcer.add_policy("corporation_member", f"corporation:{corporation_id}", "read")

        return current_user

    return _verify_access


def create_corporation_access_dependency(corporation_id: int):
    """法人アクセス権限チェック用の依存関数を生成"""
    return Depends(verify_corporation_access(corporation_id))


def verify_corporation_management_access(corporation_id: int):
    """法人管理権限を検証する依存関数ファクトリー（将来の管理者機能用）"""

    def _verify_management_access(
        current_user: models.User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ) -> models.User:
        """
        ユーザーが指定された法人の管理権限を持つかチェック
        """
        # 基本的な所属チェック
        if current_user.corporation_id != corporation_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: You can only manage your own corporation"
            )

        # Casbinでの管理権限チェック
        enforcer = get_casbin_enforcer()
        subject = f"user:{current_user.id}"
        object_name = f"corporation:{corporation_id}"
        action = "write"

        if not enforcer.enforce(subject, object_name, action):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: Insufficient management privileges"
            )

        return current_user

    return _verify_management_access