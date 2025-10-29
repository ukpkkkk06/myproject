# 项目总览（myproject）

本仓库为前后端与部署脚手架的一体化工程，包含基于 uni-app 的多端前端与基于 FastAPI 的后端服务，并提供容器化与 Nginx 反向代理配置。

## 目录结构

- frontend-mp/ 前端（uni-app + Vue3 + Vite）
- project_back/ 后端（FastAPI + SQLAlchemy + Alembic）
- docker/ 容器编排与 Nginx 示例配置
- deploy*.sh|.ps1|.bat 部署脚本（可选）
- docs/ 文档

## 前端（frontend-mp）

- 技术栈：uni-app 3.x、Vue 3、Vite、@dcloudio/vite-plugin-uni
- 入口文件：`src/main.js`，根组件：`src/App.vue`
- 路由与页面：`src/pages.json` 定义页面路径（如登录、注册、练习、错题本、题库等）
- API 封装：`src/utils/api.ts`
  - 基础地址与前缀：
    - `VITE_API_BASE_URL`（必配：后端基础地址，如 http://127.0.0.1:8000 或 https://your.domain）
    - `VITE_API_PREFIX`（默认 `/api/v1`）
  - 统一请求封装 `request()`，自动附带本地存储的 `Bearer token`
  - 主要业务接口：用户、练习（创建/答题/完成）、错题本、题库/题目、标签等
- 环境配置：
  - `.env.development` 示例：
    - `VITE_API_BASE_URL=http://192.168.167.140:8000`
    - `VITE_API_PREFIX=/api/v1`
  - `.env.production` 示例（需按生产实际修改）
- 开发与构建脚本：见 `package.json`，常用：
  - `npm run dev:h5`（H5 开发，Vite 默认端口 5173）
  - `npm run build:h5`（H5 构建）
  - 也支持各类小程序平台构建（`dev:mp-weixin` 等）

## 后端（project_back）

- 技术栈：FastAPI、Uvicorn、SQLAlchemy 2.x、Alembic、PyMySQL、python-jose（JWT）
- 入口：`app/main.py`，函数 `create_app()`
  - 默认开启 CORS（开发环境 `*`）
  - 根路由 `/` 返回 `{ "message": "Hello World" }`
  - 统一挂载 `api_router`（版本化路由以 `/api/v1` 为主）
- 配置：`app/core/config.py`
  - 优先从 `project_back/.env` 加载变量（已内置 dotenv 加载逻辑）
  - 关键变量：
    - `DATABASE_URL`（开发默认 sqlite，示例使用 MySQL：`mysql+pymysql://root:123456@127.0.0.1:3306/myexam_db?charset=utf8mb4`）
    - `ALLOW_ORIGINS`（CORS 白名单）
    - `JWT_SECRET`、`JWT_EXPIRE_MINUTES`
- 数据库会话：`app/db/session.py`（连接池配置已优化）
- 依赖：见 `requirements.txt`
- 健康检查：脚本位于 `scripts/health/healthcheck.py`，容器中默认检查 `/api/v1/health`

## 容器与部署（docker/）

- `docker-compose.yml`（开发/测试示例）
  - 服务：
    - `api`（映射 8000:8000）
    - `db`（MySQL8，映射 3306:3306）
    - `health-monitor`（可选：定时健康上报）
  - 后端需配置环境变量（注意替换密码、密钥）：`DATABASE_URL`、`JWT_SECRET`、`ALLOW_ORIGINS`、`HEALTH_CHECK_URL`
- `docker-compose.prod.yml`（生产示例）
  - 同上，但所有敏感变量需强密码/秘密，并且 `ALLOW_ORIGINS` 必须为你的实际域名
- Nginx 反向代理（`nginx.conf` 示例）
  - `/api/` 反向代理到 `http://localhost:8000`
  - `/health` 透传到 `/api/v1/health`
  - 可按需开启静态 H5 部署段落

## 本地开发（建议流程）

- 后端（Python 3.11）：
  1) 创建并激活虚拟环境
  2) 安装依赖：`pip install -r requirements.txt`
  3) 准备数据库：确保 `DATABASE_URL` 可用（MySQL 或 SQLite）
  4) 启动：`uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload`
- 前端（Node 18+）：
  1) `npm install`
  2) 配置 `.env.development` 的 `VITE_API_BASE_URL`
  3) 运行：`npm run dev:h5`（默认访问 http://localhost:5173）

> 若使用 Docker：进入 `docker/` 目录，按需选择 `docker-compose.yml` 或 `docker-compose.prod.yml`，先修改密码/密钥后再启动。

## 关键端口与路径

- API：`:8000`（容器与宿主映射）
- MySQL：`:3306`
- H5 开发：`:5173`（Vite 默认）
- 前端 API 地址由 `VITE_API_BASE_URL + VITE_API_PREFIX` 组成（默认 `/api/v1`）

## 必改项（生产）

- 前端：`frontend-mp/.env.production` 的 `VITE_API_BASE_URL`、`VITE_API_PREFIX`
- 后端：`project_back/.env.production` 的 `DATABASE_URL`、`JWT_SECRET`、`ALLOW_ORIGINS`
- Docker Compose：各处密码与密钥占位符
- Nginx：`server_name` 改为你的域名或公网 IP

## 参考文件（快速定位）

- 前端：
  - `frontend-mp/src/utils/api.ts`（API 封装与业务接口）
  - `frontend-mp/src/pages.json`（页面路由）
  - `frontend-mp/vite.config.js`（Vite/Uni 配置与别名）
- 后端：
  - `project_back/app/main.py`（应用入口/CORS/路由挂载）
  - `project_back/app/core/config.py`（配置加载）
  - `project_back/app/db/session.py`（DB 连接池）
  - `project_back/requirements.txt`（依赖）
- 部署：
  - `docker/docker-compose*.yml`（服务编排）
  - `docker/nginx.conf`（反向代理）

---

本文件旨在帮助快速理解工程结构与启动路径，后续可根据实际变更持续更新。