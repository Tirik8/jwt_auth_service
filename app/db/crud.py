from datetime import datetime, timedelta
from sqlalchemy import desc
from sqlalchemy.orm import Session
from app.core import security
from app.db import models, schemas
from app.core.config import settings


def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def get_user_by_id(db: Session, id: int):
    return db.query(models.User).filter(models.User.id == id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def authenticate_user(db: Session, username_or_email: str, password: str):
    user = get_user_by_username(db, username_or_email)
    if not user:
        user = get_user_by_email(db, username_or_email)
    if not user:
        return False
    if not security.verify_password(password, user.hashed_password): # type: ignore
        return False
    return user


def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = security.get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        is_active=True,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def create_refresh_token(
    db: Session,
    user_id: int,
    expires_delta: timedelta | None = None,
    previous_token_id: int | None = None,
) -> tuple[str, models.RefreshToken]:
    expires_at = datetime.utcnow() + (
        expires_delta or timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    )

    db_token = models.RefreshToken(
        user_id=user_id,
        expires_at=expires_at,
        is_active=True,
        previous_token_id=previous_token_id,
    )
    db.add(db_token)
    db.commit()
    db.refresh(db_token)

    token_data = {
        "sub": str(user_id),
        "token_id": db_token.id,
        "type": "refresh",
        "created_at": datetime.utcnow().isoformat(),
    }

    token = security.create_refresh_token(data=token_data, expires_delta=expires_delta)

    return token, db_token


def get_refresh_token(db: Session, id: str):
    return db.query(models.RefreshToken).filter(models.RefreshToken.id == id).first()


def revoke_refresh_token_by_id(db: Session, token_id: int):
    db_token = (
        db.query(models.RefreshToken).filter(models.RefreshToken.id == token_id).first()
    )
    if db_token:
        db_token.is_active = False # type: ignore
        db.commit()
        db.refresh(db_token)
    return db_token


def get_refresh_tokens(db: Session, count: int, user_id: int):
    return (
        db.query(models.RefreshToken)
        .filter(models.RefreshToken.user_id == user_id)
        .filter(models.RefreshToken.is_active == True)
        .order_by(desc(models.RefreshToken.created_at))
        .limit(count)
        .all()
    )
