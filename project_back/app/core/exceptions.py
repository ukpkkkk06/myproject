from typing import Any, Optional

class AppException(Exception):
    """业务异常，统一在全局异常处理里转成一致的返回体"""
    def __init__(self, message: str, *, code: int = 400, status_code: int = 400, data: Optional[Any] = None):
        self.code = code
        self.status_code = status_code
        self.message = message
        self.data = data
        super().__init__(message)

class NotFoundException(AppException):
    def __init__(self, message: str = "资源不存在", data: Optional[Any] = None):
        super().__init__(message, code=404, status_code=404, data=data)

class UnauthorizedException(AppException):
    def __init__(self, message: str = "未授权", data: Optional[Any] = None):
        super().__init__(message, code=401, status_code=401, data=data)

class ForbiddenException(AppException):
    def __init__(self, message: str = "无权限", data: Optional[Any] = None):
        super().__init__(message, code=403, status_code=403, data=data)

class ConflictException(AppException):
    def __init__(self, message: str = "资源冲突", data: Optional[Any] = None):
        super().__init__(message, code=409, status_code=409, data=data)
