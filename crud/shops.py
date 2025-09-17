from sqlalchemy.orm import Session
import models
from schemas.shops import ShopCreate, ShopUpdate


def get_shop(db: Session, shop_id: int, corporation_id: int = None):
    """
    マルチテナント対応の店舗個別取得
    corporation_id が指定された場合、そのテナントのデータのみを返す
    """
    query = db.query(models.Shop).filter(models.Shop.id == shop_id)

    # マルチテナントフィルタリング
    if corporation_id is not None:
        query = query.filter(models.Shop.corporation_id == corporation_id)

    return query.first()


def get_shops(db: Session, skip: int = 0, limit: int = 100, corporation_id: int = None):
    """
    マルチテナント対応の店舗一覧取得
    corporation_id が指定された場合、そのテナントのデータのみを返す
    """
    query = db.query(models.Shop)

    # マルチテナントフィルタリング
    if corporation_id is not None:
        query = query.filter(models.Shop.corporation_id == corporation_id)

    return query.offset(skip).limit(limit).all()




def get_shops_by_corporation(db: Session, corporation_id: int, skip: int = 0, limit: int = 100):
    """特定法人の店舗一覧を取得"""
    return db.query(models.Shop).filter(
        models.Shop.corporation_id == corporation_id
    ).offset(skip).limit(limit).all()


def create_shop(db: Session, shop: ShopCreate):
    """新規店舗作成"""
    db_shop = models.Shop(**shop.dict())
    db.add(db_shop)
    db.commit()
    db.refresh(db_shop)
    return db_shop


def update_shop(db: Session, shop_id: int, shop: ShopUpdate, corporation_id: int = None):
    """店舗情報更新"""
    db_shop = get_shop(db, shop_id, corporation_id)
    if not db_shop:
        return None

    update_data = shop.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_shop, key, value)

    db.commit()
    db.refresh(db_shop)
    return db_shop


def delete_shop(db: Session, shop_id: int, corporation_id: int = None):
    """店舗削除"""
    db_shop = get_shop(db, shop_id, corporation_id)
    if db_shop:
        db.delete(db_shop)
        db.commit()
        return True
    return False


def add_shop_to_corporation(db: Session, shop_id: int, corporation_id: int):
    """店舗を法人に関連付け（多対多）"""
    shop = db.query(models.Shop).filter(models.Shop.id == shop_id).first()
    corporation = db.query(models.Corporation).filter(models.Corporation.id == corporation_id).first()

    if shop and corporation:
        if corporation not in shop.corporations:
            shop.corporations.append(corporation)
            db.commit()
        return shop
    return None


def remove_shop_from_corporation(db: Session, shop_id: int, corporation_id: int):
    """店舗と法人の関連を解除"""
    shop = db.query(models.Shop).filter(models.Shop.id == shop_id).first()
    corporation = db.query(models.Corporation).filter(models.Corporation.id == corporation_id).first()

    if shop and corporation:
        if corporation in shop.corporations:
            shop.corporations.remove(corporation)
            db.commit()
        return shop
    return None