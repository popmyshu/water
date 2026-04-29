#!/bin/bash
# ==========================================
# 麻阳信息网 - 定时任务配置脚本
# 设置cron任务实现自动化运营
# ==========================================

set -e

echo "========================================"
echo "  麻阳信息网 定时任务配置"
echo "  Mayang Info Network - Cron Setup"
echo "========================================"

# 获取脚本所在目录（项目根目录）
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo ""
echo "📁 项目目录: $SCRIPT_DIR"
echo ""

# 检查Python3
PYTHON=$(command -v python3 || command -v python)
if [ -z "$PYTHON" ]; then
    echo "❌ 错误: 未找到Python3，请先安装"
    exit 1
fi
echo "✅ Python: $PYTHON ($($PYTHON --version 2>&1))"

# 检查脚本是否存在
for script in auto_operator.py auto_reply.py auto_collect.py; do
    if [ -f "$SCRIPT_DIR/$script" ]; then
        chmod +x "$SCRIPT_DIR/$script"
        echo "  ✅ $script"
    else
        echo "  ❌ $script 不存在于 $SCRIPT_DIR"
        exit 1
    fi
done

# 检查 deploy.sh
if [ -f "$SCRIPT_DIR/deploy.sh" ]; then
    chmod +x "$SCRIPT_DIR/deploy.sh"
    echo "  ✅ deploy.sh"
fi

echo ""
echo "========================================"
echo "  以下cron任务将被设置:"
echo "========================================"
echo ""
echo "  ⏰ 每2小时    - 自动采集新信息"
echo "     auto_collect.py all"
echo ""
echo "  ⏰ 每4小时    - 自动审核 + 自动置顶"
echo "     auto_operator.py pin"
echo ""
echo "  ⏰ 每天08:00  - 自动发布10条新内容"
echo "     auto_operator.py generate --count 10"
echo ""
echo "  ⏰ 每天02:00  - 清理过期内容 + 备份数据"
echo "     auto_operator.py cleanup"
echo ""
echo "  ⏰ 每30分钟   - 自动回复未处理留言"
echo "     auto_reply.py process"
echo ""
echo "  ⏰ 每天06:00  - 部署到GitHub Pages"
echo "     deploy.sh"
echo ""
echo "  ⏰ 每天23:59  - 生成每日运营报告"
echo "     auto_operator.py report"
echo ""

# ============ 创建cron任务 ============

# 生成crontab内容
CRON_JOBS="# ===== 麻阳信息网 AI自动运营定时任务 =====
# 项目路径: $SCRIPT_DIR

# 每2小时: 自动采集新信息（所有类别）
0 */2 * * * cd $SCRIPT_DIR && $PYTHON auto_collect.py all >> $SCRIPT_DIR/data/logs/cron_collect.log 2>&1

# 每4小时: 自动审核 + 自动置顶
30 */4 * * * cd $SCRIPT_DIR && $PYTHON auto_operator.py pin >> $SCRIPT_DIR/data/logs/cron_pin.log 2>&1

# 每天上午8点: 自动发布10条新内容（周一至周六）
0 8 * * 1-6 cd $SCRIPT_DIR && $PYTHON auto_operator.py generate --count 10 >> $SCRIPT_DIR/data/logs/cron_generate.log 2>&1

# 每天凌晨2点: 清理过期内容 + 备份数据
0 2 * * * cd $SCRIPT_DIR && $PYTHON auto_operator.py cleanup >> $SCRIPT_DIR/data/logs/cron_cleanup.log 2>&1

# 每30分钟: 自动回复未处理留言
*/30 * * * * cd $SCRIPT_DIR && $PYTHON auto_reply.py process >> $SCRIPT_DIR/data/logs/cron_reply.log 2>&1

# 每天6点: 部署到GitHub Pages
0 6 * * * cd $SCRIPT_DIR && bash deploy.sh >> $SCRIPT_DIR/data/logs/cron_deploy.log 2>&1

# 每天23:59: 生成每日运营报告
59 23 * * * cd $SCRIPT_DIR && $PYTHON auto_operator.py report >> $SCRIPT_DIR/data/logs/cron_report.log 2>&1

# ===== 结束 =====
"

# 显示将要添加的cron任务
echo "========================================"
echo "  Cron任务配置内容:"
echo "========================================"
echo "$CRON_JOBS"

# ============ 安装cron任务 ============

echo ""
echo "⏳ 正在安装cron任务..."

# 备份现有crontab
TEMP_CRON=$(mktemp)
crontab -l > "$TEMP_CRON" 2>/dev/null || true

# 检查是否已存在麻阳的cron任务，如果存在则先移除
if grep -q "麻阳信息网" "$TEMP_CRON" 2>/dev/null; then
    echo "⚠️  检测到已存在的麻阳信息网cron任务，将替换"
    # 移除旧的麻阳cron任务区块
    sed -i '/# ===== 麻阳信息网 AI自动运营定时任务 =====/,/# ===== 结束 =====/d' "$TEMP_CRON"
fi

# 添加新的cron任务
echo "$CRON_JOBS" >> "$TEMP_CRON"

# 安装新crontab
if crontab "$TEMP_CRON"; then
    echo "✅ 定时任务安装成功!"
else
    echo "❌ 定时任务安装失败!"
    echo "   可能是因为cron服务未安装"
    echo ""
    echo "   请手动安装: sudo apt-get install cron (Ubuntu/Debian)"
    echo "   或: sudo yum install cronie (CentOS/RHEL)"
    exit 1
fi

# 清理临时文件
rm "$TEMP_CRON"

# 确保cron服务在运行
echo ""
echo "⏳ 检查cron服务状态..."
if command -v systemctl &> /dev/null; then
    if systemctl is-active cron &> /dev/null || systemctl is-active crond &> /dev/null; then
        echo "✅ cron服务运行中"
    else
        echo "⚠️  cron服务未运行，尝试启动..."
        sudo systemctl start cron 2>/dev/null || sudo systemctl start crond 2>/dev/null || true
    fi
elif command -v service &> /dev/null; then
    if service cron status &> /dev/null; then
        echo "✅ cron服务运行中"
    else
        echo "⚠️  cron服务未运行，尝试启动..."
        sudo service cron start 2>/dev/null || true
    fi
else
    echo "⚠️  无法检查cron服务状态，请确保cron服务正在运行"
fi

# 确保日志目录存在
mkdir -p "$SCRIPT_DIR/data/logs"

echo ""
echo "========================================"
echo "  ✅ 配置完成!"
echo "========================================"
echo ""
echo "📋 当前cron任务列表:"
crontab -l | grep -v "^#" | grep -v "^$"
echo ""
echo "📝 日志文件位置:"
echo "  $SCRIPT_DIR/data/logs/cron_collect.log  - 采集日志"
echo "  $SCRIPT_DIR/data/logs/cron_pin.log      - 置顶日志"
echo "  $SCRIPT_DIR/data/logs/cron_generate.log - 生成日志"
echo "  $SCRIPT_DIR/data/logs/cron_cleanup.log  - 清理日志"
echo "  $SCRIPT_DIR/data/logs/cron_reply.log    - 回复日志"
echo "  $SCRIPT_DIR/data/logs/cron_deploy.log   - 部署日志"
echo "  $SCRIPT_DIR/data/logs/cron_report.log   - 报告日志"
echo ""
echo "💡 如果需要手动测试脚本，运行:"
echo "  $PYTHON $SCRIPT_DIR/auto_operator.py all     # 运行所有运营任务"
echo "  $PYTHON $SCRIPT_DIR/auto_collect.py all      # 采集所有类别"
echo "  $PYTHON $SCRIPT_DIR/auto_reply.py process    # 处理未回复留言"
echo "  bash $SCRIPT_DIR/deploy.sh                   # 部署到GitHub Pages"
