import casbin
from casbin_sqlalchemy_adapter import Adapter
from database import SQLALCHEMY_DATABASE_URL
from database import SessionLocal
import models

# CasbinのRBACモデル定義
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
    """RBACポリシーを設定"""


    # データベースセッション作成
    db = SessionLocal()

    try:
        # ロールベースの権限定義
        role_policies = [
            # 管理者の権限
            ("admin", "users", "read"),
            ("admin", "users", "create"),
            ("admin", "users", "update"),
            ("admin", "users", "delete"),
            ("admin", "corporations", "read"),
            ("admin", "corporations", "create"),
            ("admin", "corporations", "update"),
            ("admin", "corporations", "delete"),
            ("admin", "shops", "read"),
            ("admin", "shops", "create"),
            ("admin", "shops", "update"),
            ("admin", "shops", "delete"),
            ("admin", "inquiries", "read"),
            ("admin", "inquiries", "create"),
            ("admin", "inquiries", "update"),
            ("admin", "inquiries", "delete"),

            # 経理の権限
            # ("accountant", "corporations", "read"),  # 法人詳細は経理からアクセス不可
            ("accountant", "users", "read"),           # ユーザー情報の閲覧
            # inquiriesは経理からアクセス不可（adminのみ）
        ]

        # マルチテナント対応：ユーザーごとにテナント固有のポリシーを生成
        user_roles_query = db.query(
            models.User.username,
            models.User.corporation_id,
            models.Role.name.label('role_name')
        ).join(
            models.Role, models.User.role_id == models.Role.id
        ).filter(
            models.User.role_id.isnot(None),
            models.User.corporation_id.isnot(None)
        ).all()

        # ユーザーごとにマルチテナント対応のポリシーを生成
        for user_role in user_roles_query:
            username = user_role.username
            corporation_id = user_role.corporation_id
            role_name = user_role.role_name

            # 該当ロールの権限を取得してマルチテナント形式で追加
            for role, obj, act in role_policies:
                if role == role_name:
                    # corporation:{tenant_id}:{resource} 形式でポリシー追加
                    tenant_resource = f"corporation:{corporation_id}:{obj}"
                    enforcer.add_policy(username, tenant_resource, act)
                    print(f"Added policy: {username} -> {tenant_resource} -> {act}")

            # ユーザーのロール割り当ても追加（互換性のため）
            enforcer.add_grouping_policy(username, role_name)
            print(f"Assigned role '{role_name}' to user '{username}' (tenant: {corporation_id})")

        # ポリシーを保存
        enforcer.save_policy()

    finally:
        db.close()


def sync_user_roles_to_casbin():
    """データベースのユーザーロール情報をCasbinと同期"""
    from sqlalchemy.orm import Session
    from database import SessionLocal
    import models

    enforcer = get_casbin_enforcer()
    db = SessionLocal()

    try:
        # 現在のグルーピングポリシーをすべて削除
        enforcer.clear_grouping_policy()

        # データベースから最新のユーザーロール情報を取得
        user_roles_query = db.query(
            models.User.username,
            models.Role.name.label('role_name')
        ).join(
            models.Role, models.User.role_id == models.Role.id
        ).filter(
            models.User.role_id.isnot(None)
        ).all()

        # 最新のユーザーロール割り当てを追加
        for user_role in user_roles_query:
            enforcer.add_grouping_policy(user_role.username, user_role.role_name)

        # ポリシーを保存
        enforcer.save_policy()
        return True

    except Exception as e:
        print(f"Error syncing user roles to Casbin: {e}")
        return False
    finally:
        db.close()


def check_corporation_access(user_id: int, corporation_id: int, action: str, enforcer: casbin.Enforcer) -> bool:
    """法人アクセス権限をチェック"""
    # ユーザーの所属法人IDと、リクエストされた法人IDが一致するかチェック
    # これは後でget_current_userから取得したユーザー情報と比較する

    # Casbinでの権限チェック
    subject = f"user:{user_id}"
    object_name = f"corporation:{corporation_id}"

    return enforcer.enforce(subject, object_name, action)