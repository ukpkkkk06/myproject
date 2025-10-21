# 📁 项目后端目录结构

智能题库系统 - 后端服务

---

## 🏗️ 目录结构

```
project_back/
├── app/                    # 应用主代码
│   ├── api/               # API 路由
│   │   ├── deps.py       # 依赖注入
│   │   └── v1/           # API v1 版本
│   │       └── endpoints/ # 路由端点
│   ├── core/             # 核心配置
│   ├── db/               # 数据库配置
│   ├── models/           # 数据模型 (SQLAlchemy)
│   ├── schemas/          # 数据模式 (Pydantic)
│   └── services/         # 业务逻辑服务
├── docs/                  # 📚 文档目录
│   ├── reports/          # 优化和修复报告
│   ├── guides/           # 使用指南
│   └── README.md         # 文档目录说明
├── scripts/               # 🛠️ 工具脚本
│   ├── check_references.py   # 引用检查
│   ├── verify_routes.py      # 路由验证
│   └── README.md             # 脚本使用说明
├── sql/                   # 💾 SQL 脚本
│   ├── README.md         # SQL 脚本说明
│   ├── 00_init.sql       # 数据库表结构初始化
│   ├── create_database.sql # 创建数据库
│   ├── migrations/       # 🔄 历史迁移脚本 (已执行)
│   └── seeds/            # 🌱 测试数据脚本
├── alembic/              # 🔄 数据库迁移 (Alembic)
├── logs/                 # 📋 日志文件
├── .env                  # 🔐 环境配置
├── alembic.ini           # Alembic 配置
└── Import template.xlsx  # 📊 题目导入模板
```

---

## 🚀 快速开始

### 1. 安装依赖

```bash
# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境 (Windows)
.venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置环境

编辑 `.env` 文件：
```env
DATABASE_URL=mysql+pymysql://root:password@localhost:3306/myexam_db
JWT_SECRET=your-secret-key
```

### 3. 初始化数据库

```bash
# 运行数据库迁移
alembic upgrade head

# 或手动执行 SQL
mysql -u root -p < sql/00_init.sql
```

### 4. 启动服务

```bash
# 开发模式
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# 生产模式
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

访问: http://127.0.0.1:8000/docs (Swagger UI)

---

## 📚 文档

- **[docs/README.md](docs/README.md)** - 文档目录说明
- **[scripts/README.md](scripts/README.md)** - 工具脚本使用

### 主要文档

| 文档 | 说明 |
|------|------|
| [OPTIMIZATION_SUMMARY.md](docs/reports/OPTIMIZATION_SUMMARY.md) | 优化总结 |
| [REFERENCE_CHECK_REPORT.md](docs/reports/REFERENCE_CHECK_REPORT.md) | 引用检查报告 |
| [ADMIN_INIT_GUIDE.md](docs/guides/ADMIN_INIT_GUIDE.md) | 管理员初始化指南 |
| [智能推荐功能文档.md](docs/guides/智能推荐功能文档.md) | 智能推荐算法 |

---

## 🛠️ 常用命令

### 开发检查

```bash
# 检查项目引用完整性
python scripts/check_references.py

# 验证 API 路由
python scripts/verify_routes.py

# 查看所有路由
python -m uvicorn app.main:app --reload
```

### 数据库迁移

```bash
# 查看当前版本
alembic current

# 升级到最新版本
alembic upgrade head

# 创建新的迁移
alembic revision --autogenerate -m "描述"

# 回退迁移
alembic downgrade -1
```

### 测试

```bash
# 运行测试 (如果配置了)
pytest

# 测试覆盖率
pytest --cov=app
```

---

## 🏗️ 技术栈

- **框架**: FastAPI
- **数据库**: MySQL 8.0
- **ORM**: SQLAlchemy
- **验证**: Pydantic
- **迁移**: Alembic
- **认证**: JWT (python-jose)
- **密码**: passlib + bcrypt

---

## 📋 API 端点

### 认证
- `POST /api/v1/login` - 登录
- `POST /api/v1/register` - 注册
- `GET /api/v1/me` - 当前用户信息

### 题库管理
- `GET /api/v1/question-bank/my-questions` - 我的题目
- `POST /api/v1/question-bank/import-excel` - 导入题目
- `GET /api/v1/question-bank/questions/{id}` - 题目详情
- `PUT /api/v1/question-bank/questions/{id}` - 更新题目

### 练习模式
- `POST /api/v1/practice/sessions` - 创建练习
- `GET /api/v1/practice/sessions/{id}/questions/{seq}` - 获取题目
- `POST /api/v1/practice/sessions/{id}/answers` - 提交答案

### 错题本
- `GET /api/v1/error-book` - 错题列表
- `POST /api/v1/error-book/{id}/record` - 记录错题
- `PATCH /api/v1/error-book/{id}/master` - 标记掌握

### 知识点
- `GET /api/v1/knowledge/tree` - 知识点树
- `POST /api/v1/knowledge` - 创建知识点
- `PUT /api/v1/questions/{id}/knowledge` - 绑定知识点

完整 API 文档: http://127.0.0.1:8000/docs

---

## 🔒 权限说明

系统支持两种角色：
- **ADMIN**: 管理员，可以访问和管理所有数据
- **USER**: 普通用户，只能访问自己的数据

第一个注册的用户自动成为管理员。

---

## 📝 开发规范

### 代码结构
- `models/` - 数据库模型，一个文件对应一个表
- `schemas/` - API 输入输出模式
- `services/` - 业务逻辑，不包含路由
- `api/v1/endpoints/` - 路由定义，调用 services

### 命名规范
- 文件名: 小写 + 下划线 (例: `user_service.py`)
- 类名: 大驼峰 (例: `UserService`)
- 函数名: 小写 + 下划线 (例: `get_user_by_id`)
- 常量: 大写 + 下划线 (例: `MAX_LOGIN_ATTEMPTS`)

### 提交规范
```
feat: 添加新功能
fix: 修复bug
docs: 文档更新
refactor: 代码重构
test: 测试相关
chore: 构建/工具相关
```

---

## 🐛 故障排查

### 数据库连接失败
1. 检查 `.env` 中的 `DATABASE_URL`
2. 确认 MySQL 服务已启动
3. 验证数据库和用户权限

### 导入错误
1. 确保在项目根目录运行命令
2. 检查虚拟环境是否激活
3. 运行 `python scripts/check_references.py` 检查引用

### 路由404
1. 检查路由是否在 `app/__init__.py` 中注册
2. 运行 `python scripts/verify_routes.py` 验证路由
3. 查看 `/docs` 确认 API 路径

---

## 📧 联系方式

- **项目**: MyProject API
- **版本**: 1.0.0
- **维护**: 开发团队

---

**最后更新**: 2025-10-21
