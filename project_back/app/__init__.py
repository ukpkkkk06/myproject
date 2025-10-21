"""
统一的路由配置中心
所有 API 路由在此集中管理
"""
from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth,
    users,
    health,
    practice,
    error_book,
    question_bank,
    admin,
    tags,
    knowledge,
)

# 创建 API v1 路由器
api_router = APIRouter(prefix="/api/v1")

# 注册所有子路由
api_router.include_router(health.router, tags=["health"])
api_router.include_router(auth.router, tags=["auth"])
api_router.include_router(users.router, tags=["users"])
api_router.include_router(practice.router, tags=["practice"])
api_router.include_router(tags.router, tags=["tags"])
api_router.include_router(error_book.router, prefix="/error-book", tags=["error-book"])
api_router.include_router(question_bank.router, tags=["question-bank"])
api_router.include_router(admin.router, tags=["admin"])
api_router.include_router(knowledge.router, tags=["knowledge"])

__all__ = ["api_router"]