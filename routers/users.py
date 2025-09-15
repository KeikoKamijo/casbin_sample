from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

import crud
import schemas
import models
from database import get_db
from auth import security, get_current_user

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)


@router.post("/", response_model=schemas.User, summary="ユーザー作成", dependencies=[Depends(security)])
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    新規ユーザーを作成します。
    - **username**: ユーザー名（一意）
    - **email**: メールアドレス（一意）
    - **password**: パスワード
    - **corporation_id**: 所属法人ID（オプション）
    """
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return crud.create_user(db=db, user=user)


@router.get("/me", response_model=schemas.User, summary="現在のユーザー情報取得")
def read_current_user(current_user: models.User = Depends(get_current_user)):
    """
    現在ログイン中のユーザー情報を取得します。
    """
    return current_user


@router.get("/", response_model=List[schemas.User], summary="ユーザー一覧取得", dependencies=[Depends(security)])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    ユーザー一覧を取得します。
    """
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@router.get("/{user_id}", response_model=schemas.User, summary="ユーザー詳細取得", dependencies=[Depends(security)])
def read_user(user_id: int, db: Session = Depends(get_db)):
    """
    指定IDのユーザー詳細を取得します。
    """
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@router.put("/{user_id}", response_model=schemas.User, summary="ユーザー更新", dependencies=[Depends(security)])
def update_user(user_id: int, user: schemas.UserUpdate, db: Session = Depends(get_db)):
    """
    指定IDのユーザー情報を更新します。
    """
    db_user = crud.update_user(db, user_id=user_id, user=user)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@router.delete("/{user_id}", summary="ユーザー削除", dependencies=[Depends(security)])
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """
    指定IDのユーザーを削除します。
    """
    success = crud.delete_user(db, user_id=user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}


@router.get("/{user_id}/inquiries", response_model=List[schemas.Inquiry], summary="ユーザーの問い合わせ一覧", dependencies=[Depends(security)])
def read_user_inquiries(user_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    指定ユーザーが作成した問い合わせ一覧を取得します。
    """
    user = crud.get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    inquiries = crud.get_inquiries_by_user(db, user_id=user_id, skip=skip, limit=limit)
    return inquiries


@router.get("/{user_id}/assigned-inquiries", response_model=List[schemas.Inquiry], summary="担当問い合わせ一覧", dependencies=[Depends(security)])
def read_user_assigned_inquiries(user_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    指定ユーザーが担当する問い合わせ一覧を取得します。
    """
    user = crud.get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    inquiries = crud.get_inquiries_assigned_to_user(db, user_id=user_id, skip=skip, limit=limit)
    return inquiries