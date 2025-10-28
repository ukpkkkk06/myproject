# 📁 项目文件结构说明

## 🐳 Docker 部署相关文件

```
myproject/
├── docker/                          # Docker部署配置
│   └── docker-compose.yml          # 服务编排配置文件
│
├── project_back/                    # 后端项目
│   ├── docker/                     # Docker构建文件
│   │   ├── Dockerfile              # API镜像构建文件
│   │   └── .dockerignore           # Docker构建忽略文件
│   │
│   ├── scripts/                    # 脚本目录
│   │   └── health/                 # 健康检查相关脚本
│   │       ├── healthcheck.py      # 健康检查和监控脚本
│   │       └── test_health.py      # 健康检查测试脚本
│   │
│   ├── app/                        # 应用代码
│   ├── requirements.txt            # Python依赖
│   └── ...
│
├── docs/                            # 文档目录
│   └── DOCKER_DEPLOYMENT.md        # Docker部署详细文档
│
├── deploy.sh                        # Linux/Mac 部署脚本
└── deploy.bat                       # Windows 部署脚本
```

---

## 🚀 快速部署

### Windows 系统

```powershell
# 一键部署
.\deploy.bat
```

### Linux/Mac 系统

```bash
# 一键部署
chmod +x deploy.sh
./deploy.sh
```

---

## 📝 文件说明

### 核心配置文件

| 文件 | 说明 |
|------|------|
| `docker/docker-compose.yml` | 完整的服务编排配置，包含API、数据库、监控容器 |
| `project_back/docker/Dockerfile` | 后端API的Docker镜像构建文件 |
| `project_back/requirements.txt` | Python依赖列表（含psutil用于系统监控） |

### 健康检查文件

| 文件 | 说明 |
|------|------|
| `project_back/scripts/health/healthcheck.py` | 健康检查主脚本，支持单次检查和持续监控模式 |
| `project_back/scripts/health/test_health.py` | 本地测试健康检查功能的脚本 |

### 部署脚本

| 文件 | 说明 |
|------|------|
| `deploy.sh` | Linux/Mac 一键部署脚本 |
| `deploy.bat` | Windows 一键部署脚本 |

### 文档

| 文件 | 说明 |
|------|------|
| `docs/DOCKER_DEPLOYMENT.md` | 详细的Docker部署指南，包含配置说明、故障排查等 |

---

## 🔧 使用说明

### 1. 修改配置

编辑 `docker/docker-compose.yml`，修改以下内容：

```yaml
environment:
  # 必须修改：数据库密码
  - DATABASE_URL=mysql+pymysql://root:YOUR_PASSWORD@db:3306/myexam_db
  
  # 必须修改：JWT密钥（生产环境）
  - JWT_SECRET=YOUR_SECRET_KEY_HERE
  
  # 可选：外部监控webhook
  - HEALTH_WEBHOOK_URL=https://your-webhook.com/api/health
```

同时在db服务中修改：
```yaml
- MYSQL_ROOT_PASSWORD=YOUR_PASSWORD  # 与上面保持一致
```

### 2. 部署服务

运行部署脚本会自动完成：
- ✅ 检查Docker环境
- ✅ 构建镜像
- ✅ 启动服务
- ✅ 等待健康检查通过

### 3. 查看监控

监控容器每5分钟自动输出健康状态：

```bash
# Linux/Mac
docker-compose -f docker/docker-compose.yml logs -f health-monitor

# Windows
docker-compose -f docker\docker-compose.yml logs -f health-monitor
```

输出示例：
```
[2025-10-23 12:00:00] ✅ 健康 | DB:ok | CPU:5.2% | 内存:45.8%
```

---

## 🛠️ 常用命令

```bash
# 查看容器状态（会显示 healthy/unhealthy）
docker-compose -f docker/docker-compose.yml ps

# 查看API日志
docker-compose -f docker/docker-compose.yml logs -f api

# 查看监控日志
docker-compose -f docker/docker-compose.yml logs -f health-monitor

# 重启服务
docker-compose -f docker/docker-compose.yml restart api

# 停止服务
docker-compose -f docker/docker-compose.yml down

# 停止并清理数据（谨慎！）
docker-compose -f docker/docker-compose.yml down -v
```

---

## 🔍 本地测试健康检查

在部署前可以先本地测试：

```bash
# 1. 启动后端服务
cd project_back
uvicorn app.main:app --reload

# 2. 在另一个终端运行测试
python scripts/health/test_health.py
```

---

## 🌐 健康检查端点

- `http://localhost:8000/api/v1/health` - 完整健康检查（含系统资源）
- `http://localhost:8000/api/v1/ping` - 快速心跳检查

---

## 📚 更多信息

详细的部署说明、配置参数、故障排查等，请查看：
- 📖 [Docker部署完整文档](docs/DOCKER_DEPLOYMENT.md)

---

## 💡 提示

1. **首次部署**：必须修改数据库密码和JWT密钥
2. **监控间隔**：默认5分钟，可在 `docker-compose.yml` 中修改
3. **外部监控**：配置 `HEALTH_WEBHOOK_URL` 可推送到钉钉、企业微信、Slack等
4. **生产环境**：建议配置资源限制和HTTPS反向代理

---

## 🆘 遇到问题？

1. 查看日志：`docker-compose -f docker/docker-compose.yml logs`
2. 检查健康：`curl http://localhost:8000/api/v1/health`
3. 查看文档：`docs/DOCKER_DEPLOYMENT.md`
