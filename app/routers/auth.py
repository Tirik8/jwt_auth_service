from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from sqlalchemy.orm import Session
from datetime import timedelta

from app.core import security
from app.core.config import settings
from app.db import crud, schemas
from app.db.database import get_db
from app.utils import cookie

router = APIRouter(tags=["auth"])



@router.post("/register", response_model=schemas.TokenResponse)
async def register_and_login(
    user: schemas.UserCreate,
    responce: Response,
    db: Session = Depends(get_db),
):
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    user = crud.create_user(db=db, user=user)
    
    access_token = security.create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    refresh_token = security.create_refresh_token(
        data={"sub": user.username},
        expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    )
    
    cookie.set_refresh_token_cookie(responce, refresh_token)
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.post("/auth", response_model=schemas.TokenResponse)
async def login(
    form_data: schemas.UserAuth,
    responce: Response,
    db: Session = Depends(get_db),
    
):
    
    user = crud.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    
    access_token = security.create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    refresh_token, _ = crud.create_refresh_token(
        db, 
        user_id=user.id,
        expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    )
    
    cookie.set_refresh_token_cookie(responce, refresh_token)
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.post("/refresh", response_model=schemas.TokenResponse)
async def refresh_tokens(
    responce: Response,
    request: Request,
    db: Session = Depends(get_db),
):
    
    refresh_token = request.cookies.get(settings.REFRESH_TOKEN_COOKIE_NAME)
    
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token missing",
        )

    db_token = security.verify_refresh_token(db, refresh_token)
    
    if not db_token:
        cookie.delete_refresh_token_cookie(responce)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )
        
    old_token = crud.revoke_refresh_token_by_token(db, db_token.token)
    user = crud.get_user_by_id(db, db_token.user_id)
    
    access_token = security.create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    refresh_token, _ = crud.create_refresh_token(
        db,
        user_id=db_token.user_id,
        expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        previous_token_id = old_token.id
    )
    cookie.set_refresh_token_cookie(responce, refresh_token)
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }
    
@router.post("/logout")
async def logout(
    responce: Response,
    request: Request,
    db: Session = Depends(get_db),
):
    refresh_token = request.cookies.get(settings.REFRESH_TOKEN_COOKIE_NAME)
    db_token = security.verify_refresh_token(db, refresh_token)
    crud.revoke_refresh_token_by_token(db, db_token.token)
    
    cookie.delete_refresh_token_cookie(responce)
    return {"message": "Logget out sucksessfully"}

@router.get("/verify_key")
async def get_verify_key():
    return {"rsa_public_key": settings.JWT_PUBLIC_KEY_PATH.read_text()}