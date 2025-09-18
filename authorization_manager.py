"""
シンプルなドメインベースCasbin認可マネージャー
"""
from fastapi import Depends, Request, HTTPException
import models
from auth import get_current_user
from casbin_config import get_casbin_enforcer


def extract_resource_from_path(path: str) -> str:
    """URLパスからリソース名を抽出"""
    if "/users" in path:
        return "users"
    elif "/corporations" in path:
        return "corporations"
    elif "/shops" in path:
        return "shops"
    elif "/inquiries" in path:
        return "inquiries"
    else:
        return "unknown"


def map_method_to_action(method: str) -> str:
    """HTTPメソッドをアクションにマッピング"""
    action_map = {
        "GET": "read",
        "POST": "create",
        "PUT": "update",
        "PATCH": "update",
        "DELETE": "delete"
    }
    return action_map.get(method, "read")


def authorize_request(user: models.User, resource: str, action: str) -> bool:
    """
    ドメインベースCasbinで認可チェック

    Args:
        user: 認証済みユーザー
        resource: アクセス対象リソース
        action: 実行アクション

    Returns:
        bool: True=allow, False=deny
    """
    try:
        # ユーザーの所属法人をドメインとして使用
        if user.corporation_id is None:
            return False

        domain = f"corporation_{user.corporation_id}"

        # Casbinで認可チェック
        enforcer = get_casbin_enforcer()
        result = enforcer.enforce(user.username, domain, resource, action)

        return result

    except Exception as e:
        print(f"Authorization error: {e}")
        return False


def authorization_manager(
    request: Request,
    current_user: models.User = Depends(get_current_user)
) -> bool:
    """
    FastAPI依存性注入用の認可チェック関数
    認証とは分離して、認可のみを行う
    権限チェックを行い、権限がない場合はHTTPExceptionを投げる
    権限がある場合はTrueを返す

    Note: get_current_userはエンドポイントでも呼ばれる可能性があるが、
    FastAPIの依存性キャッシュ機能により、同一リクエスト内では1回だけ実行される。
    参照: https://fastapi.tiangolo.com/tutorial/dependencies/#using-the-same-dependency-multiple-times
    """
    # URLとメソッドからリソース・アクションを抽出
    resource = extract_resource_from_path(request.url.path)
    action = map_method_to_action(request.method)

    # 認可チェック実行
    if not authorize_request(current_user, resource, action):
        raise HTTPException(
            status_code=403,
            detail=f"You don't have permission to {action} {resource}"
        )

    return True