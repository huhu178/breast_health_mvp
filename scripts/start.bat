@echo off
chcp 65001
echo ================================
echo 🏥 乳腺结节健康管理系统 MVP
echo ================================
echo.

echo [1/3] 检查Python环境...
python --version
if errorlevel 1 (
    echo ❌ 错误：未找到Python，请先安装Python 3.8+
    pause
    exit /b 1
)
echo ✅ Python环境正常
echo.

echo [2/3] 安装依赖包...
cd ..
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
if errorlevel 1 (
    echo ⚠️ 警告：部分依赖安装失败，尝试继续...
)
echo ✅ 依赖安装完成
echo.

echo [3/3] 启动应用...
echo.
echo ================================
echo 📍 访问地址：http://localhost:5000
echo 📍 登录页面：http://localhost:5000/login
echo ================================
echo.
cd backend
python app.py

pause

