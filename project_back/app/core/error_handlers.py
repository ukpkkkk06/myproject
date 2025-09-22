import logging
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi import HTTPException as FastAPIHTTPException
from sqlalchemy.exc import IntegrityError
from .exceptions import AppException

logger = logging.getLogger(__name__)

def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppException)
    async def _app_exception_handler(_: Request, exc: AppException):
        # 业务异常：按内置 code/status_code 返回
        return JSONResponse(
            status_code=exc.status_code,
            content={"code": exc.code, "message": exc.message, "data": exc.data},
        )

    @app.exception_handler(RequestValidationError)
    async def _validation_exception_handler(_: Request, exc: RequestValidationError):
        # 入参校验失败
        return JSONResponse(
            status_code=422,
            content={"code": 422, "message": "参数校验失败", "data": exc.errors()},
        )

    # 兼容 FastAPI 与 Starlette 两种 HTTPException
    @app.exception_handler(FastAPIHTTPException)
    async def _fastapi_http_exception_handler(_: Request, exc: FastAPIHTTPException):
        # FastAPI 的 HTTP 异常处理
        detail = exc.detail if isinstance(exc.detail, str) else "请求错误"
        return JSONResponse(
            status_code=exc.status_code,
            content={"code": exc.status_code, "message": detail},
        )

    @app.exception_handler(StarletteHTTPException)
    async def _starlette_http_exception_handler(_: Request, exc: StarletteHTTPException):
        # Starlette 的 HTTP 异常处理
        detail = exc.detail if isinstance(exc.detail, str) else "请求错误"
        return JSONResponse(
            status_code=exc.status_code,
            content={"code": exc.status_code, "message": detail},
        )

    @app.exception_handler(IntegrityError)
    async def _integrity_error_handler(_: Request, exc: IntegrityError):
        # 数据库唯一约束冲突
        return JSONResponse(
            status_code=400,
            content={"code": 400, "message": "唯一约束冲突"},
        )

    @app.exception_handler(Exception)
    async def _unhandled_exception_handler(_: Request, exc: Exception):
        # 未捕获异常：记录堆栈，避免泄漏内部细节
        logger.exception("Unhandled error: %s", exc)
        return JSONResponse(
            status_code=500,
            content={"code": 500, "message": "服务器内部错误"},
        )