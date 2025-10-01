"""
龙泉青瓷模型训练器
基于LightGBM的模型训练和评估
"""

import pandas as pd
import numpy as np
import lightgbm as lgb
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib
import json
import os
from datetime import datetime
from typing import Dict, List, Any, Tuple
import matplotlib.pyplot as plt
import seaborn as sns

class PorcelainTrainer:
    """龙泉青瓷模型训练器"""
    
    def __init__(self, data_path: str = 'data/training_data.csv'):
        self.data_path = data_path
        self.model = None
        self.feature_names = None
        self.training_data = None
        self.test_data = None
        
    def load_data(self) -> pd.DataFrame:
        """加载训练数据"""
        try:
            if os.path.exists(self.data_path):
                self.training_data = pd.read_csv(self.data_path)
                print(f"数据加载成功: {len(self.training_data)} 条记录")
                return self.training_data
            else:
                print(f"数据文件不存在: {self.data_path}")
                return self._generate_sample_data()
        except Exception as e:
            print(f"数据加载失败: {str(e)}")
            return self._generate_sample_data()
    
    def _generate_sample_data(self) -> pd.DataFrame:
        """生成示例训练数据"""
        print("生成示例训练数据...")
        
        np.random.seed(42)
        n_samples = 120
        
        data = []
        for i in range(n_samples):
            # 胎土配方（总和为1）
            clay_ratio = np.random.dirichlet([4, 3, 2, 1])
            
            # 烧制参数
            sagger_thickness = np.random.normal(3.0, 0.5)
            charcoal_amount = np.random.normal(100, 20)
            
            # 窑位（编码为数值）
            kiln_position = np.random.choice(['A', 'B', 'C', 'D', 'E'])
            position_encoded = [1 if pos == kiln_position else 0 for pos in ['A', 'B', 'C', 'D', 'E']]
            
            # 时间特征
            start_hour = np.random.randint(6, 18)
            start_month = np.random.randint(3, 9)  # 3-8月
            start_weekday = np.random.randint(0, 7)
            
            # 环境参数
            avg_temperature = np.random.normal(1200, 100)
            avg_oxygen = np.random.normal(18, 2)
            avg_pressure = np.random.normal(101500, 500)
            
            # 生成目标变量（成色评分）
            base_score = 70
            
            # 胎土配方影响
            clay_score = (clay_ratio[0] * 0.4 + clay_ratio[1] * 0.3 + 
                         clay_ratio[2] * 0.2 + clay_ratio[3] * 0.1) * 20
            
            # 匣钵厚度影响
            thickness_score = max(0, 10 - abs(sagger_thickness - 3.0) * 2)
            
            # 木炭用量影响
            charcoal_score = max(0, 10 - abs(charcoal_amount - 100.0) / 10)
            
            # 窑位影响
            position_scores = {'A': 5, 'B': 4, 'C': 3, 'D': 2, 'E': 1}
            position_score = position_scores[kiln_position]
            
            # 温度影响
            temp_score = max(0, 10 - abs(avg_temperature - 1200) / 50)
            
            # 氧气影响
            oxygen_score = max(0, 5 - abs(avg_oxygen - 18) * 0.5)
            
            # 综合评分
            total_score = (base_score + clay_score + thickness_score + 
                          charcoal_score + position_score + temp_score + oxygen_score)
            
            # 添加随机噪声
            total_score += np.random.normal(0, 5)
            total_score = max(0, min(100, total_score))
            
            # 构建特征向量
            features = [
                clay_ratio[0], clay_ratio[1], clay_ratio[2], clay_ratio[3],  # 胎土配方
                sagger_thickness, charcoal_amount,  # 烧制参数
                *position_encoded,  # 窑位编码
                start_hour, start_month, start_weekday,  # 时间特征
                avg_temperature, avg_oxygen, avg_pressure  # 环境参数
            ]
            
            data.append(features + [total_score])
        
        # 创建DataFrame
        feature_names = [
            '高岭土比例', '石英比例', '长石比例', '其他比例',
            '匣钵厚度', '木炭用量',
            '窑位_A', '窑位_B', '窑位_C', '窑位_D', '窑位_E',
            '开始小时', '开始月份', '开始星期',
            '平均温度', '平均氧气', '平均压力'
        ]
        
        df = pd.DataFrame(data, columns=feature_names + ['成色评分'])
        
        # 保存示例数据
        os.makedirs('data', exist_ok=True)
        df.to_csv(self.data_path, index=False, encoding='utf-8')
        print(f"示例数据已保存到: {self.data_path}")
        
        return df
    
    def prepare_features(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """准备特征和标签"""
        # 分离特征和标签
        feature_columns = [col for col in df.columns if col != '成色评分']
        X = df[feature_columns].values
        y = df['成色评分'].values
        
        self.feature_names = feature_columns
        
        return X, y
    
    def train_model(self, X: np.ndarray, y: np.ndarray) -> lgb.LGBMRegressor:
        """训练LightGBM模型"""
        print("开始训练LightGBM模型...")
        
        # 分割训练集和测试集
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        self.test_data = (X_test, y_test)
        
        # LightGBM参数
        params = {
            'objective': 'regression',
            'metric': 'mae',
            'boosting_type': 'gbdt',
            'num_leaves': 31,
            'learning_rate': 0.05,
            'feature_fraction': 0.9,
            'bagging_fraction': 0.8,
            'bagging_freq': 5,
            'verbose': 0,
            'random_state': 42
        }
        
        # 创建训练数据集
        train_data = lgb.Dataset(X_train, label=y_train)
        
        # 训练模型
        self.model = lgb.train(
            params,
            train_data,
            num_boost_round=1000,
            valid_sets=[train_data],
            callbacks=[lgb.early_stopping(100), lgb.log_evaluation(100)]
        )
        
        print("模型训练完成")
        return self.model
    
    def evaluate_model(self, X_test: np.ndarray, y_test: np.ndarray) -> Dict[str, float]:
        """评估模型性能"""
        if self.model is None:
            raise ValueError("模型未训练")
        
        # 预测
        y_pred = self.model.predict(X_test)
        
        # 计算评估指标
        mae = mean_absolute_error(y_test, y_pred)
        mse = mean_squared_error(y_test, y_pred)
        rmse = np.sqrt(mse)
        r2 = r2_score(y_test, y_pred)
        
        # 准确率（误差在5分以内视为准确）
        accurate_predictions = np.sum(np.abs(y_test - y_pred) <= 5)
        accuracy = accurate_predictions / len(y_test)
        
        metrics = {
            'mae': mae,
            'mse': mse,
            'rmse': rmse,
            'r2': r2,
            'accuracy': accuracy
        }
        
        print("模型评估结果:")
        for metric, value in metrics.items():
            print(f"  {metric}: {value:.4f}")
        
        return metrics
    
    def get_feature_importance(self) -> Dict[str, float]:
        """获取特征重要性"""
        if self.model is None:
            raise ValueError("模型未训练")
        
        importance = self.model.feature_importance(importance_type='gain')
        feature_importance = dict(zip(self.feature_names, importance))
        
        # 按重要性排序
        sorted_importance = dict(sorted(
            feature_importance.items(), 
            key=lambda x: x[1], 
            reverse=True
        ))
        
        return sorted_importance
    
    def save_model(self, model_path: str = 'models/lightgbm_model.pkl'):
        """保存模型"""
        if self.model is None:
            raise ValueError("模型未训练")
        
        # 确保目录存在
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        
        # 保存模型和元数据
        model_data = {
            'model': self.model,
            'feature_names': self.feature_names,
            'training_time': datetime.now().isoformat(),
            'model_type': 'LightGBM'
        }
        
        joblib.dump(model_data, model_path)
        print(f"模型已保存到: {model_path}")
    
    def plot_training_results(self, X_test: np.ndarray, y_test: np.ndarray, 
                            save_path: str = 'models/training_plots.png'):
        """绘制训练结果图表"""
        if self.model is None:
            raise ValueError("模型未训练")
        
        y_pred = self.model.predict(X_test)
        
        # 创建子图
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('龙泉青瓷模型训练结果', fontsize=16)
        
        # 1. 预测vs实际散点图
        axes[0, 0].scatter(y_test, y_pred, alpha=0.6)
        axes[0, 0].plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--', lw=2)
        axes[0, 0].set_xlabel('实际评分')
        axes[0, 0].set_ylabel('预测评分')
        axes[0, 0].set_title('预测 vs 实际')
        
        # 2. 残差图
        residuals = y_test - y_pred
        axes[0, 1].scatter(y_pred, residuals, alpha=0.6)
        axes[0, 1].axhline(y=0, color='r', linestyle='--')
        axes[0, 1].set_xlabel('预测评分')
        axes[0, 1].set_ylabel('残差')
        axes[0, 1].set_title('残差图')
        
        # 3. 特征重要性
        importance = self.get_feature_importance()
        top_features = dict(list(importance.items())[:10])
        
        features = list(top_features.keys())
        values = list(top_features.values())
        
        axes[1, 0].barh(features, values)
        axes[1, 0].set_xlabel('重要性')
        axes[1, 0].set_title('特征重要性 (Top 10)')
        
        # 4. 误差分布
        axes[1, 1].hist(residuals, bins=20, alpha=0.7, edgecolor='black')
        axes[1, 1].set_xlabel('残差')
        axes[1, 1].set_ylabel('频次')
        axes[1, 1].set_title('残差分布')
        
        plt.tight_layout()
        
        # 保存图片
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"训练结果图表已保存到: {save_path}")
    
    def train_full_pipeline(self, model_path: str = 'models/lightgbm_model.pkl'):
        """完整的训练流程"""
        print("开始完整训练流程...")
        
        # 1. 加载数据
        df = self.load_data()
        
        # 2. 准备特征
        X, y = self.prepare_features(df)
        
        # 3. 训练模型
        self.train_model(X, y)
        
        # 4. 评估模型
        X_test, y_test = self.test_data
        metrics = self.evaluate_model(X_test, y_test)
        
        # 5. 保存模型
        self.save_model(model_path)
        
        # 6. 绘制结果
        self.plot_training_results(X_test, y_test)
        
        print("训练流程完成!")
        return metrics

def main():
    """主函数"""
    trainer = PorcelainTrainer()
    metrics = trainer.train_full_pipeline()
    
    print("\n最终模型性能:")
    for metric, value in metrics.items():
        print(f"  {metric}: {value:.4f}")

if __name__ == '__main__':
    main()
