import os
import logging
from logging.handlers import RotatingFileHandler
from fastapi import FastAPI
from app import api_router  # 导入统一的路由配置
from app.core.config import settings
from starlette.middleware.cors import CORSMiddleware
from app.core.error_handlers import register_exception_handlers
import tracemalloc

# 开关：默认开启，设置为 0/false/off 可关闭
if os.getenv("ENABLE_TRACEMALLOC", "1").lower() in ("1", "true", "yes", "on"):
    if not tracemalloc.is_tracing():
        tracemalloc.start()

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
        allow_origins=["*"],  # 开发环境允许所有来源
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/")
    def root():
        return {"message": "Hello World"}

    # 统一挂载所有 API 路由
    app.include_router(api_router)

    return app

app = create_app()