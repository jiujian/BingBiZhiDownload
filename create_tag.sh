#!/bin/bash
# 创建并推送 GitHub Tag 脚本

echo "========================================"
echo "创建并推送 GitHub Tag"
echo "========================================"
echo ""

# 设置版本号（可以根据需要修改）
VERSION="v1.0.0"
TAG_MESSAGE="初始版本发布 - 必应每日壁纸下载器 V1.0"

echo "当前版本: $VERSION"
echo "Tag 说明: $TAG_MESSAGE"
echo ""

# 检查是否已存在该 tag
if git tag -l | grep -q "^$VERSION$"; then
    echo "警告: Tag $VERSION 已存在！"
    read -p "是否删除并重新创建? (y/n) " choice
    if [[ "$choice" == "y" || "$choice" == "Y" ]]; then
        echo "删除本地 tag..."
        git tag -d "$VERSION"
        echo "删除远程 tag..."
        git push origin :refs/tags/"$VERSION"
    else
        echo "操作已取消"
        exit 1
    fi
fi

echo ""
echo "创建本地 tag..."
git tag -a "$VERSION" -m "$TAG_MESSAGE"

if [ $? -ne 0 ]; then
    echo "错误: 创建 tag 失败！"
    exit 1
fi

echo ""
echo "推送 tag 到 GitHub..."
git push origin "$VERSION"

if [ $? -ne 0 ]; then
    echo "错误: 推送 tag 失败！"
    exit 1
fi

echo ""
echo "========================================"
echo "成功！Tag $VERSION 已推送到 GitHub"
echo "========================================"
echo ""
echo "查看所有 tags:"
git tag -l

