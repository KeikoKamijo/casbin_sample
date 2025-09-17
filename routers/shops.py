from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

import crud
import schemas
import models
from database import get_db
from auth import security
from authorization_manager import authorization_manager

router = APIRouter(
    prefix="/shops",
    tags=["shops"],
    responses={404: {"description": "Not found"}},
)


@router.post("/", response_model=schemas.Shop, summary="店舗作成", dependencies=[Depends(security)])
def create_shop(
    shop: schemas.ShopCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(authorization_manager)
):
    """
    新規店舗を作成します。
    - **name**: 店舗名
    - **address**: 住所
    - **manager_name**: 店長名
    - **business_hours**: 営業時間
    - **corporation_id**: 所属法人ID
    """

    # マルチテナント: 自分の法人の店舗のみ作成可能
    if shop.corporation_id != current_user.corporation_id:
        raise HTTPException(
            status_code=403,
            detail=f"You can only create shops for your corporation (ID: {current_user.corporation_id})"
        )

    return crud.create_shop(db=db, shop=shop)


@router.get("/", response_model=List[schemas.Shop], summary="店舗一覧取得", dependencies=[Depends(security)])
def read_shops(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(authorization_manager)
):
    """
    店舗一覧を取得します（自法人のみ）。
    """
    # マルチテナント対応：自法人の店舗のみ取得
    shops = crud.get_shops(db, skip=skip, limit=limit, corporation_id=current_user.corporation_id)
    return shops


@router.get("/{shop_id}", response_model=schemas.Shop, summary="店舗詳細取得", dependencies=[Depends(security)])
def read_shop(
    shop_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(authorization_manager)
):
    """
    指定IDの店舗詳細を取得します。

    マルチテナント対応：自法人の店舗のみ取得可能
    """
    db_shop = crud.get_shop(db, shop_id=shop_id, corporation_id=current_user.corporation_id)
    if db_shop is None:
        raise HTTPException(status_code=404, detail="Shop not found")
    return db_shop


@router.put("/{shop_id}", response_model=schemas.Shop, summary="店舗更新", dependencies=[Depends(security)])
def update_shop(
    shop_id: int,
    shop: schemas.ShopUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(authorization_manager)
):
    """
    指定IDの店舗情報を更新します。
    """
    # 更新時に法人IDを変更しようとした場合はエラー
    if shop.corporation_id and shop.corporation_id != current_user.corporation_id:
        raise HTTPException(
            status_code=403,
            detail="Cannot change shop to different corporation"
        )

    db_shop = crud.update_shop(db, shop_id=shop_id, shop=shop, corporation_id=current_user.corporation_id)
    if db_shop is None:
        raise HTTPException(status_code=404, detail="Shop not found")
    return db_shop


@router.delete("/{shop_id}", summary="店舗削除", dependencies=[Depends(security)])
def delete_shop(
    shop_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(authorization_manager)
):
    """
    指定IDの店舗を削除します。
    """
    success = crud.delete_shop(db, shop_id=shop_id, corporation_id=current_user.corporation_id)
    if not success:
        raise HTTPException(status_code=404, detail="Shop not found")
    return {"message": "Shop deleted successfully"}


@router.get("/corporation/{corporation_id}/shops", response_model=List[schemas.Shop], summary="法人の店舗一覧", dependencies=[Depends(security)])
def read_corporation_shops(
    corporation_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(authorization_manager)
):
    """
    指定法人に所属する店舗一覧を取得します。

    マルチテナント対応：自法人のみアクセス可能
    """
    # マルチテナントチェック
    if corporation_id != current_user.corporation_id:
        raise HTTPException(
            status_code=403,
            detail=f"You can only access shops for your corporation (ID: {current_user.corporation_id})"
        )

    db_corporation = crud.get_corporation(db, corporation_id=corporation_id)
    if db_corporation is None:
        raise HTTPException(status_code=404, detail="Corporation not found")

    shops = crud.get_shops_by_corporation(db, corporation_id=corporation_id, skip=skip, limit=limit)
    return shops