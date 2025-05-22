from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import PostgresDsn


class Settings(BaseSettings):
    JWT_PRIVATE_KEY_PATH: Path
    JWT_PUBLIC_KEY_PATH: Path
    ALGORITHM: str

    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int
    REFRESH_TOKEN_COOKIE_NAME: str
    REFRESH_TOKEN_HTTP_ONLY: bool
    REFRESH_TOKEN_SECURE: bool
    REFRESH_TOKEN_SAME_SITE: str

    DATABASE_URL: PostgresDsn

    class Config:
        env_file = ".env"


settings = Settings()
