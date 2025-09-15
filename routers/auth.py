from fastapi import APIRouter, Depends, HTTPException, status, Path, Body
from sqlalchemy.orm import Session
import crud
import schemas
from database import get_db
from auth_examples import login_examples

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={404: {"description": "Not found"}},
)


@router.post("/login", response_model=schemas.Token, summary="ユーザーログイン")
def login(
    request: schemas.LoginRequest = Body(..., examples=login_examples),
    db: Session = Depends(get_db)
):
    """
    ユーザー名とパスワードでログインしてJWTトークンを取得します。

    **テスト用ユーザー:**
    - alice / alicepass (ABC Corporation)
    - dave / davepass (DEF Corporation)

    **使用方法:**
    1. このエンドポイントでトークンを取得
    2. 取得したaccess_tokenをBearerトークンとして他のAPIで使用
    """
    user = crud.get_user_by_username(db, username=request.username)
    if not user or not crud.verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password"
        )

    return {
        "access_token": user.username,
        "token_type": "bearer"
    }


@router.get("/token/{username}", summary="簡単認証トークン取得")
def get_simple_token(
    username: str = Path(..., examples={"alice": {"summary": "Alice用トークン", "value": "alice"}, "dave": {"summary": "Dave用トークン", "value": "dave"}}),
    db: Session = Depends(get_db)
):
    """
    指定されたユーザー名の簡単認証トークンを取得します。
    サンプル実装用の簡易認証です。

    **テスト用ユーザー名:**
    - alice (ABC Corporation)
    - dave (DEF Corporation)

    **使用方法:**
    1. このエンドポイントでトークンを取得
    2. 取得したトークンをBearerトークンとして他のAPIで使用
    3. または直接ユーザー名をBearerトークンとして使用
    """
    user = crud.get_user_by_username(db, username=username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "access_token": username,
        "token_type": "bearer",
        "user_id": user.id,
        "username": user.username,
        "corporation_id": user.corporation_id
    }