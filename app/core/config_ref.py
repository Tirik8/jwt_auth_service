from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import Field, PostgresDsn


class Settings(BaseSettings):
    JWT_PRIVATE_KEY_PATH: Path = Path
    JWT_PUBLIC_KEY_PATH: Path = Path
    ALGORITHM: str = "RS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    DATABASE_URL: PostgresDsn = Field(
        default="postgresql://user:password@server:port/database"
    )

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
