from pydantic import BaseModel, EmailStr, Field, field_validator, UUID4
from datetime import datetime
from typing import Optional


class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)

    @field_validator("username")
    def validate_username(cls, v):
        if not v.isalnum() and "_" not in v:
            raise ValueError(
                "Username can only contain alphanumeric characters and underscores"
            )
        return v


class UserAuth(UserBase):
    password: str = Field(..., min_length=8)


class UserCreate(UserAuth):
    email: EmailStr


class User(UserBase):
    email: EmailStr
    id: int
    is_active: bool

    class Config:
        from_attributes = True


class RefreshTokenCreate(BaseModel):
    user_id: UUID4
    expires_at: datetime


class RefreshTokenResponse(BaseModel):
    id: UUID4
    token: str
    user_id: UUID4
    is_active: bool
    created_at: datetime
    expires_at: datetime
    previous_token_id: UUID4 | None = None

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: Optional[str] = None
