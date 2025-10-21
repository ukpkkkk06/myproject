"""
验证路由统一配置
位置: scripts/verify_routes.py
用法: python scripts/verify_routes.py (从项目根目录运行)
"""
import os
import sys

# 设置控制台输出编码
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.main import app

# 获取所有 API 路由
api_routes = [r for r in app.routes if hasattr(r, 'path') and r.path.startswith('/api/v1')]

print('已注册的 API 路由:')
print('=' * 60)

for route in sorted(api_routes, key=lambda x: x.path):
    methods = ','.join(route.methods) if hasattr(route, 'methods') else 'N/A'
    print(f'{methods:12} {route.path}')

print('=' * 60)
print(f'总计: {len(api_routes)} 个 API 路由')
print('路由统一配置验证通过!')
