"""
批次管理API
"""

from flask import request, jsonify
from models import db, Batch, SensorData, Prediction, Image
from api import api_bp
import json
from datetime import datetime

@api_bp.route('/batches', methods=['GET'])
def get_batches():
    """获取所有批次列表"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        status = request.args.get('status')
        
        query = Batch.query
        if status:
            query = query.filter_by(status=status)
        
        batches = query.order_by(Batch.start_time.desc())\
            .paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'success': True,
            'data': [batch.to_dict() for batch in batches.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': batches.total,
                'pages': batches.pages
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/batches/<int:batch_id>', methods=['GET'])
def get_batch(batch_id):
    """获取单个批次详情"""
    try:
        batch = Batch.query.get_or_404(batch_id)
        return jsonify({
            'success': True,
            'data': batch.to_dict()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/batches', methods=['POST'])
def create_batch():
    """创建新批次"""
    try:
        data = request.get_json()
        
        # 验证必需字段
        required_fields = ['batch_name', 'clay_ratio', 'sagger_thickness', 'charcoal_amount', 'kiln_position']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'缺少必需字段: {field}'}), 400
        
        # 创建新批次
        batch = Batch(
            batch_name=data['batch_name'],
            clay_ratio=json.dumps(data['clay_ratio']),
            sagger_thickness=data['sagger_thickness'],
            charcoal_amount=data['charcoal_amount'],
            kiln_position=data['kiln_position'],
            status='preparing'
        )
        
        db.session.add(batch)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': batch.to_dict(),
            'message': '批次创建成功'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/batches/<int:batch_id>', methods=['PUT'])
def update_batch(batch_id):
    """更新批次信息"""
    try:
        batch = Batch.query.get_or_404(batch_id)
        data = request.get_json()
        
        # 更新字段
        if 'batch_name' in data:
            batch.batch_name = data['batch_name']
        if 'clay_ratio' in data:
            batch.clay_ratio = json.dumps(data['clay_ratio'])
        if 'sagger_thickness' in data:
            batch.sagger_thickness = data['sagger_thickness']
        if 'charcoal_amount' in data:
            batch.charcoal_amount = data['charcoal_amount']
        if 'kiln_position' in data:
            batch.kiln_position = data['kiln_position']
        if 'status' in data:
            batch.status = data['status']
            if data['status'] == 'completed' and not batch.end_time:
                batch.end_time = datetime.utcnow()
        if 'actual_score' in data:
            batch.actual_score = data['actual_score']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': batch.to_dict(),
            'message': '批次更新成功'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/batches/<int:batch_id>', methods=['DELETE'])
def delete_batch(batch_id):
    """删除批次"""
    try:
        batch = Batch.query.get_or_404(batch_id)
        
        # 删除关联数据（由于设置了cascade，会自动删除）
        db.session.delete(batch)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '批次删除成功'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/batches/<int:batch_id>/start', methods=['POST'])
def start_batch(batch_id):
    """开始烧制批次"""
    try:
        batch = Batch.query.get_or_404(batch_id)
        
        if batch.status != 'preparing':
            return jsonify({'success': False, 'error': '批次状态不允许开始烧制'}), 400
        
        batch.status = 'firing'
        batch.start_time = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': batch.to_dict(),
            'message': '烧制已开始'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/batches/<int:batch_id>/complete', methods=['POST'])
def complete_batch(batch_id):
    """完成烧制批次"""
    try:
        batch = Batch.query.get_or_404(batch_id)
        
        if batch.status != 'firing':
            return jsonify({'success': False, 'error': '批次状态不允许完成烧制'}), 400
        
        batch.status = 'completed'
        batch.end_time = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': batch.to_dict(),
            'message': '烧制已完成'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/batches/<int:batch_id>/summary', methods=['GET'])
def get_batch_summary(batch_id):
    """获取批次汇总信息"""
    try:
        batch = Batch.query.get_or_404(batch_id)
        
        # 获取传感器数据统计
        sensor_count = SensorData.query.filter_by(batch_id=batch_id).count()
        latest_sensor = SensorData.query.filter_by(batch_id=batch_id)\
            .order_by(SensorData.timestamp.desc()).first()
        
        # 获取预测数据
        predictions = Prediction.query.filter_by(batch_id=batch_id).all()
        
        # 获取图像数据
        images = Image.query.filter_by(batch_id=batch_id).all()
        
        summary = {
            'batch_info': batch.to_dict(),
            'sensor_data_count': sensor_count,
            'latest_temperature': latest_sensor.temperature if latest_sensor else None,
            'latest_timestamp': latest_sensor.timestamp.isoformat() if latest_sensor else None,
            'predictions_count': len(predictions),
            'images_count': len(images),
            'average_quality_score': sum(img.quality_score for img in images) / len(images) if images else None
        }
        
        return jsonify({
            'success': True,
            'data': summary
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
