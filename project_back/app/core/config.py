from __future__ import annotations
import os
from pathlib import Path
from functools import lru_cache

# 可选加载 .env（未安装 python-dotenv 也不影响）
try:
    from dotenv import load_dotenv  # type: ignore
    # 🔧 修复：始终从 project_back 目录加载 .env
    project_root = Path(__file__).parent.parent.parent  # 定位到 project_back 目录
    env_path = project_root / '.env'
    load_dotenv(dotenv_path=env_path)
except Exception:
    pass

def _get(k: str, default: str | None = None) -> str | None:
    return os.getenv(k, default)

def _as_bool(v: str | None, default: bool = False) -> bool:
    if v is None:
        return default
    return str(v).lower() in ("1", "true", "yes", "on")

def _as_list(v: str | None) -> list[str]:
    if not v:
        return []
    return [s.strip() for s in v.split(",") if s.strip()]

class Settings:
    APP_NAME = _get("APP_NAME", "myexam-api")
    ENV = _get("ENV", "development")
    DEBUG = _as_bool(_get("DEBUG", "true"))
    DATABASE_URL = _get("DATABASE_URL", "sqlite:///./app.db")
    ALLOW_ORIGINS = _as_list(_get("ALLOW_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"))
    JWT_SECRET = _get("JWT_SECRET", "change_me_please")
    JWT_ALG = "HS256"
    JWT_EXPIRE_MINUTES = int(_get("JWT_EXPIRE_MINUTES", "60"))

@lru_cache
def get_settings() -> Settings:
    return Settings()

settings = get_settings()