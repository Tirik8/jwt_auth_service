from fastapi import HTTPException, status


class ServerException:
    @staticmethod
    def verify_token_error():
        raise HTTPException(status_code=400, detail="Verify token error")

    @staticmethod
    def username_already_registered():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )

    @staticmethod
    def email_already_registered():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )

    @staticmethod
    def incorrect_username_or_password():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    @staticmethod
    def invalid_refresh_token():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    @staticmethod
    def refresh_token_missing():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token missing",
        )

    @staticmethod
    def invalid_token_type_or_subject():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type or subject",
            headers={"WWW-Authenticate": "Bearer"},
        )

    @staticmethod
    def user_not_found():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    @staticmethod
    def credentials_exception():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    @staticmethod
    def could_not_validate_credentials():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    @staticmethod
    def inactive_user():
        raise HTTPException(status_code=400, detail="Inactive user")

    @staticmethod
    def not_superuser():
        raise HTTPException(status_code=403, detail="You not superuser")
