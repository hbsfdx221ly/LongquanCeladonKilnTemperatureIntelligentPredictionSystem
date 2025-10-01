"""
模型训练脚本
"""

from ml.trainer import PorcelainTrainer
import os

def main():
    """训练模型"""
    print("龙泉青瓷窑温智能预测系统 - 模型训练")
    print("=" * 50)
    
    # 创建训练器
    trainer = PorcelainTrainer()
    
    # 执行完整训练流程
    metrics = trainer.train_full_pipeline()
    
    print("\n训练完成!")
    print("模型性能指标:")
    for metric, value in metrics.items():
        print(f"  {metric}: {value:.4f}")
    
    # 检查模型文件
    model_path = 'models/lightgbm_model.pkl'
    if os.path.exists(model_path):
        print(f"\n模型文件已保存: {model_path}")
    else:
        print("\n警告: 模型文件保存失败")

if __name__ == '__main__':
    main()
