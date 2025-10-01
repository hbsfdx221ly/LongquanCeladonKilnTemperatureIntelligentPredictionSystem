"""
龙泉青瓷预测器
基于LightGBM的成色预测模型
"""

import json
import numpy as np
import pandas as pd
import lightgbm as lgb
import joblib
import os
from datetime import datetime
from typing import Dict, List, Any, Optional

class PorcelainPredictor:
    """龙泉青瓷成色预测器"""
    
    def __init__(self, model_path: str = 'models/lightgbm_model.pkl'):
        self.model_path = model_path
        self.model = None
        self.feature_names = None
        self.is_loaded_flag = False
        self.load_model()
    
    def load_model(self):
        """加载训练好的模型"""
        try:
            if os.path.exists(self.model_path):
                model_data = joblib.load(self.model_path)
                self.model = model_data['model']
                self.feature_names = model_data['feature_names']
                self.is_loaded_flag = True
                print(f"模型加载成功: {self.model_path}")
            else:
                print(f"模型文件不存在: {self.model_path}")
                self.is_loaded_flag = False
        except Exception as e:
            print(f"模型加载失败: {str(e)}")
            self.is_loaded_flag = False
    
    def is_loaded(self) -> bool:
        """检查模型是否已加载"""
        return self.is_loaded_flag
    
    def extract_features(self, batch_data: Dict[str, Any]) -> np.ndarray:
        """从批次数据中提取特征"""
        features = []
        
        # 胎土配方特征
        clay_ratio = batch_data.get('clay_ratio', {})
        if isinstance(clay_ratio, str):
            clay_ratio = json.loads(clay_ratio)
        
        features.extend([
            clay_ratio.get('高岭土', 0.5),
            clay_ratio.get('石英', 0.25),
            clay_ratio.get('长石', 0.15),
            clay_ratio.get('其他', 0.1)
        ])
        
        # 烧制参数特征
        features.extend([
            batch_data.get('sagger_thickness', 3.0),
            batch_data.get('charcoal_amount', 100.0)
        ])
        
        # 窑位特征（编码为数值）
        kiln_position = batch_data.get('kiln_position', '窑位_A')
        position_encoded = self._encode_kiln_position(kiln_position)
        features.extend(position_encoded)
        
        # 时间特征
        start_time = batch_data.get('start_time')
        if start_time:
            if isinstance(start_time, str):
                start_time = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            features.extend([
                start_time.hour,
                start_time.month,
                start_time.weekday()
            ])
        else:
            features.extend([12, 6, 0])  # 默认值
        
        # 环境特征（如果有传感器数据）
        features.extend([
            batch_data.get('avg_temperature', 1200.0),
            batch_data.get('avg_oxygen', 18.0),
            batch_data.get('avg_pressure', 101500.0)
        ])
        
        return np.array(features).reshape(1, -1)
    
    def _encode_kiln_position(self, position: str) -> List[float]:
        """编码窑位位置"""
        # 简单的窑位编码：A=1, B=2, C=3, D=4, E=5
        position_map = {
            '窑位_A': [1, 0, 0, 0, 0],
            '窑位_B': [0, 1, 0, 0, 0],
            '窑位_C': [0, 0, 1, 0, 0],
            '窑位_D': [0, 0, 0, 1, 0],
            '窑位_E': [0, 0, 0, 0, 1]
        }
        return position_map.get(position, [0, 0, 0, 0, 0])
    
    def predict_score(self, features: np.ndarray) -> float:
        """预测成色评分"""
        if not self.is_loaded():
            # 如果模型未加载，返回基于规则的预测
            return self._rule_based_prediction(features)
        
        try:
            prediction = self.model.predict(features)
            return float(prediction[0])
        except Exception as e:
            print(f"预测失败: {str(e)}")
            return self._rule_based_prediction(features)
    
    def _rule_based_prediction(self, features: np.ndarray) -> float:
        """基于规则的预测（备用方案）"""
        # 简单的规则预测
        base_score = 70.0
        
        # 胎土配方影响
        clay_ratio_score = (features[0, 0] * 0.4 + features[0, 1] * 0.3 + 
                           features[0, 2] * 0.2 + features[0, 3] * 0.1) * 20
        
        # 匣钵厚度影响
        thickness_score = max(0, 10 - abs(features[0, 4] - 3.0) * 2)
        
        # 木炭用量影响
        charcoal_score = max(0, 10 - abs(features[0, 5] - 100.0) / 10)
        
        # 窑位影响
        position_score = 5.0  # 默认分数
        
        total_score = base_score + clay_ratio_score + thickness_score + charcoal_score + position_score
        return min(100.0, max(0.0, total_score))
    
    def predict_batch(self, batch_data: Dict[str, Any]) -> Dict[str, Any]:
        """预测批次成色"""
        try:
            # 提取特征
            features = self.extract_features(batch_data)
            
            # 预测评分
            predicted_score = self.predict_score(features)
            
            # 计算置信度
            confidence = self._calculate_confidence(features, predicted_score)
            
            # 生成温度曲线预测
            temperature_curve = self._generate_temperature_curve(batch_data)
            
            # 生成成色概率分布
            color_probability = self._generate_color_probability(predicted_score)
            
            # 生成特征重要性
            feature_importance = self._generate_feature_importance(features)
            
            # 生成预测原因
            prediction_reason = self._generate_prediction_reason(
                batch_data, predicted_score, feature_importance
            )
            
            return {
                'input_features': {
                    'clay_ratio': batch_data.get('clay_ratio'),
                    'sagger_thickness': batch_data.get('sagger_thickness'),
                    'charcoal_amount': batch_data.get('charcoal_amount'),
                    'kiln_position': batch_data.get('kiln_position')
                },
                'model_version': 'v1.0.0',
                'predicted_score': predicted_score,
                'confidence': confidence,
                'temperature_curve': json.dumps(temperature_curve),
                'color_probability': json.dumps(color_probability),
                'feature_importance': json.dumps(feature_importance),
                'prediction_reason': prediction_reason
            }
            
        except Exception as e:
            print(f"批次预测失败: {str(e)}")
            return self._default_prediction(batch_data)
    
    def _calculate_confidence(self, features: np.ndarray, predicted_score: float) -> float:
        """计算预测置信度"""
        # 基于特征质量和预测分数的置信度计算
        base_confidence = 0.7
        
        # 特征完整性检查
        feature_completeness = np.sum(features != 0) / len(features[0])
        completeness_bonus = feature_completeness * 0.2
        
        # 预测分数合理性检查
        score_reasonableness = 1.0 - abs(predicted_score - 80.0) / 80.0
        reasonableness_bonus = max(0, score_reasonableness) * 0.1
        
        confidence = base_confidence + completeness_bonus + reasonableness_bonus
        return min(0.95, max(0.5, confidence))
    
    def _generate_temperature_curve(self, batch_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成预测的温度曲线"""
        curve = []
        base_temp = 20.0
        target_temp = 1200.0
        
        for hour in range(24):
            if hour < 2:
                # 升温阶段
                temperature = base_temp + (target_temp - base_temp) * (hour / 2) * 0.3
            elif hour < 8:
                # 保温阶段
                temperature = base_temp + (target_temp - base_temp) * 0.3 + (hour - 2) * 50
            else:
                # 高温阶段
                temperature = base_temp + (target_temp - base_temp) * 0.3 + 300 + (hour - 8) * 30
            
            # 添加一些随机波动
            temperature += np.random.normal(0, 10)
            temperature = max(20, min(1300, temperature))
            
            curve.append({
                'hour': hour,
                'temperature': round(temperature, 1),
                'phase': self._get_temperature_phase(hour)
            })
        
        return curve
    
    def _get_temperature_phase(self, hour: int) -> str:
        """获取温度阶段"""
        if hour < 2:
            return '升温'
        elif hour < 8:
            return '保温'
        else:
            return '高温'
    
    def _generate_color_probability(self, predicted_score: float) -> Dict[str, float]:
        """生成成色概率分布"""
        # 基于预测分数生成成色概率
        if predicted_score >= 90:
            return {
                '青绿色': 0.4,
                '天青色': 0.3,
                '粉青色': 0.2,
                '梅子青': 0.1
            }
        elif predicted_score >= 80:
            return {
                '青绿色': 0.3,
                '天青色': 0.35,
                '粉青色': 0.25,
                '梅子青': 0.1
            }
        elif predicted_score >= 70:
            return {
                '青绿色': 0.2,
                '天青色': 0.3,
                '粉青色': 0.3,
                '梅子青': 0.2
            }
        else:
            return {
                '青绿色': 0.1,
                '天青色': 0.2,
                '粉青色': 0.3,
                '梅子青': 0.4
            }
    
    def _generate_feature_importance(self, features: np.ndarray) -> Dict[str, float]:
        """生成特征重要性"""
        # 模拟特征重要性（实际应该从模型中获取）
        return {
            '胎土配方': 0.35,
            '匣钵厚度': 0.25,
            '木炭用量': 0.20,
            '窑位位置': 0.15,
            '烧制时间': 0.05
        }
    
    def _generate_prediction_reason(self, batch_data: Dict[str, Any], 
                                  predicted_score: float, 
                                  feature_importance: Dict[str, float]) -> str:
        """生成预测原因说明"""
        reasons = []
        
        # 胎土配方分析
        clay_ratio = batch_data.get('clay_ratio', {})
        if isinstance(clay_ratio, str):
            clay_ratio = json.loads(clay_ratio)
        
        if clay_ratio.get('高岭土', 0.5) > 0.5:
            reasons.append("胎土配方中高岭土比例较高，有利于成色")
        else:
            reasons.append("胎土配方需要优化，建议增加高岭土比例")
        
        # 匣钵厚度分析
        thickness = batch_data.get('sagger_thickness', 3.0)
        if 2.5 <= thickness <= 3.5:
            reasons.append("匣钵厚度适中，有利于均匀受热")
        else:
            reasons.append("匣钵厚度需要调整，建议控制在2.5-3.5mm")
        
        # 木炭用量分析
        charcoal = batch_data.get('charcoal_amount', 100.0)
        if 80 <= charcoal <= 120:
            reasons.append("木炭用量合理，能够提供充足的热量")
        else:
            reasons.append("木炭用量需要调整，建议控制在80-120kg")
        
        # 综合评分
        if predicted_score >= 85:
            reasons.append("综合评估：烧制条件良好，预计成色优秀")
        elif predicted_score >= 75:
            reasons.append("综合评估：烧制条件一般，预计成色良好")
        else:
            reasons.append("综合评估：烧制条件需要改进，建议调整参数")
        
        return "；".join(reasons)
    
    def _default_prediction(self, batch_data: Dict[str, Any]) -> Dict[str, Any]:
        """默认预测结果（当模型不可用时）"""
        return {
            'input_features': {
                'clay_ratio': batch_data.get('clay_ratio'),
                'sagger_thickness': batch_data.get('sagger_thickness'),
                'charcoal_amount': batch_data.get('charcoal_amount'),
                'kiln_position': batch_data.get('kiln_position')
            },
            'model_version': 'rule_based',
            'predicted_score': 75.0,
            'confidence': 0.6,
            'temperature_curve': json.dumps([]),
            'color_probability': json.dumps({
                '青绿色': 0.3,
                '天青色': 0.3,
                '粉青色': 0.2,
                '梅子青': 0.2
            }),
            'feature_importance': json.dumps({
                '胎土配方': 0.3,
                '匣钵厚度': 0.3,
                '木炭用量': 0.2,
                '窑位位置': 0.2
            }),
            'prediction_reason': '使用规则预测，建议训练机器学习模型以提高准确性'
        }
