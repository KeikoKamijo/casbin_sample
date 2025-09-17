"""
AuthorizationManager
"""
from fastapi import Depends, Request
import models
from auth import get_current_user
from security_checkers import TenantsSecurityChecker, RBACSecurityChecker, ABACSecurityChecker


class AuthorizationManager:
    """
    セキュリティチェックの神クラス

    必須順序でのセキュリティチェックを保証：
    1. マルチテナント制御（最優先・忘れてはいけない）
    2. RBAC権限制御
    3. 追加ABAC条件
    """

    def __init__(self, request: Request, user: models.User):
        self.request = request
        self.user = user

        # 各チェッカーを初期化（責務分離）
        self.tenant_checker = TenantsSecurityChecker(user, request)
        self.rbac_checker = RBACSecurityChecker(user, request)
        self.abac_checker = ABACSecurityChecker(user, request)

        # コンテキスト情報を保存
        self.security_context = {
            "stages_completed": [],
            "tenant_context": {},
            "rbac_context": {},
            "abac_context": {}
        }

    def authorize(self) -> bool:
        """
        階層的セキュリティチェックの実行

        必須順序：
        1. テナント制御 → 2. RBAC → 3. ABAC

        Returns:
            bool: True=allow, False=deny
        """
        try:

            # Stage 1: マルチテナント制御
            self._execute_tenant_check()

            # Stage 2: RBAC権限制御
            self._execute_rbac_check()

            # Stage 3: 追加ABAC条件
            self._execute_abac_check()

            # 全チェック完了
            self.security_context["authorization_successful"] = True
            return True

        except Exception as e:
            # セキュリティ違反の詳細ログ（本番環境では適切なログシステムに）
            self._log_security_violation(e)
            return False

    def _execute_tenant_check(self):
        """Stage 1: マルチテナント制御実行"""
        tenant_context = self.tenant_checker.check()
        self.security_context["tenant_context"] = tenant_context
        self.security_context["stages_completed"].append("tenant")

    def _execute_rbac_check(self):
        """Stage 2: RBAC権限制御実行"""
        if "tenant" not in self.security_context["stages_completed"]:
            raise SecurityError("Internal error: Tenant check must be completed before RBAC")

        rbac_context = self.rbac_checker.check(self.security_context["tenant_context"])
        self.security_context["rbac_context"] = rbac_context
        self.security_context["stages_completed"].append("rbac")

    def _execute_abac_check(self):
        """Stage 3: ABAC条件チェック実行"""
        required_stages = ["tenant", "rbac"]
        for stage in required_stages:
            if stage not in self.security_context["stages_completed"]:
                raise SecurityError(f"Internal error: {stage} check must be completed before ABAC")

        abac_context = self.abac_checker.check(
            self.security_context["tenant_context"],
            self.security_context["rbac_context"]
        )
        self.security_context["abac_context"] = abac_context
        self.security_context["stages_completed"].append("abac")

    def _log_security_violation(self, exception: Exception):
        """セキュリティ違反のログ記録"""
        log_info = {
            "user_id": self.user.id,
            "username": self.user.username,
            "corporation_id": self.user.corporation_id,
            "user_role": self.user.role.name if self.user.role else None,
            "request_path": self.request.url.path,
            "request_method": self.request.method,
            "stages_completed": self.security_context["stages_completed"],
            "error": str(exception),
            "error_type": type(exception).__name__
        }

        # 本番環境では適切なログシステム（CloudWatch、ELK Stack等）に送信
        print(f"Security Violation: {log_info}")

    def get_security_context(self) -> dict:
        """セキュリティコンテキスト情報を取得（デバッグ・監査用）"""
        return self.security_context.copy()


class SecurityError(Exception):
    """セキュリティチェックの内部エラー"""
    pass


# FastAPIの依存性注入用の関数
def authorization_manager(
    request: Request,
    current_user: models.User = Depends(get_current_user)
) -> bool:
    """
    FastAPI依存性注入用の認可チェック関数

    Args:
        request: FastAPIのRequestオブジェクト
        current_user: 認証済みユーザー（get_current_userから）

    Returns:
        bool: True=allow, False=deny
    """
    manager = AuthorizationManager(request, current_user)
    return manager.authorize()