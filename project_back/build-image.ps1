Param(
  [string]$ImageName = "myexam-api",
  [string]$Version = "latest",
  [string]$Registry = "",
  [string]$Platform = "",           # 例: linux/amd64 或 linux/amd64,linux/arm64
  [switch]$Push,                     # 构建后推送
  [switch]$NoCache                   # 不使用缓存
)

$ErrorActionPreference = 'Stop'

function Write-Info($msg){ Write-Host "[INFO] $msg" -ForegroundColor Cyan }
function Write-Warn($msg){ Write-Host "[WARN] $msg" -ForegroundColor Yellow }
function Write-Err($msg){ Write-Host "[ERROR] $msg" -ForegroundColor Red }

function Get-ShortSha {
  try {
    $sha = (git rev-parse --short HEAD 2>$null).Trim()
    if ($LASTEXITCODE -eq 0 -and $sha) { return $sha }
  } catch {}
  return "no-git"
}

function Get-DefaultVersion($ver){
  if ($ver -and $ver -ne 'auto') { return $ver }
  $sha = Get-ShortSha
  $ts = Get-Date -Format 'yyyyMMddHHmmss'
  return "$ts-$sha"
}

# 校验 Docker 是否可用
try { docker --version | Out-Null } catch { Write-Err "Docker 未安装或未加入 PATH"; exit 1 }

# 切换到脚本所在目录（后端根目录）
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

$env:DOCKER_BUILDKIT = '1'

$resolvedVersion = Get-DefaultVersion $Version
$repo = if ($Registry) { "$Registry/" } else { "" }
$fullTag = "$repo${ImageName}:$resolvedVersion"

Write-Info "构建镜像: $fullTag"
Write-Info "Dockerfile: docker/Dockerfile"

$buildArgs = @('build', '.', '-f', 'docker/Dockerfile', '-t', $fullTag)
if ($NoCache) { $buildArgs += '--no-cache' }
if ($Platform) { $buildArgs = @('buildx','build','--platform', $Platform, '-f','docker/Dockerfile','-t', $fullTag,'.') }

Write-Info "执行: docker $($buildArgs -join ' ')"
docker @buildArgs

if ($LASTEXITCODE -ne 0) {
  Write-Err "构建失败"
  exit $LASTEXITCODE
}

Write-Host "`n==================== 成功 ====================" -ForegroundColor Green
Write-Host "镜像已构建: $fullTag"

if ($Push) {
  if (-not $Registry) { Write-Warn "未指定 Registry，跳过推送。使用 -Registry 和 -Push 可推送到远端。"; exit 0 }
  Write-Info "推送镜像到: $fullTag"
  if ($Platform) {
    Write-Info "使用 buildx 多平台推送"
    docker buildx build --platform $Platform -f docker/Dockerfile -t $fullTag --push .
  } else {
    docker push $fullTag
  }
  if ($LASTEXITCODE -ne 0) { Write-Err "推送失败"; exit $LASTEXITCODE }
  Write-Host "推送完成: $fullTag" -ForegroundColor Green
}

Write-Host "完成。" -ForegroundColor Green

<#
用法示例（在 PowerShell 中）：

1) 本地构建（默认 latest）：
   ./build-image.ps1

2) 指定版本：
   ./build-image.ps1 -Version 1.0.0

3) 自动版本（时间戳+Git短SHA）：
   ./build-image.ps1 -Version auto

4) 指定注册表并推送：
   ./build-image.ps1 -Registry docker.io/yourname -Version auto -Push

5) 多平台构建并推送（需 Docker buildx）：
   ./build-image.ps1 -Registry docker.io/yourname -Version auto -Platform "linux/amd64,linux/arm64" -Push

6) 不使用缓存：
   ./build-image.ps1 -NoCache

说明：
- 本脚本默认使用 docker/Dockerfile，并以 project_back 为构建上下文。
- 建议在 project_back 根目录新增 .dockerignore（本脚本未自动创建）。
#>
