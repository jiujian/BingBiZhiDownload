@echo off
chcp 65001 >nul
echo 正在删除 GitHub Release: v1.0.0
echo.

REM 检查是否安装了 gh CLI
where gh >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 未安装 GitHub CLI (gh)
    echo 请访问 https://cli.github.com/ 安装
    pause
    exit /b 1
)

REM 删除 Release
gh release delete v1.0.0 --repo jiujian/BingBiZhiDownload --yes

if %errorlevel% == 0 (
    echo.
    echo 成功删除 Release: v1.0.0
) else (
    echo.
    echo Release 可能不存在或删除失败
)

echo.
pause

