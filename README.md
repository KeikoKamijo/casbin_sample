# PyCasbin Authorization Sample

FastAPIとPyCasbinを使用した認可システムのサンプル実装です。

## 概要

このプロジェクトは、異なる認可モデル（RBAC、ABAC、ReBAC）の実装例を示しています。
現在の実装は主にABAC（属性ベースアクセス制御）を採用していますが、他のモデルへの拡張も可能です。

## ディレクトリ構造

```
casbin_sample/
├── main.py                 # FastAPIアプリケーションのエントリポイント
├── database.py             # データベース接続設定
├── auth.py                 # JWT認証ロジック
├── auth_dependencies.py    # 認可用の依存関数（アクセスコントローラー）
├── casbin_config.py        # Casbin設定（現在は基本設定のみ）
├── models/                 # SQLAlchemyモデル
├── schemas/                # Pydanticスキーマ
├── crud/                   # CRUD操作
├── routers/                # APIルーター
└── tests/                  # テストファイル
```

## 認可モデルの実装イメージ

### 1. RBAC (Role-Based Access Control)

役割ベースのアクセス制御。ユーザーに役割を割り当て、役割に権限を付与します。

```python
# 権限とロールの定義（本来は設定ファイルやDBで管理）
PERMISSIONS = {
    "admin": [
        "corporations:create",
        "corporations:read",
        "corporations:update",
        "corporations:delete",
        "reports:read",
        "users:manage"
    ],
    "manager": [
        "corporations:read",
        "corporations:update",
        "reports:read"
    ],
    "user": [
        "corporations:read"
    ]
}

def has_permission(user_role: str, required_permission: str) -> bool:
    """ロールが指定された権限を持っているか確認"""
    return required_permission in PERMISSIONS.get(user_role, [])

# エンドポイントでの実装例
@router.delete("/corporations/{corporation_id}")
def delete_corporation(
    corporation_id: int,
    current_user: User = Depends(get_current_user)
):
    # ロールベースで権限を確認
    if not has_permission(current_user.role, "corporations:delete"):
        raise HTTPException(status_code=403, detail="Permission denied")

    # 削除処理
    return {"message": "Deleted"}

@router.get("/reports/summary")
def get_summary_report(
    current_user: User = Depends(get_current_user)
):
    # ロールベースで権限を確認
    if not has_permission(current_user.role, "reports:read"):
        raise HTTPException(status_code=403, detail="Permission denied")

    # レポート生成
    return {"report": "..."}
```

### 2. ABAC (Attribute-Based Access Control) - 現在の実装

属性ベースのアクセス制御。ユーザーとリソースの属性を比較して権限を判定します。

```python
# ユーザーモデルの属性
class User(Base):
    id = Column(Integer, primary_key=True)
    username = Column(String)
    corporation_id = Column(Integer)  # 所属法人
    department = Column(String)       # 部署
    is_active = Column(Boolean)       # アクティブ状態

# エンドポイントでの実装例
@router.get("/corporations/{corporation_id}")
def read_corporation(
    corporation_id: int,
    current_user: User = Depends(get_current_user)
):
    # ユーザーの所属法人属性で判定
    if current_user.corporation_id != corporation_id:
        raise HTTPException(status_code=403, detail="Access denied")

    return get_corporation(corporation_id)

@router.put("/users/{user_id}/salary")
def update_salary(
    user_id: int,
    salary: float,
    current_user: User = Depends(get_current_user)
):
    # 複数の属性で判定（人事部かつアクティブユーザー）
    if current_user.department != "HR" or not current_user.is_active:
        raise HTTPException(status_code=403, detail="HR department only")

    return update_user_salary(user_id, salary)
```

### 3. ReBAC (Relationship-Based Access Control)

関係性ベースのアクセス制御。エンティティ間の関係を基に権限を判定します。

```python
# 関係性を表すモデル
class ProjectMember(Base):
    project_id = Column(Integer)
    user_id = Column(Integer)
    role = Column(String)  # "owner", "member", "viewer"

class TeamHierarchy(Base):
    parent_team_id = Column(Integer)
    child_team_id = Column(Integer)

# エンドポイントでの実装例
@router.get("/projects/{project_id}/documents")
def get_project_documents(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # プロジェクトメンバーかどうかを関係性で判定
    membership = db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == current_user.id
    ).first()

    if not membership:
        raise HTTPException(status_code=403, detail="Not a project member")

    return get_documents(project_id)

@router.delete("/projects/{project_id}")
def delete_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # オーナーのみ削除可能（関係性とロールの組み合わせ）
    ownership = db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == current_user.id,
        ProjectMember.role == "owner"
    ).first()

    if not ownership:
        raise HTTPException(status_code=403, detail="Only owner can delete")

    return delete_project_data(project_id)
```

### 認可モデルの比較

| モデル | 判定基準 | 使用場面 | 例 |
|--------|----------|----------|-----|
| RBAC | ユーザーの役割 | 固定的な権限階層がある場合 | 管理者のみ削除可能 |
| ABAC | ユーザーやリソースの属性 | 動的な条件判定が必要な場合 | 所属法人のデータのみ閲覧可能 |
| ReBAC | エンティティ間の関係 | 複雑な組織構造やプロジェクト管理 | プロジェクトメンバーのみアクセス可能 |

## エンドポイントでの使い方

### 1. 認証（ログイン）

```bash
# ログインしてトークンを取得
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "password": "alicepass"}'

# レスポンス
{
  "access_token": "alice",
  "token_type": "bearer"
}
```

### 2. 認可付きエンドポイントへのアクセス

```python
# routers/corporations.py での使用例
@router.get("/{corporation_id}",
    response_model=schemas.Corporation,
    dependencies=[Depends(security)])
def read_corporation(
    corporation_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_corporation_access_checker)
):
    """
    法人詳細を取得
    get_corporation_access_checkerが自動的に権限チェックを実行
    """
    # current_userは権限チェックを通過したユーザー
    db_corporation = crud.get_corporation(db, corporation_id=corporation_id)
    return db_corporation
```

### 3. 汎用アクセスコントローラーの使用

```python
from auth_dependencies import access_controller

# 任意のエンドポイントで使用可能
@router.get("/{resource_id}")
def get_resource(
    resource_id: int,
    current_user: models.User = Depends(access_controller)
):
    # access_controllerが自動的にpath parameterを判定して
    # 適切な権限チェックを実行
    pass
```

## 権限チェックの流れ

1. **認証**: Bearer tokenからユーザーを特定
2. **パラメータ抽出**: URLのpath parameterから対象リソースIDを取得
3. **権限判定**: ユーザーの属性とリソースIDを比較
4. **アクセス制御**: 権限がない場合は403エラー、ある場合は処理継続

## テスト用ユーザー

- **Alice** (username: alice, password: alicepass)
  - 所属: ABC Corporation (ID: 1)
  - アクセス可能: /corporations/1/* のリソース

- **Dave** (username: dave, password: davepass)
  - 所属: DEF Corporation (ID: 2)
  - アクセス可能: /corporations/2/* のリソース

## テストの実行

```bash
# 認可テスト
pytest test_auth_dependencies.py -v

# 統合テスト
pytest test_authorization.py -v
```

## 今後の拡張

- Casbinのポリシーファイル（.csv）による動的な権限管理
- RBACモデルの実装（管理者、一般ユーザーなどの役割）
- ReBACモデルの実装（組織階層、チーム所属などの関係性）
- 権限の継承とデリゲーション
- 時間ベースのアクセス制御
- リソース固有の詳細な権限設定