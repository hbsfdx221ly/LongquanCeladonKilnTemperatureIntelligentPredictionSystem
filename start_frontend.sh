#!/bin/bash

echo "启动龙泉青瓷窑温智能预测系统前端服务..."
echo "================================================"

cd frontend

echo "检查Node.js环境..."
if ! command -v node &> /dev/null; then
    echo "错误: 未找到Node.js，请先安装Node.js"
    exit 1
fi

echo "安装依赖..."
npm install
if [ $? -ne 0 ]; then
    echo "错误: 依赖安装失败"
    exit 1
fi

echo "启动开发服务器..."
npm run dev
