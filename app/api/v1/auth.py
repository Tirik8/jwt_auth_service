from fastapi import APIRouter, Depends, status, Response, Request
from sqlalchemy.orm import Session
from datetime import timedelta

from app.core import security
from app.core.config import settings
from app.db import crud, schemas
from app.db.database import get_db
from app.utils import cookie
from app.utils.exception import ServerException

router = APIRouter()


@router.post(
    "/register",
    response_model=schemas.TokenResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register_and_login(
    user: schemas.UserCreate,
    responce: Response,
    db: Session = Depends(get_db),
):
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        ServerException.username_already_registered()

    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        ServerException.email_already_registered()
    user = crud.create_user(db=db, user=user)

    access_token = security.create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    refresh_token, _ = crud.create_refresh_token(
        db,
        user_id=user.id,
        expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )

    cookie.set_refresh_token_cookie(responce, refresh_token)

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/verify_email")
async def verify_email(email_token: str):
    pass


@router.post("/login", response_model=schemas.TokenResponse)
async def login(
    form_data: schemas.UserAuth,
    responce: Response,
    db: Session = Depends(get_db),
):
    user = crud.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        ServerException.incorrect_username_or_password()

    access_token = security.create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    refresh_token, _ = crud.create_refresh_token(
        db,
        user_id=user.id,
        expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )

    cookie.set_refresh_token_cookie(responce, refresh_token)

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/refresh", response_model=schemas.TokenResponse)
async def refresh_tokens(
    responce: Response,
    request: Request,
    db: Session = Depends(get_db),
):
    refresh_token = request.cookies.get(settings.REFRESH_TOKEN_COOKIE_NAME)

    if not refresh_token:
        ServerException.refresh_token_missing()

    db_token = security.verify_refresh_token(db, refresh_token)

    if not db_token:
        cookie.delete_refresh_token_cookie(responce)
        ServerException.invalid_refresh_token()

    old_token = crud.revoke_refresh_token_by_id(db, db_token.id)
    user = crud.get_user_by_id(db, db_token.user_id)

    access_token = security.create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    refresh_token, _ = crud.create_refresh_token(
        db,
        user_id=db_token.user_id,
        expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        previous_token_id=old_token.id,
    )
    cookie.delete_refresh_token_cookie(responce)
    cookie.set_refresh_token_cookie(responce, refresh_token)

    return {"access_token": access_token, "token_type": "bearer"}


@router.delete("/logout")
async def logout(
    responce: Response,
    request: Request,
    db: Session = Depends(get_db),
):
    refresh_token = request.cookies.get(settings.REFRESH_TOKEN_COOKIE_NAME)
    db_token = security.verify_refresh_token(db, refresh_token)
    if db_token:
        crud.revoke_refresh_token_by_id(db, db_token.id)

    cookie.delete_refresh_token_cookie(responce)
    return {"message": "Logget out sucksessfully"}


@router.post("/forgot-password")
async def forgot_password():
    pass
