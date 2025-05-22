from datetime import datetime
from fastapi import APIRouter
from app.core.config import settings

router = APIRouter()

@router.get("/")
def read_root():
    return {"status": "ok", "timestamp": datetime.now()}


@router.get("/get_public_rsa_key")
async def get_verify_key():
    return {"rsa_public_key": settings.JWT_PUBLIC_KEY_PATH.read_text()}