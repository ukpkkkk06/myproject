from fastapi import FastAPI, APIRouter
from app.api.v1.endpoints import health, users, auth
from app.api.deps import get_current_user
from app.models.user import User
import logging
from app.core.config import settings
from starlette.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from fastapi import Request, HTTPException

app = FastAPI(title=settings.APP_NAME)

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

@app.exception_handler(IntegrityError)
async def on_integrity_error(request: Request, exc: IntegrityError):
    return JSONResponse(status_code=400, content={"code": 400, "message": "唯一约束冲突"})

@app.exception_handler(HTTPException)
async def on_http_exception(request: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={"code": exc.status_code, "message": str(exc.detail)})

@app.exception_handler(Exception)
async def on_exception(request: Request, exc: Exception):
    logging.exception("Unhandled error", exc_info=exc)
    return JSONResponse(status_code=500, content={"code": 500, "message": "服务器内部错误"})

@app.on_event("startup")
def _debug_user_columns():
    logging.getLogger().info("User columns mapped => %s", [c.name for c in User.__table__.columns])

api = APIRouter(prefix="/api/v1")
api.include_router(health.router, tags=["health"])
api.include_router(auth.router, tags=["auth"])
api.include_router(users.router, tags=["users"])  # 先不强制鉴权；需要时给路由/函数加 dependencies=[Depends(get_current_user)]

app.include_router(api)