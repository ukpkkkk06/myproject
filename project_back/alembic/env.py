import os, sys
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

# 允许导入 app 包
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
sys.path.append(PROJECT_ROOT)

# 读项目配置
from app.core.config import settings
from app.db.base import Base
import app.models  # 关键：确保模型被导入，填充 Base.metadata

# 这行用于 alembic.ini 的日志配置
config = context.config
fileConfig(config.config_file_name)

# 使用应用的数据库 URL
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

target_metadata = Base.metadata

def include_object(object, name, type_, reflected, compare_to):
    # 可选：忽略仅存在于数据库、但不在模型中的对象，避免生成删表/删索引
    if type_ == "table" and reflected and compare_to is None:
        return False
    if type_ in {"index", "unique_constraint", "foreign_key_constraint"} and reflected and compare_to is None:
        return False
    return True

def run_migrations_offline() -> None:
    context.configure(
        url=settings.DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
        compare_server_default=True,
        include_object=include_object
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_object=include_object,
            compare_type=True,
            compare_server_default=True,
        )
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()