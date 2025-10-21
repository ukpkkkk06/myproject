import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

DATABASE_URL = settings.DATABASE_URL  # 统一从配置读取

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
    future=True,
    # 🚀 内存优化：优化连接池配置
    pool_size=5,  # 默认连接池大小（降低以减少内存）
    max_overflow=10,  # 最大溢出连接数
    echo=False,  # 生产环境禁用SQL日志
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()