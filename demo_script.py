#!/usr/bin/env python3
"""
演示脚本 - 展示系统核心功能
"""

import requests
import json
import time
import random
from datetime import datetime

def create_demo_batch():
    """创建演示批次"""
    print("创建演示批次...")
    
    batch_data = {
        "batch_name": f"龙泉青瓷演示批次_{datetime.now().strftime('%H%M%S')}",
        "clay_ratio": {
            "高岭土": 0.52,
            "石英": 0.23,
            "长石": 0.15,
            "其他": 0.10
        },
        "sagger_thickness": 3.1,
        "charcoal_amount": 105,
        "kiln_position": "窑位_B"
    }
    
    response = requests.post('http://localhost:5000/api/batches', json=batch_data)
    if response.status_code == 201:
        batch = response.json()['data']
        print(f"✓ 批次创建成功: {batch['batch_name']} (ID: {batch['id']})")
        return batch['id']
    else:
        print(f"✗ 批次创建失败: {response.text}")
        return None

def simulate_firing_process(batch_id):
    """模拟烧制过程"""
    print("模拟烧制过程...")
    
    # 开始烧制
    requests.post(f'http://localhost:5000/api/batches/{batch_id}/start')
    print("✓ 烧制开始")
    
    # 模拟传感器数据
    for hour in range(24):
        temperature = 20 + hour * 50 + random.uniform(-10, 10)
        if hour > 8:
            temperature = 1200 + (hour - 8) * 10 + random.uniform(-20, 20)
        
        sensor_data = {
            "batch_id": batch_id,
            "temperature": max(20, min(1300, temperature)),
            "position_x": random.uniform(-2, 2),
            "position_y": random.uniform(1, 5),
            "position_z": random.uniform(0, 3),
            "oxygen_level": 18.0 + random.uniform(-1, 1),
            "co_level": random.uniform(20, 80),
            "co2_level": random.uniform(1.5, 3.0),
            "pressure": 101300 + random.uniform(-500, 500),
            "humidity": random.uniform(30, 60)
        }
        
        requests.post('http://localhost:5000/api/sensor-data', json=sensor_data)
        
        if hour % 4 == 0:
            print(f"  第{hour}小时: 温度 {sensor_data['temperature']:.1f}°C")
        
        time.sleep(0.1)  # 模拟时间间隔
    
    print("✓ 烧制过程模拟完成")

def run_prediction(batch_id):
    """运行预测"""
    print("执行智能预测...")
    
    response = requests.post('http://localhost:5000/api/predictions/predict',
                           json={"batch_id": batch_id})
    
    if response.status_code == 200:
        result = response.json()['data']
        score = result['predicted_score']
        confidence = result['confidence']
        
        print(f"✓ 预测完成!")
        print(f"  预测评分: {score:.1f}分")
        print(f"  置信度: {confidence:.1%}")
        print(f"  预测原因: {result['prediction_reason']}")
        
        # 显示成色概率
        color_prob = json.loads(result['color_probability'])
        print("  成色概率分布:")
        for color, prob in color_prob.items():
            print(f"    {color}: {prob:.1%}")
        
        return result
    else:
        print(f"✗ 预测失败: {response.text}")
        return None

def show_system_status():
    """显示系统状态"""
    print("系统状态检查...")
    
    try:
        # 健康检查
        health = requests.get('http://localhost:5000/health')
        if health.status_code == 200:
            print("✓ 系统健康状态正常")
        
        # 获取批次列表
        batches = requests.get('http://localhost:5000/api/batches')
        if batches.status_code == 200:
            batch_count = len(batches.json()['data'])
            print(f"✓ 当前批次数量: {batch_count}")
        
        # 获取预测准确率
        accuracy = requests.get('http://localhost:5000/api/predictions/accuracy')
        if accuracy.status_code == 200:
            acc_data = accuracy.json()['data']
            if acc_data['total_predictions'] > 0:
                print(f"✓ 预测准确率: {acc_data['accuracy']:.1%}")
        
    except Exception as e:
        print(f"✗ 状态检查失败: {e}")

def main():
    """主演示函数"""
    print("龙泉青瓷窑温智能预测系统 - 功能演示")
    print("=" * 50)
    
    # 检查服务是否运行
    try:
        requests.get('http://localhost:5000/health', timeout=5)
    except:
        print("❌ 后端服务未运行，请先启动后端服务")
        print("运行命令: python start_backend.py")
        return
    
    # 显示系统状态
    show_system_status()
    print()
    
    # 创建演示批次
    batch_id = create_demo_batch()
    if not batch_id:
        return
    
    print()
    
    # 模拟烧制过程
    simulate_firing_process(batch_id)
    print()
    
    # 执行预测
    prediction_result = run_prediction(batch_id)
    print()
    
    # 完成烧制
    requests.post(f'http://localhost:5000/api/batches/{batch_id}/complete')
    print("✓ 烧制完成")
    
    print("\n" + "=" * 50)
    print("🎉 演示完成！")
    print("现在可以访问 http://localhost:3000 查看前端界面")
    print("或访问 http://localhost:5000 查看API文档")

if __name__ == '__main__':
    main()
