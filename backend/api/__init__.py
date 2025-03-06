from fastapi import APIRouter
from .routes.Capture import router as capture_router
from .routes.Auth import router as auth_router
from .routes.Query import router as query_router
from .routes.Config import router as settings_router

router = APIRouter()
router.include_router(capture_router)
router.include_router(auth_router)
router.include_router(query_router)
router.include_router(settings_router)

__all__ = ["router"]
