from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
import uuid
from sqlalchemy.sql import func
from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(
        UUID(as_uuid=True), 
        default=uuid.uuid4, 
        unique=True, 
        primary_key=True, 
        index=True
    )
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    email_verified = Column(Boolean, default=False)
    
class EmailTokens(Base):
    __tablename__ = "email_codes"
    
    id = Column(int, unique=True, primary_key=True, index=True)
    user_id = Column(UUID, ForeignKey(User.id))
    token = Column(UUID)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, primary_key=True, index=True)
    user_id = Column(UUID, ForeignKey(User.id))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True))
    previous_token_id = Column(UUID, ForeignKey(id), nullable=True)
