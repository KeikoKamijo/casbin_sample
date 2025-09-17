#!/usr/bin/env python3

from casbin_config import get_casbin_enforcer


def main():
    """Casbinポリシーを初期化"""
    print("Setting up Casbin RBAC policies...")

    # エンフォーサーを取得（自動的に初期ポリシーが設定される）
    enforcer = get_casbin_enforcer()

    print("\n=== 設定されたロール権限 ===")
    policies = enforcer.get_policy()
    for policy in policies:
        print(f"Role: {policy[0]} -> Resource: {policy[1]} -> Action: {policy[2]}")

    print("\n=== ユーザーのロール割り当て ===")
    grouping_policies = enforcer.get_grouping_policy()
    for grouping in grouping_policies:
        print(f"User: {grouping[0]} -> Role: {grouping[1]}")

    # テスト実行
    print("\n=== 権限テスト ===")
    test_cases = [
        ("alice", "users", "delete"),      # 管理者 -> OK
        ("bob", "users", "delete"),        # 経理 -> NG
        ("bob", "corporations", "read"),   # 経理 -> OK
        ("dave", "schools", "create"),     # 管理者 -> OK
        ("bob", "inquiries", "update"),    # 経理 -> OK
    ]

    for user, resource, action in test_cases:
        result = enforcer.enforce(user, resource, action)
        status = "✅ ALLOWED" if result else "❌ DENIED"
        print(f"{user} -> {action} {resource}: {status}")

    print("\nCasbin RBAC setup complete!")


if __name__ == "__main__":
    main()