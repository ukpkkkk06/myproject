# 🛠️ Scripts 工具目录

本目录包含项目的维护和检查工具脚本。

---

## 📋 可用脚本

### 1. check_references.py - 引用完整性检查

**功能**: 全面检查项目中的所有引用关系

**检查项目**:
- ✅ Python 模块导入
- ✅ API 路由注册
- ✅ 数据库表模型映射
- ✅ 空文件/冗余文件

**用法**:
```bash
# 从项目根目录运行
cd C:\Users\yjq\Desktop\myproject\project_back
python scripts/check_references.py
```

**输出示例**:
```
======================================================================
🔍 项目引用检查报告
======================================================================
✅ 所有检查通过！
```

---

### 2. verify_routes.py - API 路由验证

**功能**: 列出所有已注册的 API 路由

**用法**:
```bash
# 从项目根目录运行
cd C:\Users\yjq\Desktop\myproject\project_back
python scripts/verify_routes.py
```

**输出示例**:
```
📋 已注册的 API 路由:
============================================================
POST         /api/v1/auth/login
GET          /api/v1/health
...
============================================================
✅ 总计: 50 个 API 路由
```

---

### 3. create_indexes.py - 数据库索引创建

**功能**: 执行智能推荐功能所需的数据库索引创建

**状态**: ✅ 已执行完成（索引已创建）

**用法**:
```bash
# 从项目根目录运行
cd C:\Users\yjq\Desktop\myproject\project_back
python scripts/create_indexes.py
```

**注意**: 此脚本已经执行过，不需要重复运行

---

## 📝 开发新脚本指南

如果需要添加新的维护脚本，请遵循以下规范：

### 1. 脚本模板

```python
"""
脚本功能描述
位置: scripts/your_script.py
用法: python scripts/your_script.py
"""
import os
import sys

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 导入项目模块
from app.main import app
from app.models import User

def main():
    """主函数"""
    print("开始执行...")
    # 你的代码
    print("✅ 完成")

if __name__ == "__main__":
    main()
```

### 2. 命名规范

- 使用小写字母和下划线
- 描述性命名，如 `check_database.py`, `export_data.py`
- 避免使用数字开头

### 3. 文档要求

- 在文件顶部添加 docstring 说明功能和用法
- 添加必要的注释
- 更新本 README.md

---

## 🔧 常见任务

### 部署前检查
```bash
# 1. 检查引用完整性
python scripts/check_references.py

# 2. 验证路由
python scripts/verify_routes.py

# 3. 运行测试（如果有）
pytest
```

### 数据库维护
```bash
# 查看迁移状态
alembic current

# 升级到最新版本
alembic upgrade head

# 创建新的迁移
alembic revision --autogenerate -m "描述"
```

---

## ⚠️ 注意事项

1. **从项目根目录运行**: 所有脚本都应该从 `project_back/` 目录运行
2. **Python 环境**: 确保激活了正确的虚拟环境
3. **数据库连接**: 某些脚本需要数据库连接，确保 `.env` 配置正确
4. **备份数据**: 运行修改数据的脚本前先备份数据库

---

**维护者**: 开发团队  
**最后更新**: 2025-10-21
