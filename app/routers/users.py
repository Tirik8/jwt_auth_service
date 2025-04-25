from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer
from app.core import security
from app.db import models
from fastapi import Security

router = APIRouter(prefix="/users", tags=["users"])

security_scheme = HTTPBearer()

@router.get("/me", dependencies=[Security(security_scheme)])
async def read_users_me(
    current_user: models.User = Depends(security.get_current_active_user)
):
    return current_user