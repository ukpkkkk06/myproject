import os
import logging
from logging.handlers import RotatingFileHandler
from fastapi import FastAPI
from app.api.v1.endpoints import (
    health, users, auth, practice,
    error_book as error_book_endpoint,
    question_bank as question_bank_endpoint,
    tags as tags_endpoint,
)
from app.api.v1.endpoints import admin as admin_endpoint
from app.core.config import settings
from starlette.middleware.cors import CORSMiddleware
from app.core.error_handlers import register_exception_handlers

def setup_logging():
    log_dir = r"C:\Users\yjq\Desktop\myproject\project_back\logs"
    os.makedirs(log_dir, exist_ok=True)
    fmt = "%(asctime)s %(levelname)s [%(name)s] %(message)s"
    logging.basicConfig(level=logging.DEBUG, format=fmt)  # 控制台
    fh = RotatingFileHandler(os.path.join(log_dir, "app.log"), maxBytes=5*1024*1024, backupCount=2, encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(logging.Formatter(fmt))
    logging.getLogger().addHandler(fh)                   # 写文件

setup_logging()

def create_app() -> FastAPI:
    app = FastAPI(
        title="MyProject API",
        version="1.0.0",
    )
    register_exception_handlers(app)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOW_ORIGINS or ["http://localhost:5173", "http://127.0.0.1:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/")
    def root():
        return {"message": "Hello World"}

    # 仅挂载一次 /api/v1 前缀
    app.include_router(health.router,   prefix="/api/v1", tags=["health"])
    app.include_router(auth.router,     prefix="/api/v1", tags=["auth"])
    app.include_router(users.router,    prefix="/api/v1", tags=["users"])
    app.include_router(practice.router, prefix="/api/v1", tags=["practice"])
    app.include_router(tags_endpoint.router, prefix="/api/v1", tags=["tags"])
    app.include_router(error_book_endpoint.router, prefix="/api/v1", tags=["error-book"])
    app.include_router(question_bank_endpoint.router, prefix="/api/v1", tags=["question-bank"])
    # 新增：管理员接口
    app.include_router(admin_endpoint.router, prefix="/api/v1", tags=["admin"])

    return app

app = create_app()