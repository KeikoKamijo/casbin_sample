import pytest
from unittest.mock import Mock
from fastapi import HTTPException, Request
import models
from auth_dependencies import (
    verify_corporation_access_service,
    verify_user_access_service,
    get_corporation_access_checker,
    get_user_access_checker
)


class TestCorporationAccessService:
    """法人アクセス権限サービス関数のテスト"""

    def test_verify_corporation_access_service_success(self):
        """同一法人のアクセスは成功"""
        # モックユーザー作成（法人ID: 1）
        user = Mock(spec=models.User)
        user.corporation_id = 1

        # 同一法人IDでテスト（例外が発生しないことを確認）
        try:
            verify_corporation_access_service(user, 1)
        except HTTPException:
            pytest.fail("verify_corporation_access_service raised HTTPException unexpectedly")

    def test_verify_corporation_access_service_forbidden(self):
        """異なる法人のアクセスは403エラー"""
        # モックユーザー作成（法人ID: 1）
        user = Mock(spec=models.User)
        user.corporation_id = 1

        # 異なる法人IDでテスト
        with pytest.raises(HTTPException) as exc_info:
            verify_corporation_access_service(user, 2)

        assert exc_info.value.status_code == 403
        assert "Access denied" in exc_info.value.detail

    def test_verify_corporation_access_service_none_corporation_id(self):
        """corporation_idがNoneの場合は403エラー"""
        user = Mock(spec=models.User)
        user.corporation_id = None

        with pytest.raises(HTTPException) as exc_info:
            verify_corporation_access_service(user, 1)

        assert exc_info.value.status_code == 403


class TestUserAccessService:
    """ユーザーアクセス権限サービス関数のテスト"""

    def test_verify_user_access_service_success(self):
        """自分自身のアクセスは成功"""
        # モックユーザー作成（ユーザーID: 1）
        user = Mock(spec=models.User)
        user.id = 1

        # 同一ユーザーIDでテスト（例外が発生しないことを確認）
        try:
            verify_user_access_service(user, 1)
        except HTTPException:
            pytest.fail("verify_user_access_service raised HTTPException unexpectedly")

    def test_verify_user_access_service_forbidden(self):
        """他のユーザーのアクセスは403エラー"""
        # モックユーザー作成（ユーザーID: 1）
        user = Mock(spec=models.User)
        user.id = 1

        # 異なるユーザーIDでテスト
        with pytest.raises(HTTPException) as exc_info:
            verify_user_access_service(user, 2)

        assert exc_info.value.status_code == 403
        assert "You can only access your own data" in exc_info.value.detail


class TestCorporationAccessChecker:
    """法人アクセス権限チェッカーのテスト"""

    def test_get_corporation_access_checker_success(self):
        """正常なcorporation_idでアクセス成功"""
        # モックリクエスト作成
        request = Mock(spec=Request)
        request.path_params = {"corporation_id": "1"}

        # モックユーザー作成（法人ID: 1）
        user = Mock(spec=models.User)
        user.corporation_id = 1

        # テスト実行
        result = get_corporation_access_checker(request, user)
        assert result == user

    def test_get_corporation_access_checker_forbidden(self):
        """異なる法人IDで403エラー"""
        # モックリクエスト作成
        request = Mock(spec=Request)
        request.path_params = {"corporation_id": "2"}

        # モックユーザー作成（法人ID: 1）
        user = Mock(spec=models.User)
        user.corporation_id = 1

        # テスト実行
        with pytest.raises(HTTPException) as exc_info:
            get_corporation_access_checker(request, user)

        assert exc_info.value.status_code == 403

    def test_get_corporation_access_checker_missing_param(self):
        """corporation_idがpath parameterにない場合は400エラー"""
        # モックリクエスト作成（corporation_idなし）
        request = Mock(spec=Request)
        request.path_params = {}

        # モックユーザー作成
        user = Mock(spec=models.User)
        user.corporation_id = 1

        # テスト実行
        with pytest.raises(HTTPException) as exc_info:
            get_corporation_access_checker(request, user)

        assert exc_info.value.status_code == 400
        assert "Corporation ID not found in path" in exc_info.value.detail

    def test_get_corporation_access_checker_invalid_format(self):
        """corporation_idが数値でない場合は400エラー"""
        # モックリクエスト作成（無効な形式）
        request = Mock(spec=Request)
        request.path_params = {"corporation_id": "invalid"}

        # モックユーザー作成
        user = Mock(spec=models.User)
        user.corporation_id = 1

        # テスト実行
        with pytest.raises(HTTPException) as exc_info:
            get_corporation_access_checker(request, user)

        assert exc_info.value.status_code == 400
        assert "Invalid corporation ID format" in exc_info.value.detail


class TestUserAccessChecker:
    """ユーザーアクセス権限チェッカーのテスト"""

    def test_get_user_access_checker_success(self):
        """正常なuser_idでアクセス成功"""
        # モックリクエスト作成
        request = Mock(spec=Request)
        request.path_params = {"user_id": "1"}

        # モックユーザー作成（ユーザーID: 1）
        user = Mock(spec=models.User)
        user.id = 1

        # テスト実行
        result = get_user_access_checker(request, user)
        assert result == user

    def test_get_user_access_checker_forbidden(self):
        """異なるユーザーIDで403エラー"""
        # モックリクエスト作成
        request = Mock(spec=Request)
        request.path_params = {"user_id": "2"}

        # モックユーザー作成（ユーザーID: 1）
        user = Mock(spec=models.User)
        user.id = 1

        # テスト実行
        with pytest.raises(HTTPException) as exc_info:
            get_user_access_checker(request, user)

        assert exc_info.value.status_code == 403

    def test_get_user_access_checker_missing_param(self):
        """user_idがpath parameterにない場合は400エラー"""
        # モックリクエスト作成（user_idなし）
        request = Mock(spec=Request)
        request.path_params = {}

        # モックユーザー作成
        user = Mock(spec=models.User)
        user.id = 1

        # テスト実行
        with pytest.raises(HTTPException) as exc_info:
            get_user_access_checker(request, user)

        assert exc_info.value.status_code == 400
        assert "User ID not found in path" in exc_info.value.detail

    def test_get_user_access_checker_invalid_format(self):
        """user_idが数値でない場合は400エラー"""
        # モックリクエスト作成（無効な形式）
        request = Mock(spec=Request)
        request.path_params = {"user_id": "invalid"}

        # モックユーザー作成
        user = Mock(spec=models.User)
        user.id = 1

        # テスト実行
        with pytest.raises(HTTPException) as exc_info:
            get_user_access_checker(request, user)

        assert exc_info.value.status_code == 400
        assert "Invalid user ID format" in exc_info.value.detail


if __name__ == "__main__":
    pytest.main([__file__, "-v"])