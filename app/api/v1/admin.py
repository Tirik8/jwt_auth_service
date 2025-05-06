from fastapi import APIRouter, Depends
from app.core import security
from app.db import crud
from app.db.database import get_db
from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/users/{user_id}")
async def get_user_by_id(
    user_id: int,
    user_me: bool = Depends(security.is_superuser),
    db: Session = Depends(get_db),
):
    user = crud.get_user_by_id(db, id=user_id)
    return user
