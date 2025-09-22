from fastapi import FastAPI, APIRouter
from app.api.v1.endpoints import health, users, auth
from app.api.deps import get_current_user
from app.models.user import User
import logging
from app.core.config import settings
from starlette.middleware.cors import CORSMiddleware
from app.core.error_handlers import register_exception_handlers

app = FastAPI(title=settings.APP_NAME)
register_exception_handlers(app)

# 统一日志格式
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)

# CORS 允许来源由配置控制
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

api = APIRouter(prefix="/api/v1")
api.include_router(health.router, tags=["health"])
api.include_router(auth.router, tags=["auth"])
api.include_router(users.router, tags=["users"])  # 先不强制鉴权；需要时给路由/函数加 dependencies=[Depends(get_current_user)]

app.include_router(api)