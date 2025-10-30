# 認可の実装のイメージ確認

## 参加者の目線合わせ
### 認可モデル
#### RBAC

```python
# 1. ユーザー（User）
user = {
    "username": "alice",
    "role": "admin"
}

# 2. ロール別権限（Role-based Permissions）
role_permissions = {
    "admin": {
        "users": ["read", "create", "update", "delete"],
        "shops": ["read", "create", "update", "delete"],
        "inquiries": ["read", "create", "update", "delete"],
        "corporations": ["read", "create", "update", "delete"]
    },
    "accountant": {
        "users": ["read"],
        "shops": [],  # アクセス不可
        "inquiries": [],  # アクセス不可
        "corporations": []  # アクセス不可
    }
}



```

#### ABACとは

- ユーザー、リソース、環境の様々な**属性（Attribute）**を評価

```python
# Userオブジェクトの例（多様な属性を持つ）

user = {
    "username": "alice",
    "role": "admin",
    "corporation_id": 1,
    "employment_date": "2020-01-01",
    "region": "tokyo",
    "security_clearance": "confidential",
    "is_temporary": False
}

context = {
    "classification": "confidential",
}

## 判定条件
user.employment_date < xxx
user.is_temporary == true

print(check_abac_permission(alice, "financial_reports", "read", context))  # True
print(check_abac_permission(alice, "sensitive_data", "read", context))     # True（雇用日OK）

- **RBACはABACの一種**
- 「role属性のみを使用するABAC」
```

#### ReBAC（Relationship-Based Access Control
- ユーザーとリソース間の関係性でグラフ理論で権限決定
- 権限の定義が書きやすい
- サーバが必要で学習コストも高いので、今回は多分見送り



## 今回の要件
- 認証との分離
- マルチテナント型の権限設計
  - A会社、B会社、C会社があって、会社ごとのデータは分離されていなければならない
  - ある会社から別の会社情報が見えてしまうと信用に関わる
    - DB層で分離できない
    - 権限判定で分離する


## Casbin
- ライブラリとして使える
- もうPythonでライブラリとして使えるツールはこれくらいしかない。
- これ以外だと、マネージドにするか、自前サーバが必要


## ドメインベースRBAC
- ドメイン（テナント）判定 + RBAC



## 考慮事項
- 関数？クラス？ 関数でいけそう
- 単純なAllow/Deny以外の制御が必要だと、crud側でfilter()とかが必要
- 追加要件 ABACで別実装　crud側? 神クラスを作る？
- APIのURL設計に条件あり
- 

# PyCasbin Domain-Based Multi-Tenant Authorization System

FastAPIとPyCasbinを使用したドメインベースマルチテナント対応RBAC認可システムの実装です。

## 🏗️ システムアーキテクチャ

シンプルなドメインベースCasbinによる高速マルチテナント認可：

```
リクエスト → 認証(JWT) → ドメインベースRBAC認可 → エンドポイント処理
                           ↓
                    enforce(user, domain, resource, action)
                           ↓
                    1回のCasbinチェックで完結
```

## 📁 ディレクトリ構造（認可システム関連）

```
casbin_sample/
├── 🔐 認可システムコア
│   ├── authorization_manager.py    # シンプルなドメインベース認可関数群
│   └── casbin_config.py            # ドメインベースCasbinモデル・ポリシー設定
│
├── 🔑 認証・認可補助
│   ├── auth.py                     # JWT認証ロジック
│   ├── casbin_rbac_auth.py         # レガシーCasbin関数（非推奨）
│   └── model.conf                  # ドメインベースCasbinモデル定義
│
├── 📊 データモデル
│   ├── models/
│   │   ├── users.py                # ユーザーモデル（corporation_id）
│   │   ├── roles.py                # ロールモデル（admin, accounting）
│   │   └── corporations.py         # 法人モデル（マルチテナント）
│   └── casbin_rule                 # Casbinポリシーデータベーステーブル
│
└── 🌐 APIエンドポイント
    └── routers/
        ├── inquiries.py             # 問い合わせ（管理者のみアクセス可）
        └── corporations.py          # 法人詳細（管理者のみ、経理はアクセス不可）
```

