from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

import crud
import schemas
from database import get_db
from auth import security

router = APIRouter(
    prefix="/schools",
    tags=["schools"],
    responses={404: {"description": "Not found"}},
)


@router.post("/", response_model=schemas.School, summary="学校作成", dependencies=[Depends(security)])
def create_school(school: schemas.SchoolCreate, db: Session = Depends(get_db)):
    """
    新規学校を作成します。
    - **name**: 学校名
    - **code**: 学校コード（一意）
    - **address**: 住所（オプション）
    - **phone**: 電話番号（オプション）
    - **email**: メールアドレス（オプション）
    - **corporation_ids**: 関連法人IDリスト（オプション）
    """
    db_school = crud.get_school_by_code(db, code=school.code)
    if db_school:
        raise HTTPException(status_code=400, detail="School code already registered")
    return crud.create_school(db=db, school=school)


@router.get("/", response_model=List[schemas.School], summary="学校一覧取得", dependencies=[Depends(security)])
def read_schools(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    学校一覧を取得します。
    """
    schools = crud.get_schools(db, skip=skip, limit=limit)
    return schools


@router.get("/{school_id}", response_model=schemas.School, summary="学校詳細取得", dependencies=[Depends(security)])
def read_school(school_id: int, db: Session = Depends(get_db)):
    """
    指定IDの学校詳細を取得します（関連法人含む）。
    """
    db_school = crud.get_school(db, school_id=school_id)
    if db_school is None:
        raise HTTPException(status_code=404, detail="School not found")
    return db_school


@router.put("/{school_id}", response_model=schemas.School, summary="学校更新", dependencies=[Depends(security)])
def update_school(school_id: int, school: schemas.SchoolUpdate, db: Session = Depends(get_db)):
    """
    指定IDの学校情報を更新します。
    """
    db_school = crud.update_school(db, school_id=school_id, school=school)
    if db_school is None:
        raise HTTPException(status_code=404, detail="School not found")
    return db_school


@router.delete("/{school_id}", summary="学校削除", dependencies=[Depends(security)])
def delete_school(school_id: int, db: Session = Depends(get_db)):
    """
    指定IDの学校を削除します。
    """
    success = crud.delete_school(db, school_id=school_id)
    if not success:
        raise HTTPException(status_code=404, detail="School not found")
    return {"message": "School deleted successfully"}




@router.get("/{school_id}/inquiries", response_model=List[schemas.Inquiry], summary="学校関連問い合わせ一覧", dependencies=[Depends(security)])
def read_school_inquiries(school_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    指定学校に関連する問い合わせ一覧を取得します。
    """
    school = crud.get_school(db, school_id=school_id)
    if not school:
        raise HTTPException(status_code=404, detail="School not found")
    inquiries = crud.get_inquiries_by_school(db, school_id=school_id, skip=skip, limit=limit)
    return inquiries