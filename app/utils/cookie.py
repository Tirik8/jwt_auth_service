from fastapi import Response
from app.core.config import settings

def set_refresh_token_cookie(
    responce: Response,
    refresh_token: str
) -> None:
    responce.set_cookie(
        key = settings.REFRESH_TOKEN_COOKIE_NAME,
        value = refresh_token,
        max_age = settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        httponly = settings.REFRESH_TOKEN_HTTP_ONLY,
        secure = settings.REFRESH_TOKEN_SECURE,
        samesite = settings.REFRESH_TOKEN_SAME_SITE,
    )

def delete_refresh_token_cookie(
    responce: Response
) -> None:
    responce.delete_cookie(
        key = settings.REFRESH_TOKEN_COOKIE_NAME,
        httponly = settings.REFRESH_TOKEN_HTTP_ONLY,
        secure = settings.REFRESH_TOKEN_SECURE,
        samesite = settings.REFRESH_TOKEN_SAME_SITE,
    )