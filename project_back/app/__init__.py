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
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(practice.router, prefix="/practice", tags=["practice"])
api_router.include_router(tags.router, tags=["tags"])
api_router.include_router(error_book.router, prefix="/error-book", tags=["error-book"])
api_router.include_router(question_bank.router, prefix="/question-bank", tags=["question-bank"])
api_router.include_router(question_bank.questions_router, prefix="/question-bank/questions", tags=["questions"])  # 完整路径
api_router.include_router(question_bank.questions_router, prefix="/questions", tags=["questions-short"])  # 简短别名
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(knowledge.router, prefix="/knowledge", tags=["knowledge"])

__all__ = ["api_router"]