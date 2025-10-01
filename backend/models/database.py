"""
数据库模型定义
龙泉青瓷窑温智能预测系统
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class Batch(db.Model):
    """烧制批次表"""
    __tablename__ = 'batches'
    
    id = db.Column(db.Integer, primary_key=True)
    batch_name = db.Column(db.String(100), nullable=False, comment='批次名称')
    start_time = db.Column(db.DateTime, default=datetime.utcnow, comment='开始时间')
    end_time = db.Column(db.DateTime, comment='结束时间')
    status = db.Column(db.String(20), default='preparing', comment='状态: preparing, firing, completed, failed')
    
    # 烧制参数
    clay_ratio = db.Column(db.Text, comment='胎土配方比例(JSON)')
    sagger_thickness = db.Column(db.Float, comment='匣钵厚度(mm)')
    charcoal_amount = db.Column(db.Float, comment='木炭用量(kg)')
    kiln_position = db.Column(db.String(50), comment='窑位编号')
    
    # 预测结果
    predicted_score = db.Column(db.Float, comment='预测成色评分')
    actual_score = db.Column(db.Float, comment='实际成色评分')
    confidence = db.Column(db.Float, comment='预测置信度')
    
    # 关联关系
    sensor_data = db.relationship('SensorData', backref='batch', lazy=True, cascade='all, delete-orphan')
    predictions = db.relationship('Prediction', backref='batch', lazy=True, cascade='all, delete-orphan')
    images = db.relationship('Image', backref='batch', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'batch_name': self.batch_name,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'status': self.status,
            'clay_ratio': json.loads(self.clay_ratio) if self.clay_ratio else None,
            'sagger_thickness': self.sagger_thickness,
            'charcoal_amount': self.charcoal_amount,
            'kiln_position': self.kiln_position,
            'predicted_score': self.predicted_score,
            'actual_score': self.actual_score,
            'confidence': self.confidence
        }

class SensorData(db.Model):
    """传感器数据表"""
    __tablename__ = 'sensor_data'
    
    id = db.Column(db.Integer, primary_key=True)
    batch_id = db.Column(db.Integer, db.ForeignKey('batches.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, comment='时间戳')
    
    # 温度数据
    temperature = db.Column(db.Float, comment='温度(°C)')
    position_x = db.Column(db.Float, comment='X坐标位置')
    position_y = db.Column(db.Float, comment='Y坐标位置')
    position_z = db.Column(db.Float, comment='Z坐标位置')
    
    # 气氛数据
    oxygen_level = db.Column(db.Float, comment='氧气浓度(%)')
    co_level = db.Column(db.Float, comment='一氧化碳浓度(ppm)')
    co2_level = db.Column(db.Float, comment='二氧化碳浓度(%)')
    
    # 其他参数
    pressure = db.Column(db.Float, comment='窑内压力(Pa)')
    humidity = db.Column(db.Float, comment='湿度(%)')
    
    def to_dict(self):
        return {
            'id': self.id,
            'batch_id': self.batch_id,
            'timestamp': self.timestamp.isoformat(),
            'temperature': self.temperature,
            'position': {
                'x': self.position_x,
                'y': self.position_y,
                'z': self.position_z
            },
            'atmosphere': {
                'oxygen': self.oxygen_level,
                'co': self.co_level,
                'co2': self.co2_level
            },
            'pressure': self.pressure,
            'humidity': self.humidity
        }

class Prediction(db.Model):
    """预测结果表"""
    __tablename__ = 'predictions'
    
    id = db.Column(db.Integer, primary_key=True)
    batch_id = db.Column(db.Integer, db.ForeignKey('batches.id'), nullable=False)
    prediction_time = db.Column(db.DateTime, default=datetime.utcnow, comment='预测时间')
    
    # 预测参数
    input_features = db.Column(db.Text, comment='输入特征(JSON)')
    model_version = db.Column(db.String(50), comment='模型版本')
    
    # 预测结果
    predicted_score = db.Column(db.Float, comment='预测成色评分')
    confidence = db.Column(db.Float, comment='预测置信度')
    temperature_curve = db.Column(db.Text, comment='预测温度曲线(JSON)')
    color_probability = db.Column(db.Text, comment='成色概率分布(JSON)')
    
    # 模型解释
    feature_importance = db.Column(db.Text, comment='特征重要性(JSON)')
    prediction_reason = db.Column(db.Text, comment='预测原因说明')
    
    def to_dict(self):
        return {
            'id': self.id,
            'batch_id': self.batch_id,
            'prediction_time': self.prediction_time.isoformat(),
            'input_features': json.loads(self.input_features) if self.input_features else None,
            'model_version': self.model_version,
            'predicted_score': self.predicted_score,
            'confidence': self.confidence,
            'temperature_curve': json.loads(self.temperature_curve) if self.temperature_curve else None,
            'color_probability': json.loads(self.color_probability) if self.color_probability else None,
            'feature_importance': json.loads(self.feature_importance) if self.feature_importance else None,
            'prediction_reason': self.prediction_reason
        }

class Image(db.Model):
    """图像数据表"""
    __tablename__ = 'images'
    
    id = db.Column(db.Integer, primary_key=True)
    batch_id = db.Column(db.Integer, db.ForeignKey('batches.id'), nullable=False)
    image_type = db.Column(db.String(50), comment='图像类型: before_firing, after_firing, defect_analysis')
    file_path = db.Column(db.String(255), comment='文件路径')
    file_size = db.Column(db.Integer, comment='文件大小(bytes)')
    upload_time = db.Column(db.DateTime, default=datetime.utcnow, comment='上传时间')
    
    # 图像分析结果
    color_analysis = db.Column(db.Text, comment='颜色分析结果(JSON)')
    defect_detection = db.Column(db.Text, comment='缺陷检测结果(JSON)')
    quality_score = db.Column(db.Float, comment='质量评分')
    
    def to_dict(self):
        return {
            'id': self.id,
            'batch_id': self.batch_id,
            'image_type': self.image_type,
            'file_path': self.file_path,
            'file_size': self.file_size,
            'upload_time': self.upload_time.isoformat(),
            'color_analysis': json.loads(self.color_analysis) if self.color_analysis else None,
            'defect_detection': json.loads(self.defect_detection) if self.defect_detection else None,
            'quality_score': self.quality_score
        }

class ModelVersion(db.Model):
    """模型版本管理表"""
    __tablename__ = 'model_versions'
    
    id = db.Column(db.Integer, primary_key=True)
    version = db.Column(db.String(50), unique=True, nullable=False, comment='模型版本号')
    model_path = db.Column(db.String(255), comment='模型文件路径')
    accuracy = db.Column(db.Float, comment='模型准确率')
    created_time = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    is_active = db.Column(db.Boolean, default=False, comment='是否激活')
    description = db.Column(db.Text, comment='模型描述')
    
    def to_dict(self):
        return {
            'id': self.id,
            'version': self.version,
            'model_path': self.model_path,
            'accuracy': self.accuracy,
            'created_time': self.created_time.isoformat(),
            'is_active': self.is_active,
            'description': self.description
        }


