"""
責務分離されたセキュリティチェッカークラス群
各チェッカーは独立した責任を持ち、AuthorizationManagerで統合される
"""
from fastapi import HTTPException, status, Request
import models
from casbin_rbac_auth import casbin_check_permission


class TenantsSecurityChecker:
    """
    マルチテナントセキュリティチェッカー
    現在のABAC実装からテナント判定部分を専門クラス化
    """

    def __init__(self, user: models.User, request: Request = None):
        self.user = user
        self.request = request
        self.tenant_id = None

    def check(self) -> dict:
        """
        マルチテナント制御チェック（最優先で実行されるべき）

        Returns:
            dict: テナント情報のコンテキスト
        """
        if self.user.corporation_id is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: User has no tenant association"
            )

        self.tenant_id = self.user.corporation_id

        # 法人関連のパスの場合、追加のテナントチェック
        if self.request and "/corporations/" in self.request.url.path:
            self._check_corporation_path_access()

        return {
            "tenant_id": self.tenant_id,
            "tenant_validated": True
        }

    def _check_corporation_path_access(self):
        """法人関連パスでの詳細なテナントアクセス制御"""
        corporation_id = self.request.path_params.get("corporation_id")

        if corporation_id is not None:
            try:
                corporation_id = int(corporation_id)

                # 基本ルール：ユーザーは自分の所属法人のデータのみアクセス可能
                # （管理者でも同様。super_adminが必要な場合は別途実装）
                if self.user.corporation_id != corporation_id:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Access denied: You can only access corporation {self.user.corporation_id} data, not {corporation_id}"
                    )
            except (ValueError, TypeError):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid corporation ID format"
                )


class RBACSecurityChecker:
    """
    ロールベースアクセス制御チェッカー
    Casbinを使用したマルチテナント対応RBAC
    """

    def __init__(self, user: models.User, request: Request):
        self.user = user
        self.request = request

    def check(self, tenant_context: dict) -> dict:
        """
        RBAC権限チェック（テナント情報を前提とする）

        Args:
            tenant_context: TenantsSecurityCheckerからの結果

        Returns:
            dict: RBAC情報のコンテキスト
        """
        if not tenant_context.get("tenant_validated", False):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal error: Tenant validation must be performed before RBAC check"
            )

        tenant_id = tenant_context["tenant_id"]
        resource, action = self._extract_resource_action()

        if resource is None:
            # リソースが判定できない場合はスルー（他の認証に任せる）
            return {"rbac_validated": True, "resource": None, "action": None}

        # マルチテナント対応のCasbinリソース名
        casbin_resource = f"corporation:{tenant_id}:{resource}"

        # Casbinで権限チェック
        if not casbin_check_permission(self.user.username, casbin_resource, action):
            user_role = self.user.role.name if self.user.role else "None"
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required permission: {action} on {resource} for tenant {tenant_id}. Your role: {user_role}"
            )

        return {
            "rbac_validated": True,
            "resource": resource,
            "action": action,
            "casbin_resource": casbin_resource
        }

    def _extract_resource_action(self) -> tuple:
        """URLとHTTPメソッドからリソース・アクションを抽出"""
        path = self.request.url.path
        method = self.request.method.lower()

        # URLからリソース名を判定
        resource = None
        if "/users" in path:
            resource = "users"
        elif "/corporations" in path:
            resource = "corporations"
        elif "/shops" in path:
            resource = "shops"
        elif "/inquiries" in path:
            resource = "inquiries"

        # HTTPメソッドからアクションを判定
        action_map = {
            "get": "read",
            "post": "create",
            "put": "update",
            "patch": "update",
            "delete": "delete"
        }

        action = action_map.get(method, "read")

        return resource, action


class ABACSecurityChecker:
    """
    属性ベースアクセス制御チェッカー
    プロジェクト固有の詳細な条件チェック
    """

    def __init__(self, user: models.User, request: Request):
        self.user = user
        self.request = request

    def check(self, tenant_context: dict, rbac_context: dict) -> dict:
        """
        追加のABAC条件チェック

        Args:
            tenant_context: TenantsSecurityCheckerからの結果
            rbac_context: RBACSecurityCheckerからの結果

        Returns:
            dict: ABAC情報のコンテキスト
        """
        # 現在は基本的なチェックのみ実装
        # 将来的に以下のような条件を追加可能：
        # - 時間制限（営業時間内のみアクセス）
        # - IP制限
        # - デバイス制限
        # - 地理的制限
        # - データ分類レベルチェック

        abac_conditions = self._check_additional_conditions()

        return {
            "abac_validated": True,
            "additional_conditions": abac_conditions
        }

    def _check_additional_conditions(self) -> dict:
        """プロジェクト固有の追加条件チェック"""
        conditions = {}

        # 例：ユーザーの状態チェック
        if not self.user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: User account is inactive"
            )
        conditions["user_active"] = True

        # 例：特定リソースへの追加制限
        # if self.request and "/sensitive-data" in self.request.url.path:
        #     # 機密データへのアクセスは特別な条件が必要
        #     pass

        return conditions