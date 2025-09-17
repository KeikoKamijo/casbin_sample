"""
Casbinベースのロールベース認可依存関数
現在のABACと同じパターンでDependency Injectionを使用
"""
from fastapi import Depends, HTTPException, status, Request
import models
from auth import get_current_user
from casbin_rbac_auth import casbin_check_permission


def casbin_access_controller(
    request: Request,
    current_user: models.User = Depends(get_current_user)
) -> models.User:
    """
    汎用的なCasbinアクセスコントローラー
    URLからリソースとHTTPメソッドを自動判定してRBACチェックを実行
    """
    # URLからリソースを抽出
    path = request.url.path
    method = request.method.lower()

    # URLからリソース名を判定
    resource = None
    if "/users" in path:
        resource = "users"
    elif "/corporations" in path:
        resource = "corporations"
    elif "/schools" in path:
        resource = "schools"
    elif "/inquiries" in path:
        resource = "inquiries"

    if resource is None:
        # リソースが判定できない場合はスルー（他の認証に任せる）
        return current_user

    # HTTPメソッドからアクションを判定
    action_map = {
        "get": "read",
        "post": "create",
        "put": "update",
        "patch": "update",
        "delete": "delete"
    }

    action = action_map.get(method, "read")

    # Casbinで権限チェック
    if not casbin_check_permission(current_user.username, resource, action):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied. Required permission: {action} on {resource}. Your role: {current_user.role.name if current_user.role else 'None'}"
        )

    return current_user


def casbin_abac_access_controller(
    request: Request,
    current_user: models.User = Depends(get_current_user)
) -> models.User:
    """
    CasbinのRBACとABACを組み合わせた汎用アクセスコントローラー

    1. まずCasbinでRBAC権限チェック
    2. 次にABACで所属法人チェック（管理者は除外）
    """
    # まずRBACチェック
    current_user = casbin_access_controller(request, current_user)

    # 次にABACチェック（法人関連のパスのみ）
    path = request.url.path
    if "/corporations/" in path:
        corporation_id = request.path_params.get("corporation_id")

        if corporation_id is not None:
            try:
                corporation_id = int(corporation_id)

                # 管理者は全法人にアクセス可能（RBAC優先）
                if current_user.role and current_user.role.name == "admin":
                    pass  # 制限なし
                else:
                    # 他のロールは所属法人のみアクセス可能（ABAC制限）
                    if current_user.corporation_id != corporation_id:
                        raise HTTPException(
                            status_code=status.HTTP_403_FORBIDDEN,
                            detail="Access denied: You can only access your own corporation's data"
                        )
            except (ValueError, TypeError):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid corporation ID format"
                )

    return current_user


def get_casbin_access_checker(resource: str, action: str):
    """
    CasbinでRBAC権限をチェックする依存関数ファクトリー

    Args:
        resource: リソース名 (users, corporations, schools, inquiries)
        action: アクション (read, create, update, delete)

    Returns:
        権限チェック済みのcurrent_userを返す依存関数
    """
    def check_access(current_user: models.User = Depends(get_current_user)):
        if not casbin_check_permission(current_user.username, resource, action):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required permission: {action} on {resource}"
            )
        return current_user

    return check_access


# 各リソース・アクション用の便利な依存関数
def get_users_read_checker():
    """ユーザー読み取り権限チェック"""
    return get_casbin_access_checker("users", "read")


def get_users_create_checker():
    """ユーザー作成権限チェック"""
    return get_casbin_access_checker("users", "create")


def get_users_update_checker():
    """ユーザー更新権限チェック"""
    return get_casbin_access_checker("users", "update")


def get_users_delete_checker():
    """ユーザー削除権限チェック"""
    return get_casbin_access_checker("users", "delete")


def get_corporations_read_checker():
    """法人読み取り権限チェック"""
    return get_casbin_access_checker("corporations", "read")


def get_corporations_create_checker():
    """法人作成権限チェック"""
    return get_casbin_access_checker("corporations", "create")


def get_corporations_update_checker():
    """法人更新権限チェック"""
    return get_casbin_access_checker("corporations", "update")


def get_corporations_delete_checker():
    """法人削除権限チェック"""
    return get_casbin_access_checker("corporations", "delete")


def get_schools_read_checker():
    """学校読み取り権限チェック"""
    return get_casbin_access_checker("schools", "read")


def get_schools_create_checker():
    """学校作成権限チェック"""
    return get_casbin_access_checker("schools", "create")


def get_schools_update_checker():
    """学校更新権限チェック"""
    return get_casbin_access_checker("schools", "update")


def get_schools_delete_checker():
    """学校削除権限チェック"""
    return get_casbin_access_checker("schools", "delete")


def get_inquiries_read_checker():
    """問い合わせ読み取り権限チェック"""
    return get_casbin_access_checker("inquiries", "read")


def get_inquiries_create_checker():
    """問い合わせ作成権限チェック"""
    return get_casbin_access_checker("inquiries", "create")


def get_inquiries_update_checker():
    """問い合わせ更新権限チェック"""
    return get_casbin_access_checker("inquiries", "update")


def get_inquiries_delete_checker():
    """問い合わせ削除権限チェック"""
    return get_casbin_access_checker("inquiries", "delete")


# ABAC + RBAC 複合チェック用の依存関数
def get_corporation_rbac_access_checker(action: str = "read"):
    """
    法人アクセス権限をRBACとABACの両方でチェック

    1. まずCasbinでRBACの権限をチェック
    2. 次に所属法人の一致をチェック（ABAC）

    Args:
        action: corporations リソースに対するアクション
    """
    def check_combined_access(
        request,
        current_user: models.User = Depends(get_casbin_access_checker("corporations", action))
    ):
        # RBACチェックは上記で完了済み

        # 次にABACチェック（所属法人の確認）
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

        # 管理者は全法人にアクセス可能（RBAC優先）
        # 経理は自分の所属法人のみアクセス可能（ABAC制限）
        if current_user.role and current_user.role.name == "admin":
            # 管理者は制限なし
            pass
        else:
            # 経理など他のロールは所属法人のみ
            if current_user.corporation_id != corporation_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied: You can only access your own corporation's data"
                )

        return current_user

    return check_combined_access