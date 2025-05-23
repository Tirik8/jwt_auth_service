from datetime import datetime, timedelta
from typing import Annotated, Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.config import settings
from app.db import models, crud
from app.db.database import get_db


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def load_rsa_keys() -> tuple[str, str]:
    try:
        private_key = settings.JWT_PRIVATE_KEY_PATH.read_text(encoding="utf-8")
        public_key = settings.JWT_PUBLIC_KEY_PATH.read_text(encoding="utf-8")
        return private_key, public_key
    except Exception as e:
        raise RuntimeError(f"Failed to load RSA keys: {str(e)}")

JWT_PRIVATE_KEY, JWT_PUBLIC_KEY = load_rsa_keys()


class TokenData(BaseModel):
    username: Optional[str] = None

def verify_password(plain_password: str, hashed_password: str) -> bool:
    
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_PRIVATE_KEY, algorithm=settings.ALGORITHM)
    
    return encoded_jwt

def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, JWT_PRIVATE_KEY, algorithm=settings.ALGORITHM)
    
    return encoded_jwt

def verify_token(token: str) -> dict:
    
    try:
        payload = jwt.decode(token, JWT_PUBLIC_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

def verify_refresh_token(db: Session, token: str):
    
    try:
        payload = verify_token(token)
        user_id: str = payload.get("sub")
        
        if user_id is None:
            return None
        
        db_token = crud.get_refresh_token(db, token)
        if not db_token or not db_token.is_active:
            return None
            
        return db_token
    except JWTError:
        return None

async def validate_token(token: str, db: Session, token_type: str = "access") -> models.User:
    payload = verify_token(token)
    
    username: str = payload.get("sub")
    token_type_payload: str = payload.get("type")
    
    if username is None or token_type_payload != token_type:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type or subject",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = crud.get_user_by_username(db, username=username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


async def get_current_user(credentials: Annotated[HTTPAuthorizationCredentials, Depends(HTTPBearer())], db: Session = Depends(get_db)) -> models.User:

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        token = credentials.credentials
        payload = verify_token(token)
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    
    user = crud.get_user_by_username(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    
    return user

async def get_current_active_user(current_user: models.User = Depends(get_current_user)):

    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    return current_user

async def is_superuser(current_user: models.User = Depends(get_current_active_user)) -> bool:

    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="You not superuser")
    return True