@echo off
REM ===================================
REM Windows 开发环境统一启动脚本
REM 同时启动 Flask 后端和 Vue 前端开发服务器
REM ===================================

echo ==========================================
echo 启动开发环境（Flask + Vue）
echo ==========================================

cd /d %~dp0

REM 启动 Vue 开发服务器（新窗口）
echo 1. 启动 Vue 前端开发服务器...
start "Vue Dev Server" cmd /k "cd frontend\vue-app && npm run dev"

REM 等待一下
timeout /t 3 /nobreak >nul

REM 启动 Flask 后端（新窗口）
echo 2. 启动 Flask 后端服务器...
start "Flask Backend" cmd /k "cd backend && python app.py"

echo.
echo ==========================================
echo 开发环境已启动！
echo ==========================================
echo 前端: http://localhost:5173
echo 后端: http://localhost:5000
echo.
echo 关闭窗口即可停止对应服务
echo ==========================================

pause

