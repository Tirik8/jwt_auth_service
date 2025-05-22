from pathlib import Path
from typing import Any, Dict
from pydantic_settings import BaseSettings
from pydantic import Field, PostgresDsn


class CryptContextSettings(BaseSettings):
    class Config:
        env_file = ".env"
        env_prefix = "CRYPT_"
        extra = "allow"

    @property
    def config_dict(self) -> Dict[str, Any]:
        config = {}
        for field, value in self.model_dump().items():
            if field.startswith(self.Config.env_prefix.lower()):
                key = field[len(self.Config.env_prefix) :].lower()
                config[key] = value
        return config


class Settings(BaseSettings):
    APP: str
    HOST: str
    PORT: int
    LOG_LEVEL: str

    JWT_PRIVATE_KEY_PATH: Path
    JWT_PUBLIC_KEY_PATH: Path
    ALGORITHM: str

    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int
    REFRESH_TOKEN_COOKIE_NAME: str
    REFRESH_TOKEN_HTTP_ONLY: bool
    REFRESH_TOKEN_SECURE: bool
    REFRESH_TOKEN_SAME_SITE: str

    CRYPTO_CONTEXT: CryptContextSettings = Field(default_factory=CryptContextSettings)

    DATABASE_URL: PostgresDsn

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
