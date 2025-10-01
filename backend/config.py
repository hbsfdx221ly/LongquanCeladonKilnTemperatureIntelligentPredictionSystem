"""
应用配置文件
"""

import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """基础配置"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'porcelain-ai-secret-key-2024'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 数据库配置
    # 默认使用本地SQLite，免安装MySQL。如需MySQL，设置环境变量 DATABASE_URL
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///../porcelain_ai.db'
    
    # 机器学习模型配置
    MODEL_PATH = os.environ.get('MODEL_PATH') or 'models/'
    TRAINING_DATA_PATH = os.environ.get('TRAINING_DATA_PATH') or 'data/'
    
    # 文件上传配置
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or 'uploads/'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    
    # WebSocket配置
    SOCKETIO_ASYNC_MODE = 'threading'
    
    # 预测配置
    PREDICTION_CONFIDENCE_THRESHOLD = 0.7
    TEMPERATURE_PREDICTION_HORIZON = 24  # 预测24小时内的温度曲线

class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    SQLALCHEMY_ECHO = True

class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    SQLALCHEMY_ECHO = False

class TestingConfig(Config):
    """测试环境配置"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
