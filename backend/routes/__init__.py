from fastapi import APIRouter
from .Capture import router as capture_router
from .Auth import router as auth_router

router = APIRouter()
router.include_router(capture_router)
router.include_router(auth_router)

__all__ = ["router"]
