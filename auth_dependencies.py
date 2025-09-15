from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
import models
from auth import get_current_user
from database import get_db


def verify_corporation_access_service(
    current_user: models.User,
    corporation_id: int
) -> None:
    """
    法人アクセス権限を検証するサービス関数

    Args:
        current_user: 現在のユーザー
        corporation_id: 検証対象の法人ID

    Raises:
        HTTPException: アクセス権限がない場合
    """
    if current_user.corporation_id != corporation_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: You can only access your own corporation's data"
        )


def verify_user_access_service(
    current_user: models.User,
    target_user_id: int
) -> None:
    """
    ユーザーアクセス権限を検証するサービス関数
    自分自身のデータのみアクセス可能

    Args:
        current_user: 現在のユーザー
        target_user_id: 対象ユーザーID

    Raises:
        HTTPException: アクセス権限がない場合
    """
    if current_user.id != target_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: You can only access your own data"
        )


def get_corporation_access_checker(
    request: Request,
    current_user: models.User = Depends(get_current_user)
) -> models.User:
    """
    法人アクセス権限を検証する依存関数

    FastAPIのRequestオブジェクトからpath parameterを取得して権限チェックを行う

    Args:
        request: FastAPIのRequestオブジェクト
        current_user: 現在のユーザー

    Returns:
        認証済みユーザー

    Raises:
        HTTPException: アクセス権限がない場合
    """
    # path parameterから corporation_id を取得
    corporation_id = request.path_params.get("corporation_id")

    if corporation_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Corporation ID not found in path"
        )

    try:
        corporation_id = int(corporation_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid corporation ID format"
        )

    # 権限チェック実行
    verify_corporation_access_service(current_user, corporation_id)

    return current_user


def get_user_access_checker(
    request: Request,
    current_user: models.User = Depends(get_current_user)
) -> models.User:
    """
    ユーザーアクセス権限を検証する依存関数

    FastAPIのRequestオブジェクトからpath parameterを取得して権限チェックを行う

    Args:
        request: FastAPIのRequestオブジェクト
        current_user: 現在のユーザー

    Returns:
        認証済みユーザー

    Raises:
        HTTPException: アクセス権限がない場合
    """
    # path parameterから user_id を取得
    user_id = request.path_params.get("user_id")

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User ID not found in path"
        )

    try:
        user_id = int(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )

    # 権限チェック実行
    verify_user_access_service(current_user, user_id)

    return current_user