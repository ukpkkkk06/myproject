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

api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["健康检查"])
api_router.include_router(auth.router, prefix="", tags=["认证"])
api_router.include_router(users.router, prefix="/users", tags=["用户"])
api_router.include_router(practice.router, prefix="/practice", tags=["练习"])
api_router.include_router(error_book.router, prefix="/error-book", tags=["错题本"])
api_router.include_router(question_bank.router, prefix="/question-bank", tags=["题库"])
api_router.include_router(admin.router, prefix="/admin", tags=["管理后台"])
api_router.include_router(tags.router, prefix="/tags", tags=["标签"])
api_router.include_router(knowledge.router, prefix="/knowledge", tags=["知识点"])