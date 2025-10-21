# 📁 项目文档和脚本目录说明

本目录包含项目的文档和工具脚本的组织结构。

---

## 📂 目录结构

```
project_back/
├── docs/                    # 文档目录
│   ├── reports/            # 优化报告和修复记录
│   └── guides/             # 使用指南和功能文档
├── scripts/                # 工具脚本
├── sql/                    # SQL 脚本和数据库迁移
└── alembic/                # Alembic 数据库迁移
```

---

## 📊 docs/reports/ - 优化报告

历史优化和修复记录，用于追踪项目改进历史：

| 文档 | 说明 | 日期 |
|------|------|------|
| `OPTIMIZATION_SUMMARY.md` | 路由统一与索引优化总结 | 2025-10-21 |
| `ROUTE_AND_INDEX_OPTIMIZATION.md` | 路由和索引优化详细说明 | 2025-10-21 |
| `REFERENCE_CHECK_REPORT.md` | 项目引用完整性检查报告 | 2025-10-21 |
| `ADMIN_PERMISSION_FIX.md` | 管理员权限修复记录 | - |
| `KNOWLEDGE_BINDING_FIX.md` | 知识点绑定权限漏洞修复 | - |
| `KNOWLEDGE_PERMISSION_FIX.md` | 知识点权限修复 | - |
| `USER_API_PERMISSION_FIX.md` | 用户API权限修复 | - |
| `MEMORY_OPTIMIZATION.md` | 内存优化报告 | - |
| `MULTI_USER_SUPPORT.md` | 多用户支持实现 | - |
| `SECURITY_AUDIT_REPORT.md` | 安全审计报告 | - |

---

## 📚 docs/guides/ - 使用指南

功能使用和系统初始化指南：

| 文档 | 说明 |
|------|------|
| `ADMIN_INIT_GUIDE.md` | 管理员初始化测试指南 |
| `智能推荐功能文档.md` | 智能推荐算法说明 |

---

## 🛠️ scripts/ - 工具脚本

开发和维护工具：

| 脚本 | 说明 | 用法 |
|------|------|------|
| `check_references.py` | 检查项目引用完整性 | `python scripts/check_references.py` |
| `verify_routes.py` | 验证 API 路由注册 | `python scripts/verify_routes.py` |
| `create_indexes.py` | 创建数据库索引（已执行） | `python scripts/create_indexes.py` |

---

## 💾 sql/ - SQL 脚本

数据库初始化和迁移脚本：

| 脚本 | 说明 | 状态 |
|------|------|------|
| `00_init.sql` | 数据库初始化 | ✅ 已执行 |
| `create_database.sql` | 创建数据库 | ✅ 已执行 |
| `init_admin_role.sql` | 初始化管理员角色 | ✅ 已执行 |
| `add_knowledge_created_by.sql` | 添加知识点创建者字段 | ✅ 已执行 |
| `add_smart_recommendation_indexes.sql` | 智能推荐索引 | ✅ 已执行 |
| `remove_duplicate_indexes.sql` | 删除重复索引 | ✅ 已执行 |
| `fix_null_created_by.sql` | 修复空创建者 | ✅ 已执行 |
| `seed_practice.sql` | 练习数据种子 | 📋 可选 |
| `seed_question_knowledge.sql` | 题目知识点关联种子 | 📋 可选 |
| `test.sql` | 测试脚本 | ⚠️ 临时文件 |

---

## 📝 使用建议

### 查看历史优化记录
```bash
# 查看所有优化报告
ls docs/reports/

# 阅读特定报告
cat docs/reports/OPTIMIZATION_SUMMARY.md
```

### 运行检查脚本
```bash
# 检查项目引用
python scripts/check_references.py

# 验证路由
python scripts/verify_routes.py
```

### 数据库迁移
```bash
# 使用 Alembic 进行版本控制的迁移
alembic upgrade head

# 手动执行 SQL 脚本
mysql -u root -p myexam_db < sql/00_init.sql
```

---

## 🗂️ 文件归档原则

1. **docs/reports/** - 已完成的优化和修复记录
   - 按时间归档
   - 保留用于历史追溯
   - 不再主动维护

2. **docs/guides/** - 活跃的使用文档
   - 功能说明
   - 使用教程
   - 需要保持更新

3. **scripts/** - 可重复使用的工具
   - 自动化检查
   - 维护工具
   - 数据迁移辅助

4. **sql/** - 数据库相关
   - 初始化脚本
   - 迁移脚本
   - 按执行顺序命名

---

**整理日期**: 2025-10-21  
**整理原因**: 优化项目结构，分类管理文档和脚本
