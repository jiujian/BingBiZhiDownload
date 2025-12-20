# 删除 GitHub Release 的 PowerShell 脚本
param(
    [string]$TagName = "v1.0.0",
    [string]$Repo = "jiujian/BingBiZhiDownload"
)

Write-Host "正在删除 Release: $TagName" -ForegroundColor Yellow

# 检查是否安装了 gh CLI
if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    Write-Host "错误: 未安装 GitHub CLI (gh)" -ForegroundColor Red
    Write-Host "请访问 https://cli.github.com/ 安装" -ForegroundColor Yellow
    exit 1
}

# 检查是否已登录
$loginStatus = gh auth status 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "错误: 未登录 GitHub CLI" -ForegroundColor Red
    Write-Host "请运行: gh auth login" -ForegroundColor Yellow
    exit 1
}

# 检查 Release 是否存在
$releaseExists = gh release view $TagName --repo $Repo 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "Release 存在，正在删除..." -ForegroundColor Yellow
    gh release delete $TagName --repo $Repo --yes
    if ($LASTEXITCODE -eq 0) {
        Write-Host "成功删除 Release: $TagName" -ForegroundColor Green
    } else {
        Write-Host "删除 Release 失败" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "Release 不存在: $TagName" -ForegroundColor Green
}

