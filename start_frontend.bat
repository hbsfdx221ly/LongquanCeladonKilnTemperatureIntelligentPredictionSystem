@echo off
echo 启动龙泉青瓷窑温智能预测系统前端服务...
echo ================================================

cd frontend

echo 检查Node.js环境...
node --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Node.js，请先安装Node.js
    pause
    exit /b 1
)

echo 安装依赖...
call npm install
if errorlevel 1 (
    echo 错误: 依赖安装失败
    pause
    exit /b 1
)

echo 启动开发服务器...
call npm run dev

pause
