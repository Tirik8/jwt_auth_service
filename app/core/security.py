from datetime import datetime, timedelta
from typing import Annotated, Optional
from fastapi import Depends
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db import models, crud
from app.db.database import get_db
from app.utils import rsa
from app.utils.exception import ServerException


pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto",
    argon2__time_cost=3,
    argon2__memory_cost=65536,
    argon2__parallelism=4,
    argon2__hash_len=32,
    argon2__salt_len=16,
)

JWT_PRIVATE_KEY, JWT_PUBLIC_KEY = rsa.load_rsa_keys()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_PRIVATE_KEY, algorithm=settings.ALGORITHM)

    return encoded_jwt


def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, JWT_PRIVATE_KEY, algorithm=settings.ALGORITHM)

    return encoded_jwt


def verify_token(token: str) -> dict: # type: ignore
    try:
        payload = jwt.decode(token, JWT_PUBLIC_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        ServerException.could_not_validate_credentials


def verify_refresh_token(db: Session, token: str):
    try:
        payload = verify_token(token)
        user_id: int = int(payload.get("sub")) # type: ignore
        token_id: int = int(payload.get("token_id")) # type: ignore

        if user_id is None:
            ServerException.verify_token_error()

        db_token = crud.get_refresh_token(db, token_id) # type: ignore
        if not db_token or not db_token.is_active: # type: ignore
            ServerException.verify_token_error()

        return db_token
    except JWTError:
        ServerException.verify_token_error()


async def validate_token(
    token: str, db: Session, token_type: str = "access"
) -> models.User:
    payload = verify_token(token)

    username: str = payload.get("sub") # type: ignore
    token_type_payload: str = payload.get("type") # type: ignore

    if username is None or token_type_payload != token_type:
        ServerException.invalid_token_type_or_subject()

    user = crud.get_user_by_username(db, username=username)
    if user is None:
        ServerException.user_not_found()

    return user


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(HTTPBearer())],
    db: Session = Depends(get_db),
) -> models.User:
    
    try:
        token = credentials.credentials
        payload = verify_token(token)
        username: str = payload.get("sub") # type: ignore
        if username is None:
            ServerException.credentials_exception()
    except JWTError:
        ServerException.credentials_exception()

    user = crud.get_user_by_username(db, username=username) # type: ignore
    if user is None:
        ServerException.credentials_exception()

    return user


async def get_current_active_user(
    current_user: models.User = Depends(get_current_user),
):
    if not current_user.is_active: # type: ignore
        ServerException.inactive_user()

    return current_user


async def is_superuser(
    current_user: models.User = Depends(get_current_active_user),
) -> bool:
    if not current_user.is_superuser: # type: ignore
        ServerException.not_superuser()
    return True
