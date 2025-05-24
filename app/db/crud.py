from datetime import datetime, timedelta
from sqlalchemy import desc, select
from app.core import security
from app.db import models, schemas
from app.core.config import settings
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import UUID4


async def get_user_by_username(db: AsyncSession, username: str):
    result = await db.execute(
        select(models.User).filter(models.User.username == username)
    )
    return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, id: UUID4):
    result = await db.execute(select(models.User).filter(models.User.id == id))
    return result.scalar_one_or_none()


async def get_user_by_email(db: AsyncSession, email: str):
    result = await db.execute(select(models.User).filter(models.User.email == email))
    return result.scalar_one_or_none()


async def authenticate_user(db: AsyncSession, username_or_email: str, password: str):
    user = await get_user_by_username(db, username_or_email)
    if not user:
        user = await get_user_by_email(db, username_or_email)
    if not user:
        return False
    if not security.verify_password(password, user.hashed_password):
        return False
    return user


async def create_user(db: AsyncSession, user: schemas.UserCreate):
    hashed_password = security.get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        is_active=True,
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def create_refresh_token(
    db: AsyncSession,
    user_id: UUID4,
    expires_delta: timedelta | None = None,
    previous_token_id: UUID4 | None = None,
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
    await db.commit()
    await db.refresh(db_token)

    token_data = {
        "sub": str(user_id),
        "token_id": str(db_token.id),
        "type": "refresh",
        "created_at": datetime.utcnow().isoformat(),
    }

    token = security.create_refresh_token(data=token_data, expires_delta=expires_delta)

    return token, db_token


async def get_refresh_token(db: AsyncSession, id: UUID4):
    result = await db.execute(
        select(models.RefreshToken).filter(models.RefreshToken.id == id)
    )
    return result.scalar_one_or_none()


async def revoke_refresh_token_by_id(db: AsyncSession, token_id: UUID4):
    result = await db.execute(
        select(models.RefreshToken).where(models.RefreshToken.id == token_id)
    )
    db_token = result.scalar_one()
    db_token.is_active = False
    await db.commit()
    await db.refresh(db_token)
    return db_token


async def get_refresh_tokens(db: AsyncSession, count: int, user_id: UUID4):
    result = await db.execute(
        select(models.RefreshToken)
        .filter(models.RefreshToken.user_id == user_id)
        .filter(models.RefreshToken.is_active)
        .order_by(desc(models.RefreshToken.created_at))
        .limit(count)
    )
    return result.scalars().all()
