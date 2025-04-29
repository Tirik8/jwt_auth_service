from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer
from app.core import security
from app.db import crud, models
from fastapi import Security
from app.db.database import get_db
from sqlalchemy.orm import Session

router = APIRouter(prefix="/users", tags=["users"])

security_scheme = HTTPBearer()

@router.get("/me", dependencies=[Security(security_scheme)])
async def read_users_me(
    current_user: models.User = Depends(security.get_current_active_user)
    ):
    return current_user

@router.get('/me/sessions')
async def get_sessions(
    current_user: models.User = Depends(security.get_current_active_user),
    db: Session = Depends(get_db)
):
    return crud.get_refresh_tokens(db, 5, current_user.id)

@router.get("/{user_id}")
async def get_user_by_id(
    user_id: int, 
    user_me: bool = Depends(security.is_superuser), 
    db: Session = Depends(get_db)
    ):
    user = crud.get_user_by_id(db, id=user_id)
    return user
