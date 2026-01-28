#!/bin/bash

# ===================================
# 乳腺健康管理系统 - 快速部署脚本
# ===================================
# 
# 使用方法：
# 1. 上传此脚本到服务器
# 2. chmod +x deploy.sh
# 3. ./deploy.sh
#
# 注意：此脚本适用于 Ubuntu/Debian 系统
# ===================================

set -e  # 遇到错误立即退出

echo "=========================================="
echo "乳腺健康管理系统 - 部署脚本"
echo "=========================================="

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查是否为 root 用户
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}错误：请使用 root 用户运行此脚本${NC}"
    exit 1
fi

# 配置变量（请根据实际情况修改）
PROJECT_DIR="/root/MQ/breast_health_mvp"
DB_NAME="breast_health_prod"
DB_USER="app_user"
DB_PASSWORD=""  # 将在脚本中提示输入
DOMAIN=""  # 可选，如果为空则使用 IP

echo -e "${YELLOW}步骤 1/10: 更新系统...${NC}"
apt update && apt upgrade -y

echo -e "${YELLOW}步骤 2/10: 安装基础软件...${NC}"
apt install -y python3 python3-pip python3-venv git curl wget

echo -e "${YELLOW}步骤 3/10: 检查 PostgreSQL...${NC}"
# 检查 PostgreSQL 是否已安装
if ! command -v psql &> /dev/null; then
    echo -e "${YELLOW}PostgreSQL 未安装，正在安装...${NC}"
    apt install -y postgresql postgresql-contrib libpq-dev
    systemctl start postgresql
    systemctl enable postgresql
else
    echo -e "${GREEN}✅ PostgreSQL 已安装${NC}"
fi

# 检查数据库是否已存在（可选提示）
echo -e "${YELLOW}提示：如果数据库已存在，请在 .env 文件中配置正确的 DATABASE_URL${NC}"

echo -e "${YELLOW}步骤 4/10: 检查 Node.js...${NC}"
if ! command -v node &> /dev/null; then
    echo -e "${YELLOW}Node.js 未安装，正在安装 Node.js 20...${NC}"
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
    apt install -y nodejs
else
    NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
    if [ "$NODE_VERSION" -lt 20 ]; then
        echo -e "${YELLOW}Node.js 版本过低 ($(node --version))，需要升级到 20+...${NC}"
        curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
        apt install -y nodejs
    else
        echo -e "${GREEN}✅ Node.js 已安装 ($(node --version))${NC}"
    fi
fi

echo -e "${YELLOW}步骤 5/10: 检查项目目录...${NC}"
mkdir -p /root/MQ

# 检查项目是否已存在
if [ -d "$PROJECT_DIR" ]; then
    echo -e "${GREEN}✅ 项目目录已存在: ${PROJECT_DIR}${NC}"
    echo -e "${YELLOW}将使用现有项目目录继续部署${NC}"
    cd "$PROJECT_DIR"
else
    # 项目不存在，需要解压
    cd /root/MQ
    echo -e "${YELLOW}请选择部署方式：${NC}"
    echo "1) 从 Git 仓库克隆"
    echo "2) 从本地文件上传（需要先上传项目文件到 /tmp/breast_health_mvp.tar.gz）"
    read -r choice

    case $choice in
        1)
            read -p "请输入 Git 仓库地址: " GIT_REPO
            git clone "$GIT_REPO" breast_health_mvp
            ;;
        2)
            if [ ! -f "/tmp/breast_health_mvp.tar.gz" ]; then
                echo -e "${RED}错误：未找到 /tmp/breast_health_mvp.tar.gz${NC}"
                exit 1
            fi
            tar -xzf /tmp/breast_health_mvp.tar.gz
            ;;
        *)
            echo -e "${RED}无效选择${NC}"
            exit 1
            ;;
    esac
    cd "$PROJECT_DIR"
fi

echo -e "${YELLOW}步骤 6/10: 创建 Python 虚拟环境...${NC}"
if [ ! -d "health-mvp" ]; then
    python3 -m venv health-mvp
    echo -e "${GREEN}✅ 虚拟环境已创建${NC}"
else
    echo -e "${GREEN}✅ 虚拟环境已存在${NC}"
fi
source health-mvp/bin/activate
pip install --upgrade pip

echo -e "${YELLOW}步骤 7/10: 安装 Python 依赖...${NC}"
pip install -r requirements.txt
pip install gunicorn
playwright install chromium
playwright install-deps chromium

echo -e "${YELLOW}步骤 8/10: 配置环境变量...${NC}"
if [ ! -f ".env" ]; then
    # 询问部署方式
    echo -e "${YELLOW}请选择部署方式：${NC}"
    echo "1) IP部署（无域名，推荐）"
    echo "2) 域名部署（有域名和SSL证书）"
    read -p "请选择 [1/2]: " deploy_type

    # 使用 env.example 作为模板
    if [ -f "env.example" ]; then
        cp env.example .env
        echo -e "${GREEN}✅ 已使用 env.example 模板${NC}"
    else
        echo -e "${RED}错误：未找到 env.example 文件${NC}"
        exit 1
    fi

    # 自动生成密钥
    echo -e "${YELLOW}正在生成安全密钥...${NC}"
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
    JWT_SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")

    # 替换密钥占位符
    sed -i "s/your-secret-key-here-change-in-production/$SECRET_KEY/" .env
    sed -i "s/your-jwt-secret-key-here-change-in-production/$JWT_SECRET_KEY/" .env
    sed -i "s/REPLACE_WITH_RANDOM_STRING_64_CHARS_MINIMUM/$SECRET_KEY/" .env
    sed -i "s/your-super-secret-key-64-chars-minimum-change-me-to-random-string/$SECRET_KEY/" .env
    sed -i "s/your-jwt-secret-key-64-chars-minimum-change-me-to-random-string/$JWT_SECRET_KEY/" .env

    # 如果提供了数据库密码，替换（否则在 nano 中手动填写）
    if [ -n "$DB_PASSWORD" ]; then
        sed -i "s/your_password/$DB_PASSWORD/" .env
        sed -i "s/YOUR_DB_PASSWORD_HERE/$DB_PASSWORD/" .env
    fi

    echo -e "${GREEN}✅ 密钥已自动生成${NC}"
    echo -e "${YELLOW}请继续编辑 .env 文件，填写以下信息：${NC}"
    echo "  - DATABASE_URL (必填，例如: postgresql://postgres:Maqing123@localhost:5432/jiejie)"
    echo "  - OPENROUTER_API_KEY (必填)"
    echo "  - FLASK_ENV=production"
    echo "  - DEBUG=False"
    echo ""
    read -p "按 Enter 继续（将使用 nano 编辑器）..."
    nano .env
else
    echo -e "${GREEN}✅ .env 文件已存在，跳过配置${NC}"
fi
chmod 600 .env

echo -e "${YELLOW}步骤 9/10: 构建前端...${NC}"
cd frontend/vue-app
# 清理旧的 node_modules 和 package-lock.json（解决 rolldown 原生绑定问题）
if [ -d "node_modules" ]; then
    echo -e "${YELLOW}清理旧的 node_modules...${NC}"
    rm -rf node_modules package-lock.json
fi
npm install
# 修复 node_modules/.bin 权限
chmod -R +x node_modules/.bin 2>/dev/null || true
npm run build
cd ../..

echo -e "${YELLOW}步骤 10/10: 配置服务...${NC}"

# 创建 Gunicorn 配置
cat > backend/gunicorn_config.py << 'EOF'
import multiprocessing

bind = "127.0.0.1:5000"
workers = multiprocessing.cpu_count() * 2 + 1
threads = 2
worker_class = "sync"
timeout = 120
keepalive = 5
accesslog = "/var/log/breast_health/access.log"
errorlog = "/var/log/breast_health/error.log"
loglevel = "info"
proc_name = "breast_health"
EOF

# 创建日志目录
mkdir -p /var/log/breast_health
chown www-data:www-data /var/log/breast_health

# 创建 systemd 服务
cat > /etc/systemd/system/breast-health.service << EOF
[Unit]
Description=Breast Health Management System
After=network.target postgresql.service

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=${PROJECT_DIR}/backend
Environment="PATH=${PROJECT_DIR}/health-mvp/bin:/usr/local/bin:/usr/bin:/bin"
Environment="FLASK_ENV=production"
Environment="VIRTUAL_ENV=${PROJECT_DIR}/health-mvp"
ExecStart=${PROJECT_DIR}/health-mvp/bin/gunicorn -c gunicorn_config.py app:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# 设置项目目录权限
chown -R www-data:www-data "$PROJECT_DIR"

# 安装和配置 Nginx
apt install -y nginx

# 获取域名或 IP
if [ -z "$DOMAIN" ]; then
    read -p "请输入域名（或按 Enter 使用 IP）: " DOMAIN
fi

if [ -z "$DOMAIN" ]; then
    DOMAIN=$(hostname -I | awk '{print $1}')
fi

# 创建 Nginx 配置
cat > /etc/nginx/sites-available/breast-health << EOF
server {
    listen 80;
    server_name ${DOMAIN};

    access_log /var/log/nginx/breast_health_access.log;
    error_log /var/log/nginx/breast_health_error.log;

    location / {
        root ${PROJECT_DIR}/frontend/vue-app/dist;
        try_files \$uri \$uri/ /index.html;
        index index.html;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    client_max_body_size 16M;

    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
}
EOF

# 启用 Nginx 配置
ln -sf /etc/nginx/sites-available/breast-health /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx

# 启动服务
systemctl daemon-reload
systemctl start breast-health
systemctl enable breast-health

echo -e "${GREEN}=========================================="
echo "🎉 部署完成！"
echo "=========================================="
echo "项目目录: ${PROJECT_DIR}"
echo "访问地址: http://${DOMAIN}"
echo ""
echo "下一步："
echo ""
echo "📌 重要说明："
echo "   - 应用启动时会自动创建表（如果不存在）"
echo "   - 如果数据库表已存在且结构是最新的，可以跳过迁移"
echo ""
echo "1. 数据库迁移（可选，仅在需要更新表结构时运行）:"
echo "   cd ${PROJECT_DIR}"
echo "   source health-mvp/bin/activate"
echo "   ./run_migrations.sh"
echo "   （如果表已存在且是最新的，可以跳过此步骤）"
echo ""
echo "2. 创建管理员账户（首次部署必须）:"
echo "   cd ${PROJECT_DIR}"
echo "   source health-mvp/bin/activate"
echo "   python create_admin.py"
echo "   （默认账号：admin/123456，请及时修改）"
echo ""
echo "3. 检查服务状态:"
echo "   systemctl status breast-health"
echo ""
echo "4. 查看日志:"
echo "   journalctl -u breast-health -f"
echo ""
echo "5. 浏览器访问:"
echo "   http://${DOMAIN}"
echo ""
if [ -z "$DOMAIN" ] || [[ "$DOMAIN" =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo "📌 IP部署提示："
    echo "   - 当前使用IP访问，HTTP协议不加密"
    echo "   - 建议仅在测试或内网环境使用"
    echo "   - 后续可申请域名并配置HTTPS"
fi
echo "==========================================${NC}"

