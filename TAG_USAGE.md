# GitHub Tag 使用说明

本项目已创建用于创建和推送 GitHub tags 的脚本文件。

## 脚本文件

- **create_tag.bat** - Windows 批处理脚本
- **create_tag.sh** - Linux/macOS Shell 脚本

## 使用方法

### Windows 系统

直接双击运行 `create_tag.bat`，或在命令行中执行：

```bash
create_tag.bat
```

### Linux/macOS 系统

首先给脚本添加执行权限：

```bash
chmod +x create_tag.sh
```

然后运行：

```bash
./create_tag.sh
```

## 手动创建和推送 Tag

如果你想手动创建和推送 tag，可以使用以下命令：

### 1. 创建带注释的 Tag（推荐）

```bash
git tag -a v1.0.0 -m "版本说明信息"
```

### 2. 创建轻量级 Tag（无注释）

```bash
git tag v1.0.0
```

### 3. 推送单个 Tag 到远程

```bash
git push origin v1.0.0
```

### 4. 推送所有本地 Tags 到远程

```bash
git push origin --tags
```

### 5. 删除本地 Tag

```bash
git tag -d v1.0.0
```

### 6. 删除远程 Tag

```bash
git push origin :refs/tags/v1.0.0
```

## 当前版本

- **v1.0.0** - 初始版本发布（已推送到 GitHub）

## 版本命名规范

建议使用语义化版本号（Semantic Versioning）：

- **主版本号（Major）**: 不兼容的 API 修改
- **次版本号（Minor）**: 向下兼容的功能性新增
- **修订号（Patch）**: 向下兼容的问题修正

示例：
- `v1.0.0` - 初始版本
- `v1.1.0` - 新增功能
- `v1.1.1` - 修复 bug
- `v2.0.0` - 重大更新（可能不兼容）

## 查看 Tag 信息

```bash
# 查看所有 tags
git tag -l

# 查看特定 tag 的详细信息
git show v1.0.0

# 查看 tag 列表（按版本排序）
git tag -l --sort=-v:refname
```

## 注意事项

1. Tag 一旦推送到远程，建议不要删除（除非有特殊原因）
2. 如果 tag 已存在，脚本会提示是否删除并重新创建
3. 确保在创建 tag 前，相关代码已经提交到仓库
4. Tag 名称建议使用 `v` 前缀，如 `v1.0.0`

