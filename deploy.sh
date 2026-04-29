#!/bin/bash
# ==========================================
# 麻阳信息网 - GitHub Pages 部署脚本
# 将生成的HTML文件和所有资源部署到GitHub Pages
# ==========================================

set -e

echo "========================================"
echo "  麻阳信息网 自动部署脚本"
echo "  Mayang Info Network - Auto Deploy"
echo "========================================"

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo ""
echo "[1/5] 检查Git仓库状态..."
if [ ! -d ".git" ]; then
    echo "❌ 错误: 当前目录不是Git仓库"
    echo "   请先运行: git init && git remote add origin <仓库地址>"
    exit 1
fi

# 检查是否有未提交的更改
if [ -n "$(git status --porcelain)" ]; then
    echo "⚠️  有未提交的更改，将会一并提交"
    HAS_CHANGES=true
else
    echo "✅ 工作区干净，无需提交新更改"
    HAS_CHANGES=false
fi

echo ""
echo "[2/5] 确保数据目录存在..."
mkdir -p data/posts
mkdir -p data/backup
mkdir -p data/messages
mkdir -p data/logs
mkdir -p data/images

# 创建 .gitkeep 文件确保空目录也能被提交
for dir in data/posts data/backup data/messages data/logs data/images; do
    touch "$dir/.gitkeep"
done

echo "✅ 数据目录检查完成"

echo ""
echo "[3/5] 检查必要文件..."
MISSING=false

# 检查核心脚本
for script in auto_operator.py auto_reply.py auto_collect.py; do
    if [ -f "$script" ]; then
        chmod +x "$script"
        echo "  ✅ $script"
    else
        echo "  ❌ $script 缺失!"
        MISSING=true
    fi
done

# 检查主要页面
if [ -f "index.html" ]; then
    echo "  ✅ index.html"
else
    echo "  ⚠️  index.html 不存在，但GitHub Pages需要它"
    echo "     如果你有其他页面，请确保根目录有 index.html"
fi

if [ "$MISSING" = true ]; then
    echo "❌ 存在缺失文件，请检查后重试"
    exit 1
fi

echo ""
echo "[4/5] 提交到Git仓库..."

# 添加所有文件
git add -A

# 如果有变化则提交
if [ "$HAS_CHANGES" = true ]; then
    COMMIT_MSG="🤖 自动部署: $(date '+%Y-%m-%d %H:%M')"

    # 检查是否存在 auto_operator.py 的修改，添加更具体的描述
    if git diff --cached --name-only | grep -q "auto_"; then
        UPDATED_SCRIPTS=$(git diff --cached --name-only | grep "auto_" | tr '\n' ' ')
        COMMIT_MSG="🤖 自动部署 - 更新脚本: $UPDATED_SCRIPTS ($(date '+%Y-%m-%d %H:%M'))"
    fi

    # 检查数据文件是否更新
    if git diff --cached --name-only | grep -q "^data/"; then
        DATA_COUNT=$(git diff --cached --name-only | grep "^data/" | wc -l)
        COMMIT_MSG="$COMMIT_MSG [数据更新: ${DATA_COUNT}个文件]"
    fi

    git commit -m "$COMMIT_MSG"
    echo "  ✅ 提交成功: $COMMIT_MSG"
else
    echo "  ℹ️  无新更改需要提交"
fi

echo ""
echo "[5/5] 推送到 GitHub Pages..."

# 检查远程仓库配置
REMOTE=$(git remote get-url origin 2>/dev/null || echo "")
if [ -z "$REMOTE" ]; then
    echo "⚠️  未配置远程仓库，跳过推送"
    echo "   请配置远程仓库: git remote add origin <你的GitHub仓库地址>"
    echo "   然后手动推送: git push origin main"
else
    echo "  远程仓库: $REMOTE"
    echo "  正在推送到 main 分支..."

    if git push origin main 2>&1; then
        echo "  ✅ 推送成功!"
        echo ""
        echo "  🌐 你的网站将在几分钟后更新:"
        echo "     https://popmyshu.github.io/water/"
    else
        echo "  ❌ 推送失败，请检查网络连接和权限"
        echo "     尝试手动推送: git push origin main"
        exit 1
    fi
fi

echo ""
echo "========================================"
echo "  ✅ 部署完成!"
echo "========================================"
echo ""
echo "📋 部署摘要:"
echo "  - 时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "  - 分支: main"
echo "  - 提交信息: $COMMIT_MSG"

# 显示当前状态
echo ""
echo "📊 数据文件统计:"
find data/ -type f -name "*.json" 2>/dev/null | wc -l | xargs echo "  JSON文件数:"
find data/ -type f 2>/dev/null | wc -l | xargs echo "  总文件数:"
