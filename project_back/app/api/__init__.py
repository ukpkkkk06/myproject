from fastapi import APIRouter

# 直接从 v1.endpoints 导入各 router
from .v1.endpoints.practice import router as practice_router
from .v1.endpoints.tags import router as tags_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(practice_router)
api_router.include_router(tags_router)

__all__ = ["api_router"]