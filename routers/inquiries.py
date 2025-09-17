from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

import crud
import schemas
import models
from database import get_db
from auth import security, get_current_user
from authorization_manager import authorization_manager

router = APIRouter(
    prefix="/inquiries",
    tags=["inquiries"],
    responses={404: {"description": "Not found"}},
)


# @router.post("/", response_model=schemas.Inquiry, summary="問い合わせ作成", dependencies=[Depends(security)])
# def create_inquiry(inquiry: schemas.InquiryCreate, db: Session = Depends(get_db)):
#     """
#     新規問い合わせを作成します。
#     - **title**: タイトル
#     - **content**: 内容
#     - **user_id**: 作成者ユーザーID
#     - **school_id**: 関連学校ID（オプション）
#     - **corporation_id**: 関連法人ID（オプション）
#     - **priority**: 優先度（low/normal/high/urgent）
#     - **status**: ステータス（デフォルト: pending）
#     """
#     # Validate user exists
#     user = crud.get_user(db, user_id=inquiry.user_id)
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")
#
#     # Validate school if provided
#     if inquiry.school_id:
#         school = crud.get_school(db, school_id=inquiry.school_id)
#         if not school:
#             raise HTTPException(status_code=404, detail="School not found")
#
#     # Validate corporation if provided
#     if inquiry.corporation_id:
#         corporation = crud.get_corporation(db, corporation_id=inquiry.corporation_id)
#         if not corporation:
#             raise HTTPException(status_code=404, detail="Corporation not found")
#
#     return crud.create_inquiry(db=db, inquiry=inquiry)


@router.get("/", response_model=List[schemas.Inquiry], summary="問い合わせ一覧取得（管理者のみ）", dependencies=[Depends(security)])
def read_inquiries(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    db: Session = Depends(get_db),
    is_authorized: bool = Depends(authorization_manager),
    current_user: models.User = Depends(get_current_user)
):
    """
    問い合わせ一覧を取得します。（管理者のみアクセス可能）
    - **status**: ステータスでフィルタ（pending/in_progress/resolved/closed）
    - **priority**: 優先度でフィルタ（low/normal/high/urgent）

    **権限**: admin ロールが必要（Casbinで自動判定）
    **アクセス不可**: accounting ロール
    **自動判定**: URL /inquiries + GET → inquiries:read 権限チェック
    """
    # 権限チェック
    if not is_authorized:
        raise HTTPException(status_code=403, detail="Access denied")

    # マルチテナント対応：ユーザーの所属法人のデータのみを取得
    inquiries = crud.get_inquiries(
        db,
        skip=skip,
        limit=limit,
        status=status,
        priority=priority,
        corporation_id=current_user.corporation_id
    )
    return inquiries


@router.get("/{inquiry_id}", response_model=schemas.Inquiry, summary="問い合わせ詳細取得（管理者のみ）", dependencies=[Depends(security)])
def read_inquiry(
    inquiry_id: int,
    db: Session = Depends(get_db),
    is_authorized: bool = Depends(authorization_manager),
    current_user: models.User = Depends(get_current_user)
):
    """
    指定IDの問い合わせ詳細を取得します（関連情報含む）。

    **権限**: admin ロールが必要（Casbinで自動判定）
    **アクセス不可**: accounting ロール
    **自動判定**: URL /inquiries/{id} + GET → inquiries:read 権限チェック
    """
    # 権限チェック
    if not is_authorized:
        raise HTTPException(status_code=403, detail="Access denied")

    # マルチテナント対応：ユーザーの所属法人のデータのみを取得
    db_inquiry = crud.get_inquiry(
        db,
        inquiry_id=inquiry_id,
        corporation_id=current_user.corporation_id
    )
    if db_inquiry is None:
        raise HTTPException(status_code=404, detail="Inquiry not found")
    return db_inquiry


# @router.put("/{inquiry_id}", response_model=schemas.Inquiry, summary="問い合わせ更新", dependencies=[Depends(security)])
# def update_inquiry(inquiry_id: int, inquiry: schemas.InquiryUpdate, db: Session = Depends(get_db)):
#     """
#     指定IDの問い合わせ情報を更新します。
#     """
#     db_inquiry = crud.update_inquiry(db, inquiry_id=inquiry_id, inquiry=inquiry)
#     if db_inquiry is None:
#         raise HTTPException(status_code=404, detail="Inquiry not found")
#     return db_inquiry


# @router.put("/{inquiry_id}/assign", response_model=schemas.Inquiry, summary="担当者割り当て", dependencies=[Depends(security)])
# def assign_inquiry(inquiry_id: int, assignment: schemas.InquiryAssign, db: Session = Depends(get_db)):
#     """
#     問い合わせに担当者を割り当てます。
#     ステータスがpendingの場合、自動的にin_progressに変更されます。
#     """
#     # Validate assigned_to user exists
#     assigned_user = crud.get_user(db, user_id=assignment.assigned_to_id)
#     if not assigned_user:
#         raise HTTPException(status_code=404, detail="Assigned user not found")
#
#     db_inquiry = crud.assign_inquiry(db, inquiry_id=inquiry_id, assigned_to_id=assignment.assigned_to_id)
#     if db_inquiry is None:
#         raise HTTPException(status_code=404, detail="Inquiry not found")
#     return db_inquiry


# @router.put("/{inquiry_id}/status", response_model=schemas.Inquiry, summary="ステータス更新", dependencies=[Depends(security)])
# def update_inquiry_status(inquiry_id: int, status_update: schemas.InquiryStatusUpdate, db: Session = Depends(get_db)):
#     """
#     問い合わせのステータスを更新します。
#     - **status**: pending/in_progress/resolved/closed
#     - **resolved_at**: 解決日時（resolvedステータス時）
#     """
#     db_inquiry = crud.update_inquiry_status(db, inquiry_id=inquiry_id, status_update=status_update)
#     if db_inquiry is None:
#         raise HTTPException(status_code=404, detail="Inquiry not found")
#     return db_inquiry
#
#
# @router.delete("/{inquiry_id}", summary="問い合わせ削除", dependencies=[Depends(security)])
# def delete_inquiry(inquiry_id: int, db: Session = Depends(get_db)):
#     """
#     指定IDの問い合わせを削除します。
#     """
#     success = crud.delete_inquiry(db, inquiry_id=inquiry_id)
#     if not success:
#         raise HTTPException(status_code=404, detail="Inquiry not found")
#     return {"message": "Inquiry deleted successfully"}