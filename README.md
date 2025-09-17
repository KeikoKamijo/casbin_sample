# PyCasbin Multi-Tenant Authorization System

FastAPIとPyCasbinを使用したマルチテナント対応RBAC認可システムの実装です。

## 🏗️ システムアーキテクチャ

階層的セキュリティチェックを強制実行する「AuthorizationManager（神クラス）」により、マルチテナント制御の忘れを防止します。

```
リクエスト → 認証(JWT) → AuthorizationManager → エンドポイント処理
                            ├── Stage 1: マルチテナント制御（最優先）
                            ├── Stage 2: RBAC権限制御（Casbin）
                            └── Stage 3: 追加ABAC条件
```

## 📁 ディレクトリ構造（認可システム関連）

```
casbin_sample/
├── 🔐 認可システムコア
│   ├── authorization_manager.py    # 神クラス：階層的セキュリティチェック統合管理
│   ├── security_checkers.py        # 責務分離されたセキュリティチェッカー群
│   │   ├── TenantsSecurityChecker  # マルチテナント制御
│   │   ├── RBACSecurityChecker     # Casbin RBAC権限制御
│   │   └── ABACSecurityChecker     # 追加属性ベース条件
│   └── casbin_config.py            # Casbinポリシー設定・マルチテナント対応
│
├── 🔑 認証・認可補助
│   ├── auth.py                     # JWT認証ロジック
│   ├── auth_dependencies.py        # レガシー認可依存関数（非推奨）
│   ├── casbin_dependencies.py      # Casbin専用依存関数（非推奨）
│   ├── casbin_rbac_auth.py         # Casbin権限チェック関数
│   └── model.conf                  # Casbin RBACモデル定義
│
├── 📊 データモデル
│   ├── models/
│   │   ├── users.py                # ユーザーモデル（role_id追加）
│   │   ├── roles.py                # ロールモデル（admin, accounting）
│   │   └── corporations.py         # 法人モデル（マルチテナント）
│   └── casbin_rule                 # Casbinポリシーデータベーステーブル
│
└── 🌐 APIエンドポイント
    └── routers/
        ├── inquiries.py             # 問い合わせ（管理者のみアクセス可）
        └── corporations.py          # 法人詳細（管理者のみ、経理はアクセス不可）
```

## 🛡️ セキュリティアーキテクチャ詳細

### AuthorizationManager（神クラス）

全セキュリティチェックを必須順序で実行し、マルチテナント制御の忘れを防止：

```python
class AuthorizationManager:
    def authorize(self) -> models.User:
        # Stage 1: マルチテナント制御（最優先・忘れ防止）
        self._execute_tenant_check()

        # Stage 2: RBAC権限制御
        self._execute_rbac_check()

        # Stage 3: 追加ABAC条件
        self._execute_abac_check()

        return self.user
```

### マルチテナントポリシー生成

各ユーザーのテナント（法人）ごとに自動的にポリシーを生成：

```python
# Casbinポリシー形式: corporation:{tenant_id}:{resource}
"alice" → "corporation:1:inquiries" → "read"
"dave" → "corporation:2:inquiries" → "read"
"bob" → "corporation:1:users" → "read"
```

## 🔒 実装された権限制御

### ロール権限マトリックス

| ロール | inquiries | corporations詳細 | users | schools |
|--------|-----------|-----------------|-------|---------|
| admin | ✅ 全CRUD | ✅ 全CRUD | ✅ 全CRUD | ✅ 全CRUD |
| accounting | ❌ アクセス不可 | ❌ 読取不可<br>✅ 更新のみ | ✅ 読取のみ | ❌ アクセス不可 |

### マルチテナント分離

- 各ユーザーは自分の所属法人（corporation_id）のデータのみアクセス可能
- 他法人のデータは存在しないかのように動作（"Not found"エラー）
- URLパスパラメータとデータフィルタリングの二重防御

## 🚀 使用方法

### 1. 認証（ログイン）

```bash
# ログインしてトークンを取得
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "password": "password"}'
```

### 2. 認可付きエンドポイントへのアクセス

```python
# エンドポイントでの使用例
from authorization_manager import authorization_manager

@router.get("/inquiries/", response_model=List[schemas.Inquiry])
def read_inquiries(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(authorization_manager)  # 神クラス使用
):
    # マルチテナント対応：自動的にユーザーの法人でフィルタリング
    inquiries = crud.get_inquiries(
        db,
        corporation_id=current_user.corporation_id
    )
    return inquiries
```

### 3. セキュリティ違反のログ

```json
{
  "user_id": 3,
  "username": "bob",
  "corporation_id": 1,
  "user_role": "accounting",
  "request_path": "/inquiries/",
  "stages_completed": ["tenant"],
  "error": "Access denied. Required permission: read on inquiries"
}
```

## 👥 テストユーザー

| ユーザー | パスワード | ロール | 所属法人 | corporation_id |
|----------|-----------|--------|----------|----------------|
| alice | password | admin | ABC Corporation | 1 |
| dave | password | admin | DEF Corporation | 2 |
| bob | password | accounting | ABC Corporation | 1 |

## 🧪 テスト例

```bash
# Alice（管理者）: 自法人の問い合わせアクセス ✅
curl -H "Authorization: Bearer alice" http://localhost:8000/inquiries/

# Bob（経理）: 問い合わせアクセス拒否 ❌
curl -H "Authorization: Bearer bob" http://localhost:8000/inquiries/
# → {"detail": "Access denied. Required permission: read on inquiries"}

# Dave（管理者）: 他法人データアクセス拒否 ❌
curl -H "Authorization: Bearer dave" http://localhost:8000/corporations/1
# → {"detail": "Access denied: You can only access corporation 2 data"}
```

## 📈 システムの特長

1. **マルチテナント完全分離**: 法人間のデータ完全隔離
2. **階層的セキュリティ**: 3段階の必須チェック
3. **忘れ防止設計**: 神クラスによる強制実行
4. **責務分離**: 各チェッカークラスが独立
5. **詳細なログ**: セキュリティ違反の完全記録
6. **Casbin統合**: ポリシーベースの柔軟な権限管理

## 🔧 今後の拡張

- [ ] スーパー管理者ロール（全法人アクセス）
- [ ] 時間ベースアクセス制御
- [ ] IP制限・地理的制限
- [ ] 権限の委譲機能
- [ ] 監査ログのElasticsearch連携
- [ ] WebUIでのポリシー管理画面