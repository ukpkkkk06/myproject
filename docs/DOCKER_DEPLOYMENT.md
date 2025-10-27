# 🐳 Docker 部署指南

## 📋 功能特性

✅ **自动健康检查**：每30秒检查一次服务状态  
✅ **定期报活**：独立监控容器每5分钟向外报告状态  
✅ **资源监控**：实时监控CPU、内存、磁盘使用情况  
✅ **多阶段构建**：优化镜像大小  
✅ **非root用户运行**：增强安全性  

---

## 🚀 快速开始

### 1. 准备配置文件

编辑 `docker-compose.yml`，修改以下配置：

```yaml
environment:
  # 数据库密码
  - DATABASE_URL=mysql+pymysql://root:YOUR_PASSWORD@db:3306/myexam_db
  
  # JWT密钥（生产环境必须修改！）
  - JWT_SECRET=YOUR_SECRET_KEY_HERE
  
  # 可选：外部监控webhook（Slack、钉钉、企业微信等）
  - HEALTH_WEBHOOK_URL=https://your-webhook.com/api/health
```

### 2. 构建并启动

```bash
# 构建镜像
docker-compose build

# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f api
```

### 3. 验证健康检查

```bash
# 检查容器健康状态
docker ps
# STATUS列会显示 "healthy" 或 "unhealthy"

# 手动调用健康检查端点
curl http://localhost:8000/api/v1/health

# 查看监控容器日志（每5分钟输出）
docker-compose logs -f health-monitor
```

---

## 📊 健康检查端点

### `/api/v1/health` - 完整健康检查

返回服务状态、数据库连接、系统资源等信息：

```json
{
  "status": "ok",
  "timestamp": "2025-10-23T12:00:00",
  "service": "myexam-api",
  "database": "ok",
  "system": {
    "cpu_percent": 5.2,
    "memory_percent": 45.8,
    "memory_used_mb": 234.5,
    "disk_percent": 32.1,
    "disk_free_gb": 15.6
  },
  "process": {
    "pid": 1,
    "threads": 4
  }
}
```

### `/api/v1/ping` - 快速心跳

最快响应，不检查数据库：

```json
{
  "status": "ok",
  "timestamp": "2025-10-23T12:00:00",
  "message": "pong"
}
```

---

## 🔧 配置说明

### Docker健康检查参数

```dockerfile
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3
```

- `interval=30s`: 每30秒检查一次
- `timeout=5s`: 检查超时时间5秒
- `start-period=10s`: 启动后等待10秒再开始检查
- `retries=3`: 连续3次失败才标记为不健康

### 监控容器参数

```bash
python healthcheck.py monitor 300
```

- `monitor`: 监控模式（持续运行）
- `300`: 检查间隔（秒），300秒=5分钟

**可自定义间隔时间**：
```yaml
# docker-compose.yml
command: ["python", "healthcheck.py", "monitor", "180"]  # 改为3分钟
```

---

## 🌐 外部监控集成

### 方式1：Webhook推送

在 `docker-compose.yml` 中配置：

```yaml
environment:
  - HEALTH_WEBHOOK_URL=https://your-monitoring.com/webhook
```

监控容器会定期POST以下数据：

```json
{
  "timestamp": "2025-10-23T12:00:00",
  "service": "myexam-api",
  "health": {
    "status": "ok",
    "database": "ok",
    "system": { ... }
  }
}
```

### 方式2：Prometheus监控

如果使用Prometheus，可以：

1. 配置 `HEALTH_WEBHOOK_URL` 为 Prometheus Pushgateway
2. 或让Prometheus定期拉取 `/api/v1/health` 端点

示例 `prometheus.yml`:

```yaml
scrape_configs:
  - job_name: 'myexam-api'
    scrape_interval: 30s
    static_configs:
      - targets: ['myexam-api:8000']
    metrics_path: '/api/v1/health'
```

### 方式3：云监控平台

- **阿里云云监控**：配置自定义监控指标
- **AWS CloudWatch**：使用容器日志推送
- **Azure Monitor**：配置Application Insights

---

## 📦 生产环境部署建议

### 1. 资源限制

在 `docker-compose.yml` 中添加：

```yaml
services:
  api:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
        reservations:
          cpus: '0.5'
          memory: 512M
```

### 2. 日志管理

```yaml
services:
  api:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

### 3. 环境变量文件

创建 `.env` 文件（不提交到Git）：

```bash
# .env
MYSQL_ROOT_PASSWORD=your_strong_password
JWT_SECRET=your_jwt_secret_key_at_least_32_chars
HEALTH_WEBHOOK_URL=https://your-webhook.com/api
```

修改 `docker-compose.yml`：

```yaml
services:
  api:
    env_file:
      - .env
```

### 4. 数据备份

```bash
# 备份数据库
docker-compose exec db mysqldump -u root -p myexam_db > backup.sql

# 恢复数据库
docker-compose exec -T db mysql -u root -p myexam_db < backup.sql
```

---

## 🛠️ 常用命令

```bash
# 启动服务
docker-compose up -d

# 停止服务
docker-compose down

# 重启服务
docker-compose restart api

# 查看日志
docker-compose logs -f api
docker-compose logs -f health-monitor

# 查看健康状态
docker-compose ps

# 进入容器
docker-compose exec api bash

# 清理所有数据（谨慎使用！）
docker-compose down -v

# 重新构建镜像
docker-compose build --no-cache

# 更新并重启
docker-compose pull && docker-compose up -d
```

---

## 🐛 故障排查

### 容器状态为 "unhealthy"

```bash
# 1. 查看健康检查日志
docker inspect --format='{{json .State.Health}}' myexam-api | python -m json.tool

# 2. 手动执行健康检查
docker-compose exec api python healthcheck.py

# 3. 查看API日志
docker-compose logs --tail=100 api
```

### 数据库连接失败

```bash
# 检查数据库是否启动
docker-compose ps db

# 测试数据库连接
docker-compose exec db mysql -u root -p -e "SELECT 1"

# 查看数据库日志
docker-compose logs db
```

### 监控容器无输出

```bash
# 查看监控容器状态
docker-compose ps health-monitor

# 手动运行监控
docker-compose exec health-monitor python healthcheck.py monitor 60
```

---

## 📈 监控输出示例

正常运行时，`health-monitor` 容器每5分钟输出：

```
🚀 启动健康监控，检查间隔: 300秒
📍 健康检查URL: http://api:8000/api/v1/health
📡 外部报告URL: https://your-webhook.com/api/health

[2025-10-23 12:00:00] ✅ 健康 | DB:ok | CPU:5.2% | 内存:45.8%
✅ 报告已发送到外部监控系统: 200

[2025-10-23 12:05:00] ✅ 健康 | DB:ok | CPU:4.8% | 内存:46.2%
✅ 报告已发送到外部监控系统: 200

[2025-10-23 12:10:00] ❌ 异常 | URLError: Connection refused
⚠️ 发送外部报告失败: HTTP Error 500
```

---

## 🔐 安全建议

1. ✅ **修改默认密码**：数据库和JWT密钥
2. ✅ **使用非root用户运行**：已在Dockerfile中配置
3. ✅ **限制端口暴露**：只暴露必要的端口
4. ✅ **使用HTTPS**：生产环境配置Nginx反向代理
5. ✅ **定期更新镜像**：`docker-compose pull`

---

## 📞 支持

遇到问题？查看：
- 日志：`docker-compose logs -f`
- 健康状态：`curl http://localhost:8000/api/v1/health`
- 容器状态：`docker-compose ps`
