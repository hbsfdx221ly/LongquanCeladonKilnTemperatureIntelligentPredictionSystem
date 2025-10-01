"""
传感器数据API
"""

from flask import request, jsonify
from models import db, SensorData, Batch
from api import api_bp
from datetime import datetime, timedelta
import json

@api_bp.route('/sensor-data', methods=['GET'])
def get_sensor_data():
    """获取传感器数据"""
    try:
        batch_id = request.args.get('batch_id')
        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time')
        limit = request.args.get('limit', 1000, type=int)
        
        query = SensorData.query
        
        if batch_id:
            query = query.filter_by(batch_id=batch_id)
        
        if start_time:
            start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            query = query.filter(SensorData.timestamp >= start_dt)
        
        if end_time:
            end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
            query = query.filter(SensorData.timestamp <= end_dt)
        
        sensor_data = query.order_by(SensorData.timestamp.desc()).limit(limit).all()
        
        return jsonify({
            'success': True,
            'data': [data.to_dict() for data in sensor_data]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/sensor-data', methods=['POST'])
def add_sensor_data():
    """添加传感器数据"""
    try:
        data = request.get_json()
        
        # 验证必需字段
        required_fields = ['batch_id', 'temperature']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'缺少必需字段: {field}'}), 400
        
        # 验证批次存在
        batch = Batch.query.get(data['batch_id'])
        if not batch:
            return jsonify({'success': False, 'error': '批次不存在'}), 400
        
        # 创建传感器数据
        sensor_data = SensorData(
            batch_id=data['batch_id'],
            temperature=data['temperature'],
            position_x=data.get('position_x', 0),
            position_y=data.get('position_y', 0),
            position_z=data.get('position_z', 0),
            oxygen_level=data.get('oxygen_level'),
            co_level=data.get('co_level'),
            co2_level=data.get('co2_level'),
            pressure=data.get('pressure'),
            humidity=data.get('humidity'),
            timestamp=datetime.fromisoformat(data.get('timestamp', datetime.utcnow().isoformat()))
        )
        
        db.session.add(sensor_data)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': sensor_data.to_dict(),
            'message': '传感器数据添加成功'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/sensor-data/batch/<int:batch_id>/latest', methods=['GET'])
def get_latest_sensor_data(batch_id):
    """获取批次最新传感器数据"""
    try:
        batch = Batch.query.get_or_404(batch_id)
        
        latest_data = SensorData.query.filter_by(batch_id=batch_id)\
            .order_by(SensorData.timestamp.desc()).first()
        
        if not latest_data:
            return jsonify({
                'success': True,
                'data': None,
                'message': '暂无传感器数据'
            })
        
        return jsonify({
            'success': True,
            'data': latest_data.to_dict()
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/sensor-data/batch/<int:batch_id>/temperature-curve', methods=['GET'])
def get_temperature_curve(batch_id):
    """获取批次温度曲线"""
    try:
        batch = Batch.query.get_or_404(batch_id)
        
        # 获取时间范围参数
        hours = request.args.get('hours', 24, type=int)
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=hours)
        
        # 获取温度数据
        temperature_data = SensorData.query.filter(
            SensorData.batch_id == batch_id,
            SensorData.timestamp >= start_time,
            SensorData.timestamp <= end_time
        ).order_by(SensorData.timestamp.asc()).all()
        
        # 构建温度曲线数据
        curve_data = []
        for data in temperature_data:
            curve_data.append({
                'timestamp': data.timestamp.isoformat(),
                'temperature': data.temperature,
                'position': {
                    'x': data.position_x,
                    'y': data.position_y,
                    'z': data.position_z
                }
            })
        
        return jsonify({
            'success': True,
            'data': {
                'batch_id': batch_id,
                'time_range': {
                    'start': start_time.isoformat(),
                    'end': end_time.isoformat()
                },
                'temperature_curve': curve_data
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/sensor-data/batch/<int:batch_id>/heatmap', methods=['GET'])
def get_temperature_heatmap(batch_id):
    """获取温度热力图数据"""
    try:
        batch = Batch.query.get_or_404(batch_id)
        
        # 获取最新的传感器数据
        latest_data = SensorData.query.filter_by(batch_id=batch_id)\
            .order_by(SensorData.timestamp.desc()).limit(100).all()
        
        if not latest_data:
            return jsonify({
                'success': True,
                'data': {
                    'heatmap_data': [],
                    'message': '暂无传感器数据'
                }
            })
        
        # 构建热力图数据
        heatmap_data = []
        for data in latest_data:
            heatmap_data.append({
                'x': data.position_x,
                'y': data.position_y,
                'z': data.position_z,
                'temperature': data.temperature,
                'timestamp': data.timestamp.isoformat()
            })
        
        return jsonify({
            'success': True,
            'data': {
                'batch_id': batch_id,
                'heatmap_data': heatmap_data
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/sensor-data/batch/<int:batch_id>/statistics', methods=['GET'])
def get_sensor_statistics(batch_id):
    """获取传感器数据统计"""
    try:
        batch = Batch.query.get_or_404(batch_id)
        
        # 获取时间范围参数
        hours = request.args.get('hours', 24, type=int)
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=hours)
        
        # 获取统计数据
        sensor_data = SensorData.query.filter(
            SensorData.batch_id == batch_id,
            SensorData.timestamp >= start_time,
            SensorData.timestamp <= end_time
        ).all()
        
        if not sensor_data:
            return jsonify({
                'success': True,
                'data': {
                    'message': '暂无传感器数据'
                }
            })
        
        # 计算统计指标
        temperatures = [data.temperature for data in sensor_data if data.temperature is not None]
        oxygen_levels = [data.oxygen_level for data in sensor_data if data.oxygen_level is not None]
        
        statistics = {
            'data_count': len(sensor_data),
            'time_range': {
                'start': start_time.isoformat(),
                'end': end_time.isoformat()
            },
            'temperature': {
                'min': min(temperatures) if temperatures else None,
                'max': max(temperatures) if temperatures else None,
                'avg': sum(temperatures) / len(temperatures) if temperatures else None,
                'current': temperatures[-1] if temperatures else None
            },
            'oxygen': {
                'min': min(oxygen_levels) if oxygen_levels else None,
                'max': max(oxygen_levels) if oxygen_levels else None,
                'avg': sum(oxygen_levels) / len(oxygen_levels) if oxygen_levels else None,
                'current': oxygen_levels[-1] if oxygen_levels else None
            }
        }
        
        return jsonify({
            'success': True,
            'data': statistics
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
