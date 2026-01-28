#!/bin/bash

# ===================================
# 开发环境统一启动脚本
# 同时启动 Flask 后端和 Vue 前端开发服务器
# ===================================

echo "=========================================="
echo "启动开发环境（Flask + Vue）"
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

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 函数：清理后台进程
cleanup() {
    echo -e "\n${YELLOW}正在停止服务...${NC}"
    kill $FLASK_PID $VUE_PID 2>/dev/null
    exit 0
}

# 注册清理函数
trap cleanup SIGINT SIGTERM

# 启动 Vue 开发服务器
echo -e "${GREEN}1. 启动 Vue 前端开发服务器...${NC}"
cd "$FRONTEND_DIR"
if [ ! -d "node_modules" ]; then
    echo "安装前端依赖..."
    npm install
fi
# 使用 --host 参数让 Vite 监听所有接口，允许外部访问
npm run dev -- --host &
VUE_PID=$!
echo "Vue 开发服务器 PID: $VUE_PID"
echo "前端地址: http://localhost:5173"

# 等待 Vue 服务器启动
sleep 3

# 启动 Flask 后端
echo -e "${GREEN}2. 启动 Flask 后端服务器...${NC}"
cd "$BACKEND_DIR"

# 检查虚拟环境（使用 health-mvp）
if [ ! -d "../health-mvp" ]; then
    echo "创建虚拟环境..."
    python3 -m venv ../health-mvp
fi

# 激活虚拟环境
source ../health-mvp/bin/activate

# 检查依赖
if ! python -c "import flask" 2>/dev/null; then
    echo "安装后端依赖..."
    pip install -r ../requirements.txt
fi

# 启动 Flask
python app.py &
FLASK_PID=$!
echo "Flask 后端服务器 PID: $FLASK_PID"
echo "后端地址: http://localhost:5000"
echo "API 地址: http://localhost:5000/api/health"

echo -e "\n${GREEN}=========================================="
echo "✅ 开发环境已启动！"
echo "=========================================="
echo "前端: http://localhost:5173"
echo "后端: http://localhost:5000"
echo ""
echo "按 Ctrl+C 停止所有服务"
echo "==========================================${NC}"

# 等待进程
wait

