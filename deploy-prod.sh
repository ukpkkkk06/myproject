#!/bin/bash
# 生产环境部署脚本
# 使用方法: ./deploy.sh [start|stop|restart|logs|backup]

set -e

PROJECT_ROOT="/opt/myproject"
COMPOSE_FILE="$PROJECT_ROOT/docker/docker-compose.prod.yml"
BACKUP_DIR="$PROJECT_ROOT/backups"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查必要的配置文件
check_config() {
    log_info "检查配置文件..."
    
    if [ ! -f "$PROJECT_ROOT/project_back/.env" ]; then
        log_error ".env 文件不存在!"
        log_warn "请复制 .env.production 并修改配置"
        exit 1
    fi
    
    if grep -q "YOUR_" "$PROJECT_ROOT/project_back/.env"; then
        log_error ".env 文件中仍有未修改的配置项(YOUR_*)"
        exit 1
    fi
    
    if grep -q "YOUR_" "$COMPOSE_FILE"; then
        log_error "docker-compose.prod.yml 中仍有未修改的配置项(YOUR_*)"
        exit 1
    fi
    
    log_info "配置文件检查通过 ✓"
}

# 启动服务
start() {
    log_info "启动服务..."
    check_config
    
    cd $PROJECT_ROOT/docker
    docker-compose -f docker-compose.prod.yml up -d
    
    log_info "等待服务启动..."
    sleep 10
    
    log_info "服务状态:"
    docker-compose -f docker-compose.prod.yml ps
    
    log_info "健康检查..."
    curl -f http://localhost:8000/api/v1/health || log_warn "健康检查失败,请查看日志"
    
    log_info "部署完成! ✓"
}

# 停止服务
stop() {
    log_info "停止服务..."
    cd $PROJECT_ROOT/docker
    docker-compose -f docker-compose.prod.yml down
    log_info "服务已停止 ✓"
}

# 重启服务
restart() {
    log_info "重启服务..."
    stop
    sleep 3
    start
}

# 查看日志
logs() {
    cd $PROJECT_ROOT/docker
    docker-compose -f docker-compose.prod.yml logs -f --tail=100 $1
}

# 备份数据库
backup() {
    log_info "开始备份数据库..."
    
    mkdir -p $BACKUP_DIR
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    BACKUP_FILE="$BACKUP_DIR/myexam_db_$TIMESTAMP.sql"
    
    # 从 .env 读取数据库密码
    DB_PASSWORD=$(grep MYSQL_ROOT_PASSWORD $PROJECT_ROOT/project_back/.env | cut -d'=' -f2)
    
    docker exec myexam-db mysqldump -uroot -p$DB_PASSWORD myexam_db > $BACKUP_FILE
    
    # 压缩备份
    gzip $BACKUP_FILE
    
    log_info "备份完成: ${BACKUP_FILE}.gz ✓"
    
    # 保留最近7天的备份
    find $BACKUP_DIR -name "*.sql.gz" -mtime +7 -delete
    log_info "已清理7天前的备份"
}

# 更新部署
update() {
    log_info "开始更新部署..."
    
    # 备份数据库
    backup
    
    # 拉取最新代码
    cd $PROJECT_ROOT
    log_info "拉取最新代码..."
    git pull
    
    # 重新构建并启动
    log_info "重新构建镜像..."
    cd $PROJECT_ROOT/docker
    docker-compose -f docker-compose.prod.yml build
    
    # 重启服务
    restart
    
    log_info "更新完成! ✓"
}

# 查看状态
status() {
    log_info "服务状态:"
    cd $PROJECT_ROOT/docker
    docker-compose -f docker-compose.prod.yml ps
    
    log_info "\n资源使用:"
    docker stats --no-stream myexam-api myexam-db
    
    log_info "\n健康检查:"
    curl -s http://localhost:8000/api/v1/health | python3 -m json.tool || log_error "健康检查失败"
}

# 进入容器
shell() {
    CONTAINER=${1:-myexam-api}
    log_info "进入容器: $CONTAINER"
    docker exec -it $CONTAINER /bin/bash
}

# 主函数
case "$1" in
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        restart
        ;;
    logs)
        logs $2
        ;;
    backup)
        backup
        ;;
    update)
        update
        ;;
    status)
        status
        ;;
    shell)
        shell $2
        ;;
    *)
        echo "使用方法: $0 {start|stop|restart|logs|backup|update|status|shell}"
        echo ""
        echo "命令说明:"
        echo "  start   - 启动所有服务"
        echo "  stop    - 停止所有服务"
        echo "  restart - 重启所有服务"
        echo "  logs    - 查看日志 (可选参数: api|db)"
        echo "  backup  - 备份数据库"
        echo "  update  - 更新代码并重新部署"
        echo "  status  - 查看服务状态"
        echo "  shell   - 进入容器 (可选参数: 容器名)"
        echo ""
        echo "示例:"
        echo "  $0 start          # 启动服务"
        echo "  $0 logs api       # 查看 API 日志"
        echo "  $0 shell myexam-api  # 进入 API 容器"
        exit 1
        ;;
esac

exit 0
