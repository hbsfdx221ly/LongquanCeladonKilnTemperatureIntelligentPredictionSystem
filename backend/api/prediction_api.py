"""
预测管理API
"""

from flask import request, jsonify
from models import db, Batch, Prediction
from api import api_bp
from ml.predictor import PorcelainPredictor
import json

@api_bp.route('/predictions', methods=['GET'])
def get_predictions():
    """获取预测列表"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        batch_id = request.args.get('batch_id')
        
        query = Prediction.query
        if batch_id:
            query = query.filter_by(batch_id=batch_id)
        
        predictions = query.order_by(Prediction.prediction_time.desc())\
            .paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'success': True,
            'data': [prediction.to_dict() for prediction in predictions.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': predictions.total,
                'pages': predictions.pages
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/predictions/<int:prediction_id>', methods=['GET'])
def get_prediction(prediction_id):
    """获取单个预测详情"""
    try:
        prediction = Prediction.query.get_or_404(prediction_id)
        return jsonify({
            'success': True,
            'data': prediction.to_dict()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/predictions/predict', methods=['POST'])
def predict_batch():
    """执行批次预测"""
    try:
        data = request.get_json()
        batch_id = data.get('batch_id')
        
        if not batch_id:
            return jsonify({'success': False, 'error': '缺少批次ID'}), 400
        
        # 获取批次信息
        batch = Batch.query.get_or_404(batch_id)
        
        # 初始化预测器
        predictor = PorcelainPredictor()
        
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
        
        # 更新批次的预测分数
        batch.predicted_score = prediction_result['predicted_score']
        batch.confidence = prediction_result['confidence']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': prediction_result,
            'message': '预测完成'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/predictions/batch/<int:batch_id>', methods=['GET'])
def get_batch_predictions(batch_id):
    """获取批次的预测历史"""
    try:
        batch = Batch.query.get_or_404(batch_id)
        predictions = Prediction.query.filter_by(batch_id=batch_id)\
            .order_by(Prediction.prediction_time.desc()).all()
        
        return jsonify({
            'success': True,
            'data': [prediction.to_dict() for prediction in predictions]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/predictions/<int:prediction_id>/feedback', methods=['POST'])
def submit_prediction_feedback(prediction_id):
    """提交预测反馈"""
    try:
        prediction = Prediction.query.get_or_404(prediction_id)
        data = request.get_json()
        
        actual_score = data.get('actual_score')
        feedback_notes = data.get('feedback_notes', '')
        
        if actual_score is None:
            return jsonify({'success': False, 'error': '缺少实际评分'}), 400
        
        # 更新预测结果
        prediction.actual_score = actual_score
        prediction.feedback_notes = feedback_notes
        
        # 更新批次的实际评分
        batch = prediction.batch
        batch.actual_score = actual_score
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '反馈提交成功'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/predictions/accuracy', methods=['GET'])
def get_prediction_accuracy():
    """获取预测准确率统计"""
    try:
        # 获取有实际评分的预测
        predictions = Prediction.query.filter(Prediction.actual_score.isnot(None)).all()
        
        if not predictions:
            return jsonify({
                'success': True,
                'data': {
                    'total_predictions': 0,
                    'accuracy': 0,
                    'mae': 0,
                    'rmse': 0
                }
            })
        
        # 计算准确率指标
        total_predictions = len(predictions)
        errors = [abs(p.predicted_score - p.actual_score) for p in predictions]
        mae = sum(errors) / total_predictions  # 平均绝对误差
        rmse = (sum(e**2 for e in errors) / total_predictions) ** 0.5  # 均方根误差
        
        # 准确率：误差在5分以内视为准确
        accurate_predictions = sum(1 for e in errors if e <= 5)
        accuracy = accurate_predictions / total_predictions
        
        return jsonify({
            'success': True,
            'data': {
                'total_predictions': total_predictions,
                'accuracy': accuracy,
                'mae': mae,
                'rmse': rmse,
                'accurate_predictions': accurate_predictions
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/predictions/features/importance', methods=['GET'])
def get_feature_importance():
    """获取特征重要性分析"""
    try:
        # 获取最新的预测结果
        latest_predictions = Prediction.query.order_by(Prediction.prediction_time.desc()).limit(100).all()
        
        if not latest_predictions:
            return jsonify({
                'success': True,
                'data': {
                    'feature_importance': {},
                    'message': '暂无预测数据'
                }
            })
        
        # 计算平均特征重要性
        feature_importance = {}
        for prediction in latest_predictions:
            if prediction.feature_importance:
                importance = json.loads(prediction.feature_importance)
                for feature, value in importance.items():
                    if feature not in feature_importance:
                        feature_importance[feature] = []
                    feature_importance[feature].append(value)
        
        # 计算平均值
        avg_importance = {
            feature: sum(values) / len(values)
            for feature, values in feature_importance.items()
        }
        
        return jsonify({
            'success': True,
            'data': {
                'feature_importance': avg_importance,
                'sample_count': len(latest_predictions)
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
