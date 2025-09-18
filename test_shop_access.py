#!/usr/bin/env python3
"""
shop権限テスト - aliceとbobでのアクセス制御を確認
"""

import requests
import json

# APIのベースURL
BASE_URL = "http://localhost:8000"

def test_shop_access():
    """shop1へのアクセス権限テスト"""

    # aliceでテスト（admin権限）
    print("=== Alice (admin) でのテスト ===")
    alice_headers = {"Authorization": "Bearer alice"}

    # shop一覧取得
    response = requests.get(f"{BASE_URL}/shops", headers=alice_headers)
    print(f"Alice - shop一覧取得: {response.status_code}")
    if response.status_code == 200:
        shops = response.json()
        print(f"取得したshop数: {len(shops)}")
        for shop in shops:
            print(f"  - Shop {shop['id']}: {shop['name']}")
    else:
        print(f"エラー: {response.text}")

    # shop1詳細取得
    response = requests.get(f"{BASE_URL}/shops/1", headers=alice_headers)
    print(f"Alice - shop1詳細取得: {response.status_code}")
    if response.status_code == 200:
        shop = response.json()
        print(f"  Shop名: {shop['name']}, 法人ID: {shop['corporation_id']}")
    else:
        print(f"エラー: {response.text}")

    print("\n=== Bob (accountant) でのテスト ===")
    bob_headers = {"Authorization": "Bearer bob"}

    # shop一覧取得
    response = requests.get(f"{BASE_URL}/shops", headers=bob_headers)
    print(f"Bob - shop一覧取得: {response.status_code}")
    if response.status_code == 200:
        shops = response.json()
        print(f"取得したshop数: {len(shops)}")
    else:
        print(f"エラー: {response.text}")

    # shop1詳細取得
    response = requests.get(f"{BASE_URL}/shops/1", headers=bob_headers)
    print(f"Bob - shop1詳細取得: {response.status_code}")
    if response.status_code == 200:
        shop = response.json()
        print(f"  Shop名: {shop['name']}, 法人ID: {shop['corporation_id']}")
    else:
        print(f"エラー: {response.text}")

    print("\n=== 権限テスト結果まとめ ===")
    alice_shops = requests.get(f"{BASE_URL}/shops", headers=alice_headers)
    bob_shops = requests.get(f"{BASE_URL}/shops", headers=bob_headers)

    print(f"Alice (admin): {alice_shops.status_code} - {'✓ アクセス可能' if alice_shops.status_code == 200 else '✗ アクセス拒否'}")
    print(f"Bob (accountant): {bob_shops.status_code} - {'✓ アクセス可能' if bob_shops.status_code == 200 else '✗ アクセス拒否'}")

    if alice_shops.status_code == 200 and bob_shops.status_code == 403:
        print("🎉 権限設定が正しく動作しています！")
    else:
        print("⚠️  権限設定に問題があります")

if __name__ == "__main__":
    test_shop_access()