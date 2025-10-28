# 腾讯云服务器部署指南

## 一、需要修改的配置

### 1. 前端配置 (frontend-mp)

#### 方式一:使用环境变量(推荐)
创建 `.env.production` 文件:
```env
VITE_API_BASE_URL=https://你的域名或IP
VITE_API_PREFIX=/api/v1
```

#### 方式二:直接修改代码
修改 `frontend-mp/src/utils/api.ts` 第3-4行:
```typescript
const API_BASE = 'https://你的域名或IP'  // 改为你的服务器地址
const API_PREFIX = '/api/v1'
```

### 2. 后端配置 (project_back)

创建 `.env` 文件(或修改现有的):
```env
# 基本配置
APP_NAME=myexam-api
ENV=production
DEBUG=false

# 数据库配置
DATABASE_URL=mysql+pymysql://root:你的数据库密码@db:3306/myexam_db

# JWT 配置
JWT_SECRET=请生成一个强随机字符串
JWT_EXPIRE_MINUTES=1440

# CORS 配置 - 重要!
ALLOW_ORIGINS=https://你的域名,https://你的小程序域名

# 健康检查
HEALTH_CHECK_URL=http://api:8000/api/v1/health
```

### 3. Docker Compose 配置

修改 `docker/docker-compose.yml`:
- 将 `your_password` 改为强密码
- 将 `your_secret_key_here` 改为强随机字符串
- 配置正确的域名/IP

## 二、腾讯云服务器配置要求

### 推荐配置
- **CPU**: 2核以上
- **内存**: 4GB 以上
- **硬盘**: 40GB 以上
- **带宽**: 3Mbps 以上
- **操作系统**: Ubuntu 20.04/22.04 或 CentOS 7/8

### 需要开放的端口
- **80**: HTTP (如果使用 Nginx)
- **443**: HTTPS (强烈推荐配置 SSL)
- **8000**: API 服务 (可选,推荐通过 Nginx 反向代理)
- **22**: SSH 管理

## 三、部署步骤

### 第 1 步: 购买并配置服务器

1. 登录腾讯云控制台
2. 购买云服务器 CVM
3. 配置安全组规则,开放上述端口
4. 获取公网 IP

### 第 2 步: 连接服务器并安装环境

```bash
# SSH 连接服务器
ssh root@你的服务器IP

# 更新系统
apt update && apt upgrade -y  # Ubuntu
# 或
yum update -y  # CentOS

# 安装 Docker
curl -fsSL https://get.docker.com | sh
systemctl start docker
systemctl enable docker

# 安装 Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# 验证安装
docker --version
docker-compose --version
```

### 第 3 步: 上传项目代码

#### 方式一: 使用 Git (推荐)
```bash
# 在服务器上
cd /opt
git clone https://github.com/ukpkkkk06/myproject.git
cd myproject
```

#### 方式二: 使用 SCP 上传
```powershell
# 在本地执行
scp -r C:\Users\yjq\Desktop\myproject root@你的服务器IP:/opt/
```

### 第 4 步: 配置环境变量

```bash
cd /opt/myproject/project_back

# 创建 .env 文件
cat > .env << 'EOF'
APP_NAME=myexam-api
ENV=production
DEBUG=false
DATABASE_URL=mysql+pymysql://root:你的数据库密码@db:3306/myexam_db
JWT_SECRET=你的JWT密钥
JWT_EXPIRE_MINUTES=1440
ALLOW_ORIGINS=https://你的域名
HEALTH_CHECK_URL=http://api:8000/api/v1/health
EOF

# 修改 docker-compose.yml 中的密码
cd /opt/myproject/docker
# 使用 vim 或 nano 编辑 docker-compose.yml
```

### 第 5 步: 启动服务

```bash
cd /opt/myproject/docker

# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 检查服务状态
docker-compose ps
```

### 第 6 步: 初始化数据库

```bash
# 进入 API 容器
docker exec -it myexam-api bash

# 运行数据库迁移
alembic upgrade head

# 退出容器
exit
```

### 第 7 步: 配置 Nginx 反向代理 (可选但推荐)

```bash
# 安装 Nginx
apt install nginx -y  # Ubuntu
# 或
yum install nginx -y  # CentOS

# 创建配置文件
cat > /etc/nginx/sites-available/myexam << 'EOF'
server {
    listen 80;
    server_name 你的域名或IP;

    # 前端静态文件 (如果有)
    location / {
        root /opt/myproject/frontend-mp/dist;
        try_files $uri $uri/ /index.html;
    }

    # API 反向代理
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket 支持 (如果需要)
    location /ws/ {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
EOF

# 启用配置
ln -s /etc/nginx/sites-available/myexam /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx
systemctl enable nginx
```

### 第 8 步: 配置 SSL 证书 (强烈推荐)

```bash
# 安装 Certbot
apt install certbot python3-certbot-nginx -y

# 获取免费 SSL 证书
certbot --nginx -d 你的域名

# 自动续期
certbot renew --dry-run
```

## 四、前端小程序配置

### 1. 配置服务器域名
在微信公众平台 → 开发 → 开发管理 → 服务器域名中添加:
- request合法域名: `https://你的域名`
- uploadFile合法域名: `https://你的域名`
- downloadFile合法域名: `https://你的域名`

### 2. 修改前端配置
```bash
cd frontend-mp

# 创建生产环境配置
cat > .env.production << 'EOF'
VITE_API_BASE_URL=https://你的域名
VITE_API_PREFIX=/api/v1
EOF

# 构建生产版本
npm run build:mp-weixin
```

## 五、常用运维命令

```bash
# 查看所有容器状态
docker-compose ps

# 查看日志
docker-compose logs -f api
docker-compose logs -f db

# 重启服务
docker-compose restart

# 停止服务
docker-compose down

# 更新代码后重新部署
git pull
docker-compose down
docker-compose build
docker-compose up -d

# 备份数据库
docker exec myexam-db mysqldump -uroot -p你的密码 myexam_db > backup_$(date +%Y%m%d).sql

# 查看资源使用
docker stats
```

## 六、安全建议

1. **修改 SSH 端口**: 将默认的 22 端口改为其他端口
2. **禁用 root 登录**: 创建普通用户,禁止 root 直接登录
3. **配置防火墙**: 使用 ufw 或 firewalld
4. **定期备份**: 设置自动备份数据库和代码
5. **监控告警**: 配置监控系统(如 Prometheus + Grafana)
6. **使用强密码**: 数据库、JWT 密钥都要用强随机字符串
7. **开启 HTTPS**: 必须配置 SSL 证书

## 七、故障排查

### API 无法访问
```bash
# 检查容器状态
docker-compose ps

# 检查日志
docker-compose logs api

# 检查端口占用
netstat -tunlp | grep 8000

# 检查防火墙
ufw status
```

### 数据库连接失败
```bash
# 检查数据库容器
docker-compose logs db

# 进入数据库容器测试
docker exec -it myexam-db mysql -uroot -p

# 检查数据库配置
docker exec myexam-api env | grep DATABASE
```

### 前端无法调用 API
1. 检查 CORS 配置
2. 检查域名是否正确
3. 检查微信小程序服务器域名配置
4. 查看浏览器/小程序开发工具控制台错误

## 八、性能优化建议

1. **使用 CDN**: 静态资源使用腾讯云 CDN
2. **数据库优化**: 添加索引,优化查询
3. **Redis 缓存**: 添加 Redis 缓存热点数据
4. **负载均衡**: 流量大时使用腾讯云 CLB
5. **监控告警**: 配置云监控和告警策略

---

## 快速检查清单

- [ ] 服务器已购买并配置好安全组
- [ ] Docker 和 Docker Compose 已安装
- [ ] 项目代码已上传到服务器
- [ ] `.env` 文件已正确配置(密码、密钥等)
- [ ] `docker-compose.yml` 中的密码已修改
- [ ] 前端 API 地址已修改为服务器地址
- [ ] 数据库迁移已运行
- [ ] 服务已启动(docker-compose up -d)
- [ ] Nginx 反向代理已配置(可选)
- [ ] SSL 证书已配置
- [ ] 微信小程序服务器域名已添加
- [ ] 防火墙规则已配置
- [ ] 定期备份已设置
