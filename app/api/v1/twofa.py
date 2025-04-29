from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer
from app.core import security
from app.db import crud, models
from fastapi import Security
from app.db.database import get_db
from sqlalchemy.orm import Session

router = APIRouter()

@router.post("/enable")
async def enable_2fa(
    current_user: models.User = Depends(security.get_current_active_user)
):
    pass


@router.post("/disable")
async def disable_2fa(
    current_user: models.User = Depends(security.get_current_active_user)
):
    pass


@router.post("/verify")
async def verivy_2fa(
    current_user: models.User = Depends(security.get_current_active_user)
):
    pass