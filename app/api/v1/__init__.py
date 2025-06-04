from fastapi import APIRouter

from . import auth, users, admin, twofa


router = APIRouter()

router.include_router(auth.router, prefix="/auth", tags=["Auth"])
router.include_router(users.router, prefix="/users/me", tags=["Users"])
router.include_router(admin.router, prefix="/admin", tags=["Admin"])
router.include_router(twofa.router, prefix="/2fa", tags=["2fa"])
