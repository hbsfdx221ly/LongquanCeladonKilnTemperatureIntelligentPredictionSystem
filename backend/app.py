"""
龙泉青瓷窑温智能预测系统 - Flask主应用
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import os
import sys

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import db, Batch, SensorData, Prediction, Image, ModelVersion
from config import config
from api import api_bp
from ml.predictor import PorcelainPredictor

def create_app(config_name='default'):
    """创建Flask应用"""
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # 初始化扩展
    db.init_app(app)
    CORS(app, origins="*")
    socketio = SocketIO(app, cors_allowed_origins="*")
    
    # 注册蓝图
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # 初始化机器学习预测器
    predictor = PorcelainPredictor()
    
    @app.route('/')
    def index():
        return jsonify({
            'message': '龙泉青瓷窑温智能预测系统',
            'version': '1.0.0',
            'status': 'running'
        })
    
    @app.route('/health')
    def health():
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'ml_model': 'loaded' if predictor.is_loaded() else 'not_loaded'
        })
    
    # WebSocket事件处理
    @socketio.on('connect')
    def handle_connect():
        print('客户端已连接')
        emit('status', {'message': '连接成功'})
    
    @socketio.on('disconnect')
    def handle_disconnect():
        print('客户端已断开')
    
    @socketio.on('request_prediction')
    def handle_prediction_request(data):
        """处理预测请求"""
        try:
            batch_id = data.get('batch_id')
            if not batch_id:
                emit('prediction_error', {'error': '缺少批次ID'})
                return
            
            # 获取批次信息
            batch = Batch.query.get(batch_id)
            if not batch:
                emit('prediction_error', {'error': '批次不存在'})
                return
            
            # 执行预测
            prediction_result = predictor.predict_batch(batch)
            
            # 保存预测结果
            prediction = Prediction(
                batch_id=batch.id,
                input_features=prediction_result['input_features'],
                model_version=prediction_result['model_version'],
                predicted_score=prediction_result['predicted_score'],
                confidence=prediction_result['confidence'],
                temperature_curve=prediction_result['temperature_curve'],
                color_probability=prediction_result['color_probability'],
                feature_importance=prediction_result['feature_importance'],
                prediction_reason=prediction_result['prediction_reason']
            )
            
            db.session.add(prediction)
            batch.predicted_score = prediction_result['predicted_score']
            batch.confidence = prediction_result['confidence']
            db.session.commit()
            
            # 发送预测结果
            emit('prediction_result', prediction_result)
            
        except Exception as e:
            print(f'预测错误: {str(e)}')
            emit('prediction_error', {'error': str(e)})
    
    @socketio.on('request_monitoring')
    def handle_monitoring_request(data):
        """处理监控请求"""
        try:
            batch_id = data.get('batch_id')
            if not batch_id:
                emit('monitoring_error', {'error': '缺少批次ID'})
                return
            
            # 获取最新的传感器数据
            latest_data = SensorData.query.filter_by(batch_id=batch_id)\
                .order_by(SensorData.timestamp.desc()).first()
            
            if latest_data:
                emit('sensor_data', latest_data.to_dict())
            else:
                emit('monitoring_error', {'error': '暂无传感器数据'})
                
        except Exception as e:
            print(f'监控错误: {str(e)}')
            emit('monitoring_error', {'error': str(e)})
    
    return app, socketio

if __name__ == '__main__':
    app, socketio = create_app()
    
    # 创建上传目录
    os.makedirs('uploads', exist_ok=True)
    os.makedirs('models', exist_ok=True)
    
    # 启动应用
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)
