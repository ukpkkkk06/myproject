@echo off
REM 🚀 Docker部署一键启动脚本 (Windows)

echo 🐳 ===== MyExam Docker 部署 =====
echo.

REM 检查Docker
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker未安装，请先安装Docker Desktop
    pause
    exit /b 1
)

docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker Compose未安装，请先安装Docker Compose
    pause
    exit /b 1
)

echo ✅ Docker环境检查通过
echo.

REM 检查配置文件
if not exist "docker\docker-compose.yml" (
    echo ❌ 找不到 docker\docker-compose.yml 文件
    pause
    exit /b 1
)

REM 提示修改配置
echo ⚠️  请确认你已经修改了以下配置：
echo    1. 数据库密码 (DATABASE_URL, MYSQL_ROOT_PASSWORD)
echo    2. JWT密钥 (JWT_SECRET)
echo    3. 外部监控URL (HEALTH_WEBHOOK_URL) [可选]
echo.
set /p CONFIRM="已确认配置？(y/n): "
if /i not "%CONFIRM%"=="y" (
    echo 请先编辑 docker\docker-compose.yml 文件
    pause
    exit /b 1
)

REM 构建镜像
echo.
echo 📦 开始构建镜像...
docker-compose -f docker\docker-compose.yml build

REM 启动服务
echo.
echo 🚀 启动服务...
docker-compose -f docker\docker-compose.yml up -d

REM 等待服务启动
echo.
echo ⏳ 等待服务启动（最多60秒）...
timeout /t 10 /nobreak >nul

REM 检查健康状态
set ATTEMPT=0
set MAX_ATTEMPTS=12

:HEALTH_CHECK
docker inspect --format="{{.State.Health.Status}}" myexam-api 2>nul | findstr "healthy" >nul
if %errorlevel% equ 0 (
    echo ✅ 服务已启动并健康
    goto DEPLOY_SUCCESS
)

set /a ATTEMPT+=1
if %ATTEMPT% geq %MAX_ATTEMPTS% (
    echo ⚠️ 服务启动超时，请检查日志：
    echo    docker-compose logs api
    pause
    exit /b 1
)

echo 等待中... (%ATTEMPT%/%MAX_ATTEMPTS%)
timeout /t 5 /nobreak >nul
goto HEALTH_CHECK

:DEPLOY_SUCCESS
echo.
echo 🎉 ===== 部署成功！ =====
echo.
echo 📍 服务地址：
echo    - API: http://localhost:8000
echo    - 健康检查: http://localhost:8000/api/v1/health
echo    - API文档: http://localhost:8000/docs
echo.
echo 📊 查看服务状态：
echo    docker-compose -f docker\docker-compose.yml ps
echo.
echo 📋 查看日志：
echo    docker-compose -f docker\docker-compose.yml logs -f api              # API日志
echo    docker-compose -f docker\docker-compose.yml logs -f health-monitor   # 监控日志
echo.
echo 🛑 停止服务：
echo    docker-compose -f docker\docker-compose.yml down
echo.
echo 💡 提示：监控容器每5分钟输出一次健康状态
echo.
pause
