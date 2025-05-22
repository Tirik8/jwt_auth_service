from fastapi import APIRouter

from . import v1
from .root import router as root_router

router = APIRouter()

router.include_router(v1.router, prefix="/v1")
router.include_router(root_router, prefix="/")
