# 生产环境部署脚本 (PowerShell)
# 使用方法: .\deploy-prod.ps1 [start|stop|restart|logs|backup]

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet('start','stop','restart','logs','backup','update','status','shell')]
    [string]$Action = 'help',
    
    [Parameter(Mandatory=$false)]
    [string]$Container = 'myexam-api'
)

$ErrorActionPreference = "Stop"

$ProjectRoot = "C:\myproject"  # ⚠️ 修改为服务器上的实际路径
$ComposeFile = "$ProjectRoot\docker\docker-compose.prod.yml"
$BackupDir = "$ProjectRoot\backups"

function Write-ColorOutput {
    param([string]$Message, [string]$Color = 'Green')
    Write-Host $Message -ForegroundColor $Color
}

function Check-Config {
    Write-ColorOutput "检查配置文件..." "Cyan"
    
    if (-not (Test-Path "$ProjectRoot\project_back\.env")) {
        Write-ColorOutput ".env 文件不存在!" "Red"
        Write-ColorOutput "请复制 .env.production 并修改配置" "Yellow"
        exit 1
    }
    
    $envContent = Get-Content "$ProjectRoot\project_back\.env" -Raw
    if ($envContent -match "YOUR_") {
        Write-ColorOutput ".env 文件中仍有未修改的配置项(YOUR_*)" "Red"
        exit 1
    }
    
    Write-ColorOutput "配置文件检查通过 ✓" "Green"
}

function Start-Services {
    Write-ColorOutput "启动服务..." "Cyan"
    Check-Config
    
    Set-Location "$ProjectRoot\docker"
    docker-compose -f docker-compose.prod.yml up -d
    
    Write-ColorOutput "等待服务启动..." "Cyan"
    Start-Sleep -Seconds 10
    
    Write-ColorOutput "服务状态:" "Cyan"
    docker-compose -f docker-compose.prod.yml ps
    
    Write-ColorOutput "健康检查..." "Cyan"
    try {
        Invoke-RestMethod -Uri "http://localhost:8000/api/v1/health"
        Write-ColorOutput "健康检查通过 ✓" "Green"
    } catch {
        Write-ColorOutput "健康检查失败,请查看日志" "Yellow"
    }
    
    Write-ColorOutput "部署完成! ✓" "Green"
}

function Stop-Services {
    Write-ColorOutput "停止服务..." "Cyan"
    Set-Location "$ProjectRoot\docker"
    docker-compose -f docker-compose.prod.yml down
    Write-ColorOutput "服务已停止 ✓" "Green"
}

function Restart-Services {
    Write-ColorOutput "重启服务..." "Cyan"
    Stop-Services
    Start-Sleep -Seconds 3
    Start-Services
}

function Show-Logs {
    Set-Location "$ProjectRoot\docker"
    docker-compose -f docker-compose.prod.yml logs -f --tail=100 $Container
}

function Backup-Database {
    Write-ColorOutput "开始备份数据库..." "Cyan"
    
    if (-not (Test-Path $BackupDir)) {
        New-Item -ItemType Directory -Path $BackupDir | Out-Null
    }
    
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $backupFile = "$BackupDir\myexam_db_$timestamp.sql"
    
    # 从 .env 读取数据库密码
    $envContent = Get-Content "$ProjectRoot\project_back\.env"
    $dbPassword = ($envContent | Select-String "MYSQL_ROOT_PASSWORD=(.+)").Matches.Groups[1].Value
    
    docker exec myexam-db mysqldump -uroot -p$dbPassword myexam_db > $backupFile
    
    # 压缩备份
    Compress-Archive -Path $backupFile -DestinationPath "$backupFile.zip"
    Remove-Item $backupFile
    
    Write-ColorOutput "备份完成: $backupFile.zip ✓" "Green"
    
    # 保留最近7天的备份
    Get-ChildItem $BackupDir -Filter "*.zip" | 
        Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-7) } | 
        Remove-Item
    
    Write-ColorOutput "已清理7天前的备份" "Green"
}

function Update-Deployment {
    Write-ColorOutput "开始更新部署..." "Cyan"
    
    # 备份数据库
    Backup-Database
    
    # 拉取最新代码
    Set-Location $ProjectRoot
    Write-ColorOutput "拉取最新代码..." "Cyan"
    git pull
    
    # 重新构建并启动
    Write-ColorOutput "重新构建镜像..." "Cyan"
    Set-Location "$ProjectRoot\docker"
    docker-compose -f docker-compose.prod.yml build
    
    # 重启服务
    Restart-Services
    
    Write-ColorOutput "更新完成! ✓" "Green"
}

function Show-Status {
    Write-ColorOutput "服务状态:" "Cyan"
    Set-Location "$ProjectRoot\docker"
    docker-compose -f docker-compose.prod.yml ps
    
    Write-ColorOutput "`n资源使用:" "Cyan"
    docker stats --no-stream myexam-api myexam-db
    
    Write-ColorOutput "`n健康检查:" "Cyan"
    try {
        $health = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/health"
        $health | ConvertTo-Json
    } catch {
        Write-ColorOutput "健康检查失败" "Red"
    }
}

function Enter-Shell {
    Write-ColorOutput "进入容器: $Container" "Cyan"
    docker exec -it $Container /bin/bash
}

# 主逻辑
switch ($Action) {
    'start' { Start-Services }
    'stop' { Stop-Services }
    'restart' { Restart-Services }
    'logs' { Show-Logs }
    'backup' { Backup-Database }
    'update' { Update-Deployment }
    'status' { Show-Status }
    'shell' { Enter-Shell }
    default {
        Write-Host @"
使用方法: .\deploy-prod.ps1 -Action <命令> [-Container <容器名>]

命令说明:
  start   - 启动所有服务
  stop    - 停止所有服务
  restart - 重启所有服务
  logs    - 查看日志 (默认: myexam-api)
  backup  - 备份数据库
  update  - 更新代码并重新部署
  status  - 查看服务状态
  shell   - 进入容器 (默认: myexam-api)

示例:
  .\deploy-prod.ps1 -Action start
  .\deploy-prod.ps1 -Action logs -Container db
  .\deploy-prod.ps1 -Action shell -Container myexam-db
"@
    }
}
