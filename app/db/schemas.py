from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)

    @field_validator('username')
    def validate_username(cls, v):
        if not v.isalnum() and '_' not in v:
            raise ValueError('Username can only contain alphanumeric characters and underscores')
        return v
    
class UserCreate(UserBase):
    email: EmailStr
    password: str = Field(..., min_length=8)
    
class User(UserBase):
    email: EmailStr
    id: int
    is_active: bool
    
    class Config:
        from_attributes = True

class UserAuth(UserBase):
    password: str = Field(..., min_length=8)

class RefreshTokenCreate(BaseModel):
    user_id: int
    expires_at: datetime

class RefreshTokenResponse(BaseModel):
    id: int
    token: str
    user_id: int
    is_active: bool
    created_at: datetime
    expires_at: datetime
    previous_token_id: int | None = None

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_at: datetime

class TokenPairResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    username: Optional[str] = None