#!/bin/bash

# ===================================
# 后台启动脚本
# 同时启动 Flask 后端和 Vue 前端，关闭终端也不受影响
# ===================================

echo "=========================================="
echo "后台启动服务（Flask + Vue）"
echo "=========================================="

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$SCRIPT_DIR"
BACKEND_DIR="$PROJECT_DIR/backend"
FRONTEND_DIR="$PROJECT_DIR/frontend/vue-app"

# 检查目录
if [ ! -d "$BACKEND_DIR" ]; then
    echo "❌ 错误：找不到 backend 目录"
    exit 1
fi

if [ ! -d "$FRONTEND_DIR" ]; then
    echo "❌ 错误：找不到 frontend/vue-app 目录"
    exit 1
fi

# 停止可能存在的旧进程
echo "检查并停止旧进程..."
pkill -f "python.*app.py" 2>/dev/null
pkill -f "vite" 2>/dev/null
sleep 2

# 创建日志目录
mkdir -p /tmp/breast_health
LOG_DIR="/tmp/breast_health"

# 启动后端
echo "启动 Flask 后端..."
cd "$BACKEND_DIR"
source ../health-mvp/bin/activate
# 禁用 Flask 内部自动启动 Vite，避免端口冲突
export DISABLE_INTERNAL_VUE=1
# 使用 setsid 确保完全脱离终端，即使关闭终端也不会停止
setsid nohup python app.py > "$LOG_DIR/flask.log" 2>&1 &
FLASK_PID=$!
echo "✅ Flask 后端已启动，PID: $FLASK_PID"
echo "   日志: $LOG_DIR/flask.log"

# 等待一下
sleep 2

# 启动前端
echo "启动 Vue 前端..."
cd "$FRONTEND_DIR"
# 使用 setsid 确保完全脱离终端，并明确指定 host 和 port
setsid nohup npm run dev -- --host 0.0.0.0 --port 5173 > "$LOG_DIR/vue.log" 2>&1 &
VUE_PID=$!
echo "✅ Vue 前端已启动，PID: $VUE_PID"
echo "   日志: $LOG_DIR/vue.log"

# 等待服务启动
sleep 3

# 检查进程
echo ""
echo "=========================================="
echo "✅ 服务已启动！"
echo "=========================================="
echo "Flask 后端 PID: $FLASK_PID"
echo "Vue 前端 PID: $VUE_PID"
echo ""
echo "访问地址："
echo "  前端: http://115.190.207.23:5173"
echo "  后端: http://115.190.207.23:5000"
echo ""
echo "查看日志："
echo "  tail -f $LOG_DIR/flask.log"
echo "  tail -f $LOG_DIR/vue.log"
echo ""
echo "停止服务："
echo "  pkill -f 'python.*app.py'"
echo "  pkill -f 'vite'"
echo "=========================================="

# 保存 PID 到文件（可选）
echo "$FLASK_PID" > "$LOG_DIR/flask.pid"
echo "$VUE_PID" > "$LOG_DIR/vue.pid"

echo ""
echo "服务已在后台运行，可以安全关闭终端！"

