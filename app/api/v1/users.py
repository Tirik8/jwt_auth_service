from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer
from app.core import security
from app.db import crud, models
from fastapi import Security
from app.db.database import get_db
from sqlalchemy.orm import Session

router = APIRouter()

security_scheme = HTTPBearer()

@router.get("", dependencies=[Security(security_scheme)])
async def read_users_me(
    current_user: models.User = Depends(security.get_current_active_user)
    ):
    return current_user


@router.put("")
async def write_users_me(
    current_user: models.User = Depends(security.get_current_active_user)
):
    pass


@router.get('/sessions')
async def get_sessions(
    current_user: models.User = Depends(security.get_current_active_user),
    db: Session = Depends(get_db)
):
    return crud.get_refresh_tokens(db, 5, current_user.id)


@router.delete("/sessions")
async def delete_sessions(
    current_user: models.User = Depends(security.get_current_active_user)
    ):
    pass


@router.patch("/password")
async def change_password(
    current_user: models.User = Depends(security.get_current_active_user)
    ):
    pass

