#!/usr/bin/env python3
"""
テストデータを作成
"""

from database import SessionLocal
import models

def setup_test_data():
    """テストデータを作成"""
    db = SessionLocal()

    try:
        # accountantロールを作成
        accountant_role = db.query(models.Role).filter(models.Role.name == "accountant").first()
        if not accountant_role:
            accountant_role = models.Role(name="accountant")
            db.add(accountant_role)
            db.commit()
            db.refresh(accountant_role)
            print(f"Created accountant role: {accountant_role.id}")

        # bobユーザーを作成
        bob_user = db.query(models.User).filter(models.User.username == "bob").first()
        if not bob_user:
            bob_user = models.User(
                username="bob",
                email="bob@company1.com",
                full_name="Bob Accountant",
                hashed_password="dummy_hash",
                corporation_id=1,  # corporation_1に所属
                role_id=accountant_role.id  # accountantロール
            )
            db.add(bob_user)
            db.commit()
            db.refresh(bob_user)
            print(f"Created bob user: {bob_user.id}")

        # shop1を作成
        shop1 = db.query(models.Shop).filter(models.Shop.id == 1).first()
        if not shop1:
            shop1 = models.Shop(
                name="Shop 1",
                address="123 Main St",
                manager_name="Manager 1",
                business_hours="9:00-18:00",
                corporation_id=1  # corporation_1に所属
            )
            db.add(shop1)
            db.commit()
            db.refresh(shop1)
            print(f"Created shop1: {shop1.id}")

        print("テストデータセットアップ完了")

    finally:
        db.close()

if __name__ == "__main__":
    setup_test_data()