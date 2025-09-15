from typing import Callable, Any
from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
import models
from auth import get_current_user
from database import get_db


def verify_corporation_access_service(
    current_user: models.User,
    corporation_id: int
) -> None:
    if current_user.corporation_id != corporation_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: You can only access your own corporation's data"
        )


def verify_user_access_service(
    current_user: models.User,
    target_user_id: int
) -> None:
    if current_user.id != target_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: You can only access your own data"
        )


def access_controller(
    request: Request,
    current_user: models.User = Depends(get_current_user)
) -> models.User:
    """
    汎用的なアクセスコントローラー
    path parameterに応じて適切な権限チェックを実行
    """
    path_params = request.path_params

    # corporation_id に基づく権限チェック
    if "corporation_id" in path_params:
        corporation_id = path_params.get("corporation_id")
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
        verify_corporation_access_service(current_user, corporation_id)

    # user_id に基づく権限チェック
    elif "user_id" in path_params:
        user_id = path_params.get("user_id")
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
        verify_user_access_service(current_user, user_id)

    # school_id などの他のリソースにも拡張可能
    # elif "school_id" in path_params:
    #     # school用の権限チェックロジック
    #     pass

    return current_user


def get_corporation_access_checker(
    request: Request,
    current_user: models.User = Depends(get_current_user)
) -> models.User:
    """
    法人アクセス権限を検証する依存関数（後方互換性のため）
    """
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

    verify_corporation_access_service(current_user, corporation_id)
    return current_user


def get_user_access_checker(
    request: Request,
    current_user: models.User = Depends(get_current_user)
) -> models.User:
    """
    ユーザーアクセス権限を検証する依存関数（後方互換性のため）
    """
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

    verify_user_access_service(current_user, user_id)
    return current_user


