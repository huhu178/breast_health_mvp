@echo off
chcp 65001 >nul
echo ========================================
echo 乳腺健康系统 - 快速启动脚本
echo ========================================
echo.

echo [1/3] 请在新的PowerShell窗口中手动执行SSH隧道命令：
echo.
echo     ssh -L 5433:localhost:5432 root@115.190.207.23
echo.
echo 输入密码后保持该窗口打开！
echo.
pause

echo.
echo [2/3] 启动后端服务...
cd /d "%~dp0"
call venv\Scripts\activate.bat
python backend/app.py

pause
