import casbin
from casbin_sqlalchemy_adapter import Adapter
from database import SQLALCHEMY_DATABASE_URL

def add_role_inheritance():
    """ロールの継承関係を追加（adminはaccountantの権限も継承）"""

    # SQLAlchemy Adapterを使用
    adapter = Adapter(SQLALCHEMY_DATABASE_URL)

    # モデル設定ファイルを使用
    enforcer = casbin.Enforcer("model.conf", adapter)

    # ロールの継承関係を追加
    # adminロールはaccountantロールの権限を継承
    # g = sub, role, domain の形式で、adminがaccountantを継承

    # ABC Corporation (corporation_1) でのロール継承
    enforcer.add_grouping_policy("admin", "accountant", "corporation_1")
    print("Added role inheritance: admin inherits accountant in corporation_1")

    # DEF Corporation (corporation_2) でのロール継承
    enforcer.add_grouping_policy("admin", "accountant", "corporation_2")
    print("Added role inheritance: admin inherits accountant in corporation_2")

    # ポリシーを保存
    enforcer.save_policy()
    print("\nRole inheritance has been saved to database")

    # 権限テスト（継承を含む）
    print("\n=== Permission Tests with Inheritance ===")
    tests = [
        # Aliceのテスト（ABC Corporationのadmin）
        ["Alice", "corporation_1", "users", "create"],    # True (admin権限)
        ["Alice", "corporation_1", "users", "read"],      # True (admin権限)
        ["Alice", "corporation_1", "shops", "read"],      # True (accountantから継承)
        ["Alice", "corporation_2", "users", "read"],      # False (別ドメイン)

        # Bobのテスト（ABC Corporationのaccountant）
        ["Bob", "corporation_1", "users", "read"],        # True (accountant権限)
        ["Bob", "corporation_1", "users", "create"],      # False (accountantは作成不可)
        ["Bob", "corporation_1", "shops", "read"],        # True (accountant権限)

        # Daveのテスト（DEF Corporationのadmin）
        ["Dave", "corporation_2", "users", "create"],     # True (admin権限)
        ["Dave", "corporation_2", "shops", "read"],       # True (accountantから継承)
        ["Dave", "corporation_1", "users", "read"],       # False (別ドメイン)
    ]

    for test in tests:
        result = enforcer.enforce(*test)
        print(f"enforce({test[0]}, {test[1]}, {test[2]}, {test[3]}) = {result}")

    # 現在の全ポリシーを表示
    print("\n=== Current Grouping Policies (Role Assignments & Inheritance) ===")
    grouping_policy = enforcer.get_grouping_policy()
    for policy in grouping_policy:
        if len(policy) >= 3:
            if policy[0] in ["Alice", "Bob", "Dave"]:
                print(f"User Assignment: {policy[0]} -> {policy[1]} in {policy[2]}")
            else:
                print(f"Role Inheritance: {policy[0]} inherits {policy[1]} in {policy[2]}")

if __name__ == "__main__":
    add_role_inheritance()