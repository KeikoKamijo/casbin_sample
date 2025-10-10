import casbin
from casbin_sqlalchemy_adapter import Adapter
from database import SQLALCHEMY_DATABASE_URL, SessionLocal
import models

def setup_casbin_policies():
    """Casbinのドメインベースポリシーを設定"""

    # SQLAlchemy Adapterを使用
    adapter = Adapter(SQLALCHEMY_DATABASE_URL)

    # モデル設定ファイルを使用
    enforcer = casbin.Enforcer("model.conf", adapter)

    # 既存のポリシーをクリア
    enforcer.clear_policy()
    enforcer.remove_grouping_policy()

    db = SessionLocal()

    try:
        # ユーザーとロールの割り当てを設定
        alice = db.query(models.User).filter_by(username="Alice").first()
        bob = db.query(models.User).filter_by(username="Bob").first()
        dave = db.query(models.User).filter_by(username="Dave").first()

        admin_role = db.query(models.Role).filter_by(name="admin").first()
        accountant_role = db.query(models.Role).filter_by(name="accountant").first()

        # AliceをABC Corporationのadminに
        if alice and admin_role:
            alice.role_id = admin_role.id
            db.commit()
            print(f"Assigned admin role to Alice")

        # BobをABC Corporationのaccountantに
        if bob and accountant_role:
            bob.role_id = accountant_role.id
            db.commit()
            print(f"Assigned accountant role to Bob")

        # DaveをDEF Corporationのadminに
        if dave and admin_role:
            dave.role_id = admin_role.id
            db.commit()
            print(f"Assigned admin role to Dave")

        # ドメイン(Corporation)ベースのポリシーを追加
        # ABC Corporation (domain: corporation_1)
        abc_policies = [
            # adminロールの権限
            ["admin", "corporation_1", "users", "read"],
            ["admin", "corporation_1", "users", "create"],
            ["admin", "corporation_1", "users", "update"],
            ["admin", "corporation_1", "users", "delete"],
            ["admin", "corporation_1", "shops", "read"],
            ["admin", "corporation_1", "shops", "create"],
            ["admin", "corporation_1", "shops", "update"],
            ["admin", "corporation_1", "shops", "delete"],
            ["admin", "corporation_1", "inquiries", "read"],
            ["admin", "corporation_1", "inquiries", "create"],
            ["admin", "corporation_1", "inquiries", "update"],
            ["admin", "corporation_1", "inquiries", "delete"],

            # accountantロールの権限
            ["accountant", "corporation_1", "users", "read"],
            ["accountant", "corporation_1", "shops", "read"],
            ["accountant", "corporation_1", "inquiries", "read"],
        ]

        # DEF Corporation (domain: corporation_2)
        def_policies = [
            # adminロールの権限
            ["admin", "corporation_2", "users", "read"],
            ["admin", "corporation_2", "users", "create"],
            ["admin", "corporation_2", "users", "update"],
            ["admin", "corporation_2", "users", "delete"],
            ["admin", "corporation_2", "shops", "read"],
            ["admin", "corporation_2", "shops", "create"],
            ["admin", "corporation_2", "shops", "update"],
            ["admin", "corporation_2", "shops", "delete"],
            ["admin", "corporation_2", "inquiries", "read"],
            ["admin", "corporation_2", "inquiries", "create"],
            ["admin", "corporation_2", "inquiries", "update"],
            ["admin", "corporation_2", "inquiries", "delete"],

            # accountantロールの権限
            ["accountant", "corporation_2", "users", "read"],
            ["accountant", "corporation_2", "shops", "read"],
            ["accountant", "corporation_2", "inquiries", "read"],
        ]

        # ポリシーを追加
        for policy in abc_policies:
            enforcer.add_policy(*policy)
            print(f"Added policy: {policy}")

        for policy in def_policies:
            enforcer.add_policy(*policy)
            print(f"Added policy: {policy}")

        # ユーザーのロール割り当て (g = user, role, domain)
        user_role_assignments = [
            ["Alice", "admin", "corporation_1"],     # AliceはABC Corporationのadmin
            ["Bob", "accountant", "corporation_1"],   # BobはABC Corporationのaccountant
            ["Dave", "admin", "corporation_2"],       # DaveはDEF Corporationのadmin
        ]

        for assignment in user_role_assignments:
            enforcer.add_grouping_policy(*assignment)
            print(f"Added role assignment: {assignment}")

        # ポリシーを保存
        enforcer.save_policy()
        print("\nAll policies have been saved to database")

        # 権限テスト
        print("\n=== Permission Tests ===")
        tests = [
            ["Alice", "corporation_1", "users", "create"],    # Should be True
            ["Alice", "corporation_2", "users", "create"],    # Should be False (different domain)
            ["Bob", "corporation_1", "users", "read"],       # Should be True
            ["Bob", "corporation_1", "users", "create"],     # Should be False (accountant can't create)
            ["Dave", "corporation_2", "users", "create"],    # Should be True
            ["Dave", "corporation_1", "users", "create"],    # Should be False (different domain)
        ]

        for test in tests:
            result = enforcer.enforce(*test)
            print(f"enforce({test[0]}, {test[1]}, {test[2]}, {test[3]}) = {result}")

    finally:
        db.close()

if __name__ == "__main__":
    setup_casbin_policies()
