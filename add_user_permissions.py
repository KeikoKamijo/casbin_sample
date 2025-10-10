import casbin
from casbin_sqlalchemy_adapter import Adapter
from database import SQLALCHEMY_DATABASE_URL

def add_user_permissions():
    """ユーザーに直接権限を追加（ロール経由の権限とは別に）"""

    # SQLAlchemy Adapterを使用
    adapter = Adapter(SQLALCHEMY_DATABASE_URL)

    # モデル設定ファイルを使用
    enforcer = casbin.Enforcer("model.conf", adapter)

    # Aliceの直接権限（ABC Corporation内）
    alice_permissions = [
        ["Alice", "corporation_1", "users", "read"],
        ["Alice", "corporation_1", "users", "create"],
        ["Alice", "corporation_1", "users", "update"],
        ["Alice", "corporation_1", "users", "delete"],
        ["Alice", "corporation_1", "shops", "read"],
        ["Alice", "corporation_1", "shops", "create"],
        ["Alice", "corporation_1", "shops", "update"],
        ["Alice", "corporation_1", "shops", "delete"],
        ["Alice", "corporation_1", "inquiries", "read"],
        ["Alice", "corporation_1", "inquiries", "create"],
        ["Alice", "corporation_1", "inquiries", "update"],
        ["Alice", "corporation_1", "inquiries", "delete"],
    ]

    # Bobの直接権限（ABC Corporation内、読み取りのみ）
    bob_permissions = [
        ["Bob", "corporation_1", "users", "read"],
        ["Bob", "corporation_1", "shops", "read"],
        ["Bob", "corporation_1", "inquiries", "read"],
    ]

    # Daveの直接権限（DEF Corporation内）
    dave_permissions = [
        ["Dave", "corporation_2", "users", "read"],
        ["Dave", "corporation_2", "users", "create"],
        ["Dave", "corporation_2", "users", "update"],
        ["Dave", "corporation_2", "users", "delete"],
        ["Dave", "corporation_2", "shops", "read"],
        ["Dave", "corporation_2", "shops", "create"],
        ["Dave", "corporation_2", "shops", "update"],
        ["Dave", "corporation_2", "shops", "delete"],
        ["Dave", "corporation_2", "inquiries", "read"],
        ["Dave", "corporation_2", "inquiries", "create"],
        ["Dave", "corporation_2", "inquiries", "update"],
        ["Dave", "corporation_2", "inquiries", "delete"],
    ]

    # Aliceの権限を追加
    print("Adding Alice's direct permissions:")
    for perm in alice_permissions:
        enforcer.add_policy(*perm)
        print(f"  Added: {perm}")

    # Bobの権限を追加
    print("\nAdding Bob's direct permissions:")
    for perm in bob_permissions:
        enforcer.add_policy(*perm)
        print(f"  Added: {perm}")

    # Daveの権限を追加
    print("\nAdding Dave's direct permissions:")
    for perm in dave_permissions:
        enforcer.add_policy(*perm)
        print(f"  Added: {perm}")

    # ポリシーを保存
    enforcer.save_policy()
    print("\nAll user permissions have been saved to database")

    # 権限テスト
    print("\n=== Direct User Permission Tests ===")
    tests = [
        ["Alice", "corporation_1", "users", "create"],    # True
        ["Alice", "corporation_1", "shops", "delete"],    # True
        ["Alice", "corporation_2", "users", "read"],      # False (別ドメイン)
        ["Bob", "corporation_1", "users", "read"],        # True
        ["Bob", "corporation_1", "users", "create"],      # False
        ["Bob", "corporation_1", "shops", "read"],        # True
        ["Dave", "corporation_2", "users", "create"],     # True
        ["Dave", "corporation_2", "inquiries", "delete"], # True
        ["Dave", "corporation_1", "users", "read"],       # False (別ドメイン)
    ]

    for test in tests:
        result = enforcer.enforce(*test)
        print(f"enforce({test[0]}, {test[1]}, {test[2]}, {test[3]}) = {result}")

if __name__ == "__main__":
    add_user_permissions()