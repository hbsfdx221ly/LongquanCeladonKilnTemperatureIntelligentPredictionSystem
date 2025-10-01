#!/usr/bin/env python3
"""
启动后端服务
"""

import os
import sys
import subprocess

def main():
    print("启动龙泉青瓷窑温智能预测系统后端服务...")
    print("=" * 50)
    
    # 检查Python环境
    if sys.version_info < (3, 8):
        print("错误: 需要Python 3.8或更高版本")
        sys.exit(1)
    
    # 切换到backend目录
    backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
    os.chdir(backend_dir)
    
    # 检查依赖
    try:
        import flask
        import lightgbm
        import pandas
        print("✓ 依赖检查通过")
    except ImportError as e:
        print(f"✗ 缺少依赖: {e}")
        print("请运行: pip install -r requirements.txt")
        sys.exit(1)
    
    # 初始化数据库
    print("初始化数据库...")
    try:
        subprocess.run([sys.executable, 'init_db.py'], check=True)
        print("✓ 数据库初始化完成")
    except subprocess.CalledProcessError as e:
        print(f"✗ 数据库初始化失败: {e}")
        sys.exit(1)
    
    # 训练模型（如果不存在）
    model_path = 'models/lightgbm_model.pkl'
    if not os.path.exists(model_path):
        print("训练机器学习模型...")
        try:
            subprocess.run([sys.executable, 'train_model.py'], check=True)
            print("✓ 模型训练完成")
        except subprocess.CalledProcessError as e:
            print(f"✗ 模型训练失败: {e}")
            print("将使用规则预测模式")
    
    # 启动Flask应用
    print("启动Flask应用...")
    try:
        subprocess.run([sys.executable, 'app.py'], check=True)
    except KeyboardInterrupt:
        print("\n服务已停止")
    except subprocess.CalledProcessError as e:
        print(f"✗ 服务启动失败: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
