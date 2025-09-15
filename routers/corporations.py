from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

import crud
import schemas
from database import get_db

router = APIRouter(
    prefix="/api/v1/corporations",
    tags=["corporations"],
    responses={404: {"description": "Not found"}},
)


@router.post("/", response_model=schemas.Corporation, summary="法人作成")
def create_corporation(corporation: schemas.CorporationCreate, db: Session = Depends(get_db)):
    """
    新規法人を作成します。
    - **name**: 法人名（一意）
    - **code**: 法人コード（一意）
    - **description**: 説明（オプション）
    """
    db_corporation = crud.get_corporation_by_name(db, name=corporation.name)
    if db_corporation:
        raise HTTPException(status_code=400, detail="Corporation name already registered")
    db_corporation = crud.get_corporation_by_code(db, code=corporation.code)
    if db_corporation:
        raise HTTPException(status_code=400, detail="Corporation code already registered")
    return crud.create_corporation(db=db, corporation=corporation)


@router.get("/", response_model=List[schemas.Corporation], summary="法人一覧取得")
def read_corporations(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    法人一覧を取得します。
    """
    corporations = crud.get_corporations(db, skip=skip, limit=limit)
    return corporations


@router.get("/{corporation_id}", response_model=schemas.CorporationWithUsers, summary="法人詳細取得")
def read_corporation(corporation_id: int, db: Session = Depends(get_db)):
    """
    指定IDの法人詳細を取得します（所属ユーザー含む）。
    """
    db_corporation = crud.get_corporation(db, corporation_id=corporation_id)
    if db_corporation is None:
        raise HTTPException(status_code=404, detail="Corporation not found")
    return db_corporation


@router.put("/{corporation_id}", response_model=schemas.Corporation, summary="法人更新")
def update_corporation(corporation_id: int, corporation: schemas.CorporationUpdate, db: Session = Depends(get_db)):
    """
    指定IDの法人情報を更新します。
    """
    db_corporation = crud.update_corporation(db, corporation_id=corporation_id, corporation=corporation)
    if db_corporation is None:
        raise HTTPException(status_code=404, detail="Corporation not found")
    return db_corporation


@router.delete("/{corporation_id}", summary="法人削除")
def delete_corporation(corporation_id: int, db: Session = Depends(get_db)):
    """
    指定IDの法人を削除します。
    """
    success = crud.delete_corporation(db, corporation_id=corporation_id)
    if not success:
        raise HTTPException(status_code=404, detail="Corporation not found")
    return {"message": "Corporation deleted successfully"}


@router.get("/{corporation_id}/users", response_model=List[schemas.User], summary="法人所属ユーザー一覧")
def read_corporation_users(corporation_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    指定法人に所属するユーザー一覧を取得します。
    """
    db_corporation = crud.get_corporation(db, corporation_id=corporation_id)
    if db_corporation is None:
        raise HTTPException(status_code=404, detail="Corporation not found")
    users = crud.get_users_by_corporation(db, corporation_id=corporation_id, skip=skip, limit=limit)
    return users


@router.get("/{corporation_id}/schools", response_model=List[schemas.School], summary="法人関連学校一覧")
def read_corporation_schools(corporation_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    指定法人に関連する学校一覧を取得します。
    """
    db_corporation = crud.get_corporation(db, corporation_id=corporation_id)
    if db_corporation is None:
        raise HTTPException(status_code=404, detail="Corporation not found")
    schools = crud.get_schools_by_corporation(db, corporation_id=corporation_id, skip=skip, limit=limit)
    return schools


@router.get("/{corporation_id}/inquiries", response_model=List[schemas.Inquiry], summary="法人関連問い合わせ一覧")
def read_corporation_inquiries(corporation_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    指定法人に関連する問い合わせ一覧を取得します。
    """
    corporation = crud.get_corporation(db, corporation_id=corporation_id)
    if not corporation:
        raise HTTPException(status_code=404, detail="Corporation not found")
    inquiries = crud.get_inquiries_by_corporation(db, corporation_id=corporation_id, skip=skip, limit=limit)
    return inquiries


@router.post("/{corporation_id}/schools/{school_id}", summary="法人と学校の関連付け")
def add_school_to_corporation(corporation_id: int, school_id: int, db: Session = Depends(get_db)):
    """
    法人と学校を関連付けます。
    """
    school = crud.add_school_to_corporation(db, school_id=school_id, corporation_id=corporation_id)
    if school is None:
        raise HTTPException(status_code=404, detail="School or Corporation not found")
    return {"message": "School added to Corporation successfully"}


@router.delete("/{corporation_id}/schools/{school_id}", summary="法人と学校の関連解除")
def remove_school_from_corporation(corporation_id: int, school_id: int, db: Session = Depends(get_db)):
    """
    法人と学校の関連を解除します。
    """
    school = crud.remove_school_from_corporation(db, school_id=school_id, corporation_id=corporation_id)
    if school is None:
        raise HTTPException(status_code=404, detail="School or Corporation not found")
    return {"message": "School removed from Corporation successfully"}