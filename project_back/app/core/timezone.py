"""
时区统一管理模块
统一使用 UTC+8 (北京时间)
"""
from datetime import datetime, timezone, timedelta

# 定义 UTC+8 时区
UTC8 = timezone(timedelta(hours=8))

def now() -> datetime:
    """
    获取当前时间(UTC+8, 无时区信息)
    返回 naive datetime 对象,兼容数据库存储
    """
    return datetime.now(UTC8).replace(tzinfo=None)

def now_with_tz() -> datetime:
    """
    获取当前时间(UTC+8, 带时区信息)
    返回 aware datetime 对象,用于时区转换
    """
    return datetime.now(UTC8)
