import casbin
from casbin_sqlalchemy_adapter import Adapter
from database import SQLALCHEMY_DATABASE_URL

# Casbinポリシー設定
CASBIN_MODEL = """
[request_definition]
r = sub, obj, act

[policy_definition]
p = sub, obj, act

[role_definition]
g = _, _

[policy_effect]
e = some(where (p.eft == allow))

[matchers]
m = g(r.sub, p.sub) && r.obj == p.obj && r.act == p.act
"""


def get_casbin_enforcer():
    """Casbinエンフォーサーを取得"""
    # SQLAlchemy Adapterを使用してポリシーをデータベースに保存
    adapter = Adapter(SQLALCHEMY_DATABASE_URL)

    # モデル設定を文字列から作成
    with open("model.conf", "w") as f:
        f.write(CASBIN_MODEL)

    # エンフォーサーを作成
    enforcer = casbin.Enforcer("model.conf", adapter)

    # 初期ポリシーを設定
    setup_initial_policies(enforcer)

    return enforcer


def setup_initial_policies(enforcer: casbin.Enforcer):
    """初期ポリシーを設定"""
    # 基本的なポリシー例
    # ユーザーは自分の所属法人の詳細を取得できる
    policies = [
        # フォーマット: (subject, object, action)
        ("corporation_member", "corporation", "read"),
        ("corporation_admin", "corporation", "read"),
        ("corporation_admin", "corporation", "write"),
        ("corporation_admin", "corporation", "delete"),
    ]

    for policy in policies:
        enforcer.add_policy(*policy)

    # 初期ロール設定例
    # enforcer.add_grouping_policy("user:1", "corporation_member")

    # ポリシーを保存
    enforcer.save_policy()


def check_corporation_access(user_id: int, corporation_id: int, action: str, enforcer: casbin.Enforcer) -> bool:
    """法人アクセス権限をチェック"""
    # ユーザーの所属法人IDと、リクエストされた法人IDが一致するかチェック
    # これは後でget_current_userから取得したユーザー情報と比較する

    # Casbinでの権限チェック
    subject = f"user:{user_id}"
    object_name = f"corporation:{corporation_id}"

    return enforcer.enforce(subject, object_name, action)