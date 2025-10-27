#!/bin/bash
# 🚀 Docker部署一键启动脚本

set -e

echo "🐳 ===== MyExam Docker 部署 ====="
echo ""

# 检查Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker未安装，请先安装Docker"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose未安装，请先安装Docker Compose"
    exit 1
fi

echo "✅ Docker环境检查通过"
echo ""

# 检查配置文件
if [ ! -f "docker/docker-compose.yml" ]; then
    echo "❌ 找不到 docker/docker-compose.yml 文件"
    exit 1
fi

# 提示修改配置
echo "⚠️  请确认你已经修改了以下配置："
echo "   1. 数据库密码 (DATABASE_URL, MYSQL_ROOT_PASSWORD)"
echo "   2. JWT密钥 (JWT_SECRET)"
echo "   3. 外部监控URL (HEALTH_WEBHOOK_URL) [可选]"
echo ""
read -p "已确认配置？(y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "请先编辑 docker/docker-compose.yml 文件"
    exit 1
fi

# 构建镜像
echo ""
echo "📦 开始构建镜像..."
docker-compose -f docker/docker-compose.yml build

# 启动服务
echo ""
echo "🚀 启动服务..."
docker-compose -f docker/docker-compose.yml up -d

# 等待服务启动
echo ""
echo "⏳ 等待服务启动（最多60秒）..."
sleep 10

# 检查健康状态
MAX_ATTEMPTS=12
ATTEMPT=0
while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
    HEALTH=$(docker inspect --format='{{.State.Health.Status}}' myexam-api 2>/dev/null || echo "starting")
    
    if [ "$HEALTH" = "healthy" ]; then
        echo "✅ 服务已启动并健康"
        break
    fi
    
    ATTEMPT=$((ATTEMPT+1))
    echo "等待中... ($ATTEMPT/$MAX_ATTEMPTS) 当前状态: $HEALTH"
    sleep 5
done

if [ $ATTEMPT -eq $MAX_ATTEMPTS ]; then
    echo "⚠️ 服务启动超时，请检查日志："
    echo "   docker-compose logs api"
else
    echo ""
    echo "🎉 ===== 部署成功！ ====="
    echo ""
    echo "📍 服务地址："
    echo "   - API: http://localhost:8000"
    echo "   - 健康检查: http://localhost:8000/api/v1/health"
    echo "   - API文档: http://localhost:8000/docs"
    echo ""
    echo "📊 查看服务状态："
    echo "   docker-compose -f docker/docker-compose.yml ps"
    echo ""
    echo "📋 查看日志："
    echo "   docker-compose -f docker/docker-compose.yml logs -f api              # API日志"
    echo "   docker-compose -f docker/docker-compose.yml logs -f health-monitor   # 监控日志"
    echo ""
    echo "🛑 停止服务："
    echo "   docker-compose -f docker/docker-compose.yml down"
    echo ""
    echo "💡 提示：监控容器每5分钟输出一次健康状态"
fi
