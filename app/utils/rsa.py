from app.core.config import settings


def load_rsa_keys() -> tuple[str, str]:
    try:
        private_key = settings.JWT_PRIVATE_KEY_PATH.read_text()
        public_key = settings.JWT_PUBLIC_KEY_PATH.read_text()
        return private_key, public_key
    except Exception as e:
        raise RuntimeError(f"Failed to load RSA keys: {str(e)}")