"""
数据库初始化脚本
"""

from app import create_app
from models import db, Batch, SensorData, Prediction, Image, ModelVersion
import json
from datetime import datetime, timedelta
import random

def init_database():
    """初始化数据库"""
    app, _socketio = create_app()
    
    with app.app_context():
        # 创建所有表
        db.create_all()
        print("数据库表创建完成")
        
        # 插入示例数据
        insert_sample_data()
        print("示例数据插入完成")

def insert_sample_data():
    """插入示例数据"""
    
    # 创建示例批次
    sample_batches = []
    for i in range(5):
        batch = Batch(
            batch_name=f'龙泉青瓷批次_{i+1:03d}',
            start_time=datetime.utcnow() - timedelta(hours=random.randint(1, 48)),
            status=random.choice(['completed', 'firing', 'preparing']),
            clay_ratio=json.dumps({
                '高岭土': random.uniform(0.4, 0.6),
                '石英': random.uniform(0.2, 0.3),
                '长石': random.uniform(0.1, 0.2),
                '其他': random.uniform(0.05, 0.15)
            }),
            sagger_thickness=random.uniform(2.0, 5.0),
            charcoal_amount=random.uniform(50, 200),
            kiln_position=f'窑位_{chr(65+i)}',
            predicted_score=random.uniform(70, 95),
            actual_score=random.uniform(65, 98) if random.random() > 0.3 else None,
            confidence=random.uniform(0.7, 0.95)
        )
        sample_batches.append(batch)
        db.session.add(batch)
    
    db.session.commit()
    
    # 为每个批次创建传感器数据
    for batch in sample_batches:
        create_sensor_data_for_batch(batch)
        create_predictions_for_batch(batch)
        create_images_for_batch(batch)
    
    # 创建模型版本
    model_version = ModelVersion(
        version='v1.0.0',
        model_path='models/lightgbm_model_v1.pkl',
        accuracy=0.87,
        is_active=True,
        description='基于120次复烧数据的LightGBM模型，预测准确率87%'
    )
    db.session.add(model_version)
    
    db.session.commit()

def create_sensor_data_for_batch(batch):
    """为批次创建传感器数据"""
    start_time = batch.start_time
    duration_hours = random.randint(8, 24)
    
    for hour in range(duration_hours):
        for minute in range(0, 60, 15):  # 每15分钟一个数据点
            timestamp = start_time + timedelta(hours=hour, minutes=minute)
            
            # 模拟温度曲线（烧制过程中的典型温度变化）
            if hour < 2:
                temperature = 20 + (hour * 60) + (minute * 0.5)  # 升温阶段
            elif hour < 8:
                temperature = 140 + (hour - 2) * 20 + random.uniform(-5, 5)  # 保温阶段
            else:
                temperature = 240 + (hour - 8) * 10 + random.uniform(-10, 10)  # 高温阶段
            
            sensor_data = SensorData(
                batch_id=batch.id,
                timestamp=timestamp,
                temperature=temperature,
                position_x=random.uniform(0, 10),
                position_y=random.uniform(0, 5),
                position_z=random.uniform(0, 3),
                oxygen_level=random.uniform(15, 21),
                co_level=random.uniform(0, 100),
                co2_level=random.uniform(0, 5),
                pressure=random.uniform(101300, 102000),
                humidity=random.uniform(30, 80)
            )
            db.session.add(sensor_data)

def create_predictions_for_batch(batch):
    """为批次创建预测数据"""
    prediction = Prediction(
        batch_id=batch.id,
        input_features=json.dumps({
            'clay_ratio': json.loads(batch.clay_ratio),
            'sagger_thickness': batch.sagger_thickness,
            'charcoal_amount': batch.charcoal_amount,
            'kiln_position': batch.kiln_position
        }),
        model_version='v1.0.0',
        predicted_score=batch.predicted_score,
        confidence=batch.confidence,
        temperature_curve=json.dumps([
            {'time': i, 'temperature': 20 + i * 8 + random.uniform(-5, 5)}
            for i in range(24)
        ]),
        color_probability=json.dumps({
            '青绿色': random.uniform(0.3, 0.8),
            '天青色': random.uniform(0.1, 0.4),
            '粉青色': random.uniform(0.05, 0.3),
            '梅子青': random.uniform(0.1, 0.5),
            '其他': random.uniform(0.05, 0.2)
        }),
        feature_importance=json.dumps({
            '胎土配方': random.uniform(0.2, 0.4),
            '匣钵厚度': random.uniform(0.1, 0.3),
            '木炭用量': random.uniform(0.15, 0.35),
            '窑位位置': random.uniform(0.1, 0.25)
        }),
        prediction_reason=f'基于历史数据预测，{batch.kiln_position}位置烧制条件良好，预计成色评分{batch.predicted_score:.1f}分'
    )
    db.session.add(prediction)

def create_images_for_batch(batch):
    """为批次创建图像数据"""
    image_types = ['before_firing', 'after_firing']
    
    for img_type in image_types:
        image = Image(
            batch_id=batch.id,
            image_type=img_type,
            file_path=f'uploads/batch_{batch.id}_{img_type}.jpg',
            file_size=random.randint(500000, 2000000),
            color_analysis=json.dumps({
                'dominant_color': random.choice(['青绿', '天青', '粉青', '梅子青']),
                'color_saturation': random.uniform(0.6, 0.9),
                'brightness': random.uniform(0.4, 0.8)
            }),
            defect_detection=json.dumps({
                'cracks': random.randint(0, 3),
                'bubbles': random.randint(0, 5),
                'color_unevenness': random.uniform(0, 0.3)
            }),
            quality_score=random.uniform(70, 95)
        )
        db.session.add(image)

if __name__ == '__main__':
    init_database()
