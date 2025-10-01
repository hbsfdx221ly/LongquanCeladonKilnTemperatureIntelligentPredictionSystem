"""
图像管理API
"""

from flask import request, jsonify, send_file
from models import db, Image, Batch
from api import api_bp
import os
import json
from werkzeug.utils import secure_filename
from datetime import datetime

# 允许的文件扩展名
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}

def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@api_bp.route('/images', methods=['GET'])
def get_images():
    """获取图像列表"""
    try:
        batch_id = request.args.get('batch_id')
        image_type = request.args.get('image_type')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        query = Image.query
        
        if batch_id:
            query = query.filter_by(batch_id=batch_id)
        if image_type:
            query = query.filter_by(image_type=image_type)
        
        images = query.order_by(Image.upload_time.desc())\
            .paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'success': True,
            'data': [image.to_dict() for image in images.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': images.total,
                'pages': images.pages
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/images/<int:image_id>', methods=['GET'])
def get_image(image_id):
    """获取单个图像信息"""
    try:
        image = Image.query.get_or_404(image_id)
        return jsonify({
            'success': True,
            'data': image.to_dict()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/images/<int:image_id>/file', methods=['GET'])
def get_image_file(image_id):
    """获取图像文件"""
    try:
        image = Image.query.get_or_404(image_id)
        
        if not os.path.exists(image.file_path):
            return jsonify({'success': False, 'error': '图像文件不存在'}), 404
        
        return send_file(image.file_path, as_attachment=False)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/images', methods=['POST'])
def upload_image():
    """上传图像"""
    try:
        # 检查是否有文件
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': '没有选择文件'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': '没有选择文件'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'success': False, 'error': '不支持的文件格式'}), 400
        
        # 获取表单数据
        batch_id = request.form.get('batch_id')
        image_type = request.form.get('image_type', 'before_firing')
        
        if not batch_id:
            return jsonify({'success': False, 'error': '缺少批次ID'}), 400
        
        # 验证批次存在
        batch = Batch.query.get(batch_id)
        if not batch:
            return jsonify({'success': False, 'error': '批次不存在'}), 400
        
        # 生成安全的文件名
        filename = secure_filename(file.filename)
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        filename = f"batch_{batch_id}_{image_type}_{timestamp}_{filename}"
        
        # 确保上传目录存在
        upload_dir = 'uploads'
        os.makedirs(upload_dir, exist_ok=True)
        
        # 保存文件
        file_path = os.path.join(upload_dir, filename)
        file.save(file_path)
        
        # 获取文件大小
        file_size = os.path.getsize(file_path)
        
        # 创建图像记录
        image = Image(
            batch_id=batch_id,
            image_type=image_type,
            file_path=file_path,
            file_size=file_size
        )
        
        db.session.add(image)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': image.to_dict(),
            'message': '图像上传成功'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/images/<int:image_id>', methods=['PUT'])
def update_image(image_id):
    """更新图像信息"""
    try:
        image = Image.query.get_or_404(image_id)
        data = request.get_json()
        
        # 更新字段
        if 'image_type' in data:
            image.image_type = data['image_type']
        if 'color_analysis' in data:
            image.color_analysis = json.dumps(data['color_analysis'])
        if 'defect_detection' in data:
            image.defect_detection = json.dumps(data['defect_detection'])
        if 'quality_score' in data:
            image.quality_score = data['quality_score']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': image.to_dict(),
            'message': '图像信息更新成功'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/images/<int:image_id>', methods=['DELETE'])
def delete_image(image_id):
    """删除图像"""
    try:
        image = Image.query.get_or_404(image_id)
        
        # 删除文件
        if os.path.exists(image.file_path):
            os.remove(image.file_path)
        
        # 删除数据库记录
        db.session.delete(image)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '图像删除成功'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/images/batch/<int:batch_id>/analysis', methods=['POST'])
def analyze_image(image_id):
    """分析图像（颜色分析、缺陷检测等）"""
    try:
        image = Image.query.get_or_404(image_id)
        
        if not os.path.exists(image.file_path):
            return jsonify({'success': False, 'error': '图像文件不存在'}), 404
        
        # 这里可以集成图像分析算法
        # 目前返回模拟数据
        color_analysis = {
            'dominant_color': '青绿色',
            'color_saturation': 0.75,
            'brightness': 0.65,
            'color_distribution': {
                '青绿色': 0.4,
                '天青色': 0.3,
                '粉青色': 0.2,
                '其他': 0.1
            }
        }
        
        defect_detection = {
            'cracks': 0,
            'bubbles': 1,
            'color_unevenness': 0.1,
            'overall_quality': 'good'
        }
        
        quality_score = 85.5
        
        # 更新图像分析结果
        image.color_analysis = json.dumps(color_analysis)
        image.defect_detection = json.dumps(defect_detection)
        image.quality_score = quality_score
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': {
                'color_analysis': color_analysis,
                'defect_detection': defect_detection,
                'quality_score': quality_score
            },
            'message': '图像分析完成'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/images/batch/<int:batch_id>/before-after', methods=['GET'])
def get_before_after_images(batch_id):
    """获取批次烧制前后的对比图像"""
    try:
        batch = Batch.query.get_or_404(batch_id)
        
        before_images = Image.query.filter_by(
            batch_id=batch_id, 
            image_type='before_firing'
        ).all()
        
        after_images = Image.query.filter_by(
            batch_id=batch_id, 
            image_type='after_firing'
        ).all()
        
        return jsonify({
            'success': True,
            'data': {
                'before_firing': [img.to_dict() for img in before_images],
                'after_firing': [img.to_dict() for img in after_images]
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
