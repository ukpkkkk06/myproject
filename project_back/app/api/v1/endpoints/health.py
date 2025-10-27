from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.session import get_db
from app.core.timezone import now
import os

router = APIRouter()

@router.get("/health")
def health(db: Session = Depends(get_db), response: Response = None):
    """
    健康检查端点 - 用于外部系统测活
    GET http://your-server:8000/api/v1/health
    
    返回格式：
    {
        "status": "healthy",  // 总体状态: healthy 或 unhealthy
        "timestamp": "2025-10-23T12:00:00",
        "service": "myexam-api",
        "checks": {
            "database": {
                "status": "healthy",
                "message": "数据库状态健康"
            },
            "system": {
                "status": "healthy", 
                "message": "系统状态健康",
                "details": {
                    "cpu_percent": 5.2,
                    "memory_percent": 45.8
                }
            }
        }
    }
    """
    checks = {}
    overall_healthy = True
    
    # 1. 检查数据库连接
    try:
        db.execute(text("SELECT 1"))
        checks["database"] = {
            "status": "healthy",
            "message": "数据库状态健康"
        }
    except Exception as e:
        checks["database"] = {
            "status": "unhealthy",
            "message": f"数据库连接失败: {type(e).__name__}",
            "error": str(e)
        }
        overall_healthy = False
    
    # 2. 检查系统资源
    try:
        # 尝试导入psutil，如果没有则跳过详细检查
        try:
            import psutil
            cpu = psutil.cpu_percent(interval=0.1)
            mem = psutil.virtual_memory()
            
            # 判断系统资源是否健康（CPU<80%, 内存<90%）
            is_system_healthy = cpu < 80 and mem.percent < 90
            
            if is_system_healthy:
                checks["system"] = {
                    "status": "healthy",
                    "message": "系统状态健康",
                    "details": {
                        "cpu_percent": round(cpu, 2),
                        "memory_percent": round(mem.percent, 2),
                        "memory_used_mb": round(mem.used / 1024 / 1024, 2)
                    }
                }
            else:
                checks["system"] = {
                    "status": "warning",
                    "message": f"系统资源紧张 (CPU:{cpu:.1f}%, 内存:{mem.percent:.1f}%)",
                    "details": {
                        "cpu_percent": round(cpu, 2),
                        "memory_percent": round(mem.percent, 2)
                    }
                }
                # 警告不影响整体健康状态，但会记录
        except ImportError:
            # psutil未安装，跳过详细检查
            checks["system"] = {
                "status": "healthy",
                "message": "系统状态健康 (简化检查)"
            }
            
    except Exception as e:
        checks["system"] = {
            "status": "unhealthy",
            "message": f"系统检查失败: {str(e)}"
        }
        overall_healthy = False
    
    # 3. 构建响应
    result = {
        "status": "healthy" if overall_healthy else "unhealthy",
        "timestamp": now().isoformat(),
        "service": "myexam-api",
        "checks": checks
    }
    
    # 如果不健康，返回503状态码
    if not overall_healthy and response:
        response.status_code = 503
    
    return result

@router.get("/ping")
def ping():
    """
    快速心跳检查 - 不检查数据库和系统，只确认服务可访问
    最快响应，用于简单的存活检查
    """
    return {
        "status": "ok",
        "timestamp": now().isoformat(),
        "message": "pong"
    }