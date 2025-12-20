@echo off
chcp 65001 >nul
echo ========================================
echo 创建并推送 GitHub Tag
echo ========================================
echo.

REM 设置版本号（可以根据需要修改）
set VERSION=v1.0.0
set TAG_MESSAGE=初始版本发布 - 必应每日壁纸下载器 V1.0

echo 当前版本: %VERSION%
echo Tag 说明: %TAG_MESSAGE%
echo.

REM 检查是否已存在该 tag
git tag -l %VERSION% >nul 2>&1
if %errorlevel% == 0 (
    echo 警告: Tag %VERSION% 已存在！
    echo 是否删除并重新创建? (Y/N)
    set /p choice=
    if /i "%choice%"=="Y" (
        echo 删除本地 tag...
        git tag -d %VERSION%
        echo 删除远程 tag...
        git push origin :refs/tags/%VERSION%
    ) else (
        echo 操作已取消
        pause
        exit /b
    )
)

echo.
echo 创建本地 tag...
git tag -a %VERSION% -m "%TAG_MESSAGE%"

if %errorlevel% neq 0 (
    echo 错误: 创建 tag 失败！
    pause
    exit /b 1
)

echo.
echo 推送 tag 到 GitHub...
git push origin %VERSION%

if %errorlevel% neq 0 (
    echo 错误: 推送 tag 失败！
    pause
    exit /b 1
)

echo.
echo ========================================
echo 成功！Tag %VERSION% 已推送到 GitHub
echo ========================================
echo.
echo 查看所有 tags:
git tag -l
echo.
pause

