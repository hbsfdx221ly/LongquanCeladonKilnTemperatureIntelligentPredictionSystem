# 《瓷路算法》——龙泉青瓷窑温智能预测系统

## 项目简介

这是一个融合传统龙泉青瓷工艺与现代AI技术的智能预测系统，通过机器学习算法预测窑温曲线和釉面成色，帮助青瓷匠人优化烧制工艺。

## 技术栈

### 前端
- Vue 3 + Vite
- ECharts 数据可视化
- Three.js 3D窑炉模型
- Element Plus UI组件
- WebSocket 实时通信

### 后端
- Python Flask
- LightGBM 机器学习
- MySQL 数据库
- WebSocket 实时推送

## 核心功能

1. **3D窑炉可视化**：Three.js构建龙泉窑剖面模型，实时显示火焰流动
2. **智能预测**：基于胎土配方、匣钵厚度、木炭用量预测最佳升温曲线
3. **成色评分**：AI模型预测釉面成色概率，准确率85%+
4. **实时监控**：WebSocket推送窑温数据，手机扫码远程监控
5. **温差云图**：可视化不同窑位的温度分布

## 快速开始

### 环境要求
- Python 3.8+
- Node.js 16+
- MySQL 5.7+ (可选，默认使用SQLite)

### 一键启动

#### Windows用户
```bash
# 启动后端服务
python start_backend.py

# 新开终端窗口，启动前端服务
start_frontend.bat
```

#### Linux/Mac用户
```bash
# 启动后端服务
python start_backend.py

# 新开终端窗口，启动前端服务
./start_frontend.sh
```

### 手动启动

#### 后端启动
```bash
# 1. 安装Python依赖
pip install -r requirements.txt

# 2. 初始化数据库和训练模型
cd backend
python init_db.py
python train_model.py

# 3. 启动Flask服务
python app.py
```

#### 前端启动
```bash
# 1. 安装Node.js依赖
cd frontend
npm install

# 2. 启动开发服务器
npm run dev
```

### 系统测试
```bash
# 运行系统测试
python test_system.py

# 运行功能演示
python demo_script.py
```

## 启动与关闭（前后端）

### 后端（Flask + Socket.IO）
启动（开发模式，默认 SQLite 数据库）
```powershell
cd backend
..\\.venv\\Scripts\\activate
python app.py
```
关闭
```powershell
# 在启动的终端按 Ctrl + C
# 或在任务管理器结束 python 进程
```

可选：一键后台启动（根目录）
```powershell
python start_backend.py
```

健康检查
```powershell
curl http://127.0.0.1:5000/health
```

### 前端（Vite + Vue3）
启动（网络模式，便于同网段访问）
```powershell
cd frontend
npm run dev -- --host
```
关闭
```powershell
# 在启动的终端按 Ctrl + C
```

访问地址（以 Vite 输出为准）
- Local: http://localhost:3000/（如端口被占用会自动切到 3001 等）
- Network: 终端显示的本机 IP，如 http://172.29.xx.xx:3000/

构建生产包
```powershell
cd frontend
npm run build
```

## 常见问题与解决方案（本次排障实录）

### 1) pip 安装报编码/构建错误
- 现象：`pip install -r requirements.txt` 在中文 Windows 下报解码错误，或 `numpy/scipy/matplotlib` 需要本地编译失败。
- 解决：
  - 将 `requirements.txt` 改为纯 ASCII（已修复）。
  - 先装兼容的二进制包，再装其余依赖：
    ```powershell
    ..\\.venv\\Scripts\\activate
    pip install --upgrade pip setuptools wheel -i https://pypi.tuna.tsinghua.edu.cn/simple
    pip install numpy==1.26.4 scipy==1.11.3 -i https://pypi.tuna.tsinghua.edu.cn/simple
    pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
    ```

### 2) 连接 MySQL 失败（WinError 10061）
- 现象：`Can't connect to MySQL server on 'localhost'`。
- 解决：已将后端默认数据库切换为 SQLite（`backend/config.py`），无需 MySQL。若需使用 MySQL，设置环境变量：
  ```powershell
  $env:DATABASE_URL="mysql+pymysql://user:pass@host:3306/porcelain_ai"
  ```

### 3) Flask-SocketIO 拒绝使用 Werkzeug
- 现象：`RuntimeError: The Werkzeug web server is not designed to run in production`。
- 解决：在 `backend/app.py` 的 `socketio.run` 中加入 `allow_unsafe_werkzeug=True`（已修复）。

### 4) 前端访问 404（localhost:3000 打不开）
- 原因：Vite 默认以项目根为前端根，而源码在 `frontend/` 子目录；或端口被占用/代理拦截。
- 解决：
  - 已在 `vite.config.js` 显式设置 `root: 'frontend'`。
  - 若端口占用，Vite 会切到 3001，按终端输出访问 `http://localhost:3001/`。
  - 如浏览器走系统代理，访问 `http://127.0.0.1:3000/` 或在代理排除列表加入 `localhost;127.0.0.1`。
  - 本机自检：
    ```powershell
    curl http://127.0.0.1:3000/ -UseBasicParsing
    netstat -ano | findstr :3000   # 确认由 node.exe 监听
    ```

### 5) 前端对外访问
- 使用 `npm run dev -- --host`，按 Vite “Network” 行给出的 IP 访问，如 `http://172.29.xx.xx:3000/`。

### 6) 一键复现本项目运行
```powershell
# 后端
cd D:\\program\\project5
python -m venv .venv
..\\.venv\\Scripts\\activate
pip install --upgrade pip setuptools wheel -i https://pypi.tuna.tsinghua.edu.cn/simple
pip install numpy==1.26.4 scipy==1.11.3 -i https://pypi.tuna.tsinghua.edu.cn/simple
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
cd backend
python init_db.py
python train_model.py
python app.py   # http://127.0.0.1:5000/health

# 前端
cd ..\\frontend
npm install
npm run dev -- --host   # 打开终端显示的 Local/Network 地址
```

## 项目结构

```
project5/
├── backend/                 # 后端代码
│   ├── app.py              # Flask主应用
│   ├── models/             # 数据模型
│   ├── api/                # API路由
│   ├── ml/                 # 机器学习模块
│   └── utils/              # 工具函数
├── frontend/               # 前端代码
│   ├── src/
│   │   ├── components/     # Vue组件
│   │   ├── views/          # 页面视图
│   │   ├── assets/         # 静态资源
│   │   └── utils/          # 工具函数
│   └── public/             # 公共资源
├── data/                   # 训练数据
├── models/                 # 训练好的模型
└── docs/                   # 文档
```

## 数据说明

系统基于120次现代复烧真实数据训练，包含：
- 时间序列温度数据
- 窑内气氛参数
- 胎土配方比例
- 匣钵厚度参数
- 木炭用量数据
- 最终成色评分

## 演示效果

现场演示：将瓷片放入指定窑位 → 10秒后大屏显示"预测成色87分"，评委可直观看到AI预测结果。


