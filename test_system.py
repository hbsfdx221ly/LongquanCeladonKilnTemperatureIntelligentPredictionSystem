#!/usr/bin/env python3
"""
系统测试脚本
"""

import requests
import json
import time
import sys
import os

# 添加backend目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def test_api_connection():
    """测试API连接"""
    print("测试API连接...")
    try:
        response = requests.get('http://localhost:5000/health', timeout=5)
        if response.status_code == 200:
            print("✓ API连接正常")
            return True
        else:
            print(f"✗ API连接失败: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"✗ API连接失败: {e}")
        return False

def test_batch_creation():
    """测试批次创建"""
    print("测试批次创建...")
    try:
        batch_data = {
            "batch_name": "测试批次_001",
            "clay_ratio": {
                "高岭土": 0.5,
                "石英": 0.25,
                "长石": 0.15,
                "其他": 0.1
            },
            "sagger_thickness": 3.0,
            "charcoal_amount": 100,
            "kiln_position": "窑位_A"
        }
        
        response = requests.post('http://localhost:5000/api/batches', 
                               json=batch_data, timeout=10)
        
        if response.status_code == 201:
            result = response.json()
            print(f"✓ 批次创建成功: ID {result['data']['id']}")
            return result['data']['id']
        else:
            print(f"✗ 批次创建失败: {response.status_code}")
            print(response.text)
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"✗ 批次创建失败: {e}")
        return None

def test_prediction(batch_id):
    """测试预测功能"""
    print("测试预测功能...")
    try:
        response = requests.post('http://localhost:5000/api/predictions/predict',
                               json={"batch_id": batch_id}, timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            score = result['data']['predicted_score']
            confidence = result['data']['confidence']
            print(f"✓ 预测成功: 评分 {score:.1f}, 置信度 {confidence:.1%}")
            return True
        else:
            print(f"✗ 预测失败: {response.status_code}")
            print(response.text)
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"✗ 预测失败: {e}")
        return False

def test_sensor_data(batch_id):
    """测试传感器数据"""
    print("测试传感器数据...")
    try:
        sensor_data = {
            "batch_id": batch_id,
            "temperature": 1200.5,
            "position_x": 0.0,
            "position_y": 2.0,
            "position_z": 1.0,
            "oxygen_level": 18.2,
            "co_level": 45.0,
            "co2_level": 2.1,
            "pressure": 101300.0,
            "humidity": 45.0
        }
        
        response = requests.post('http://localhost:5000/api/sensor-data',
                               json=sensor_data, timeout=10)
        
        if response.status_code == 201:
            print("✓ 传感器数据添加成功")
            return True
        else:
            print(f"✗ 传感器数据添加失败: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"✗ 传感器数据添加失败: {e}")
        return False

def test_websocket():
    """测试WebSocket连接"""
    print("测试WebSocket连接...")
    try:
        import socketio
        
        sio = socketio.Client()
        
        @sio.event
        def connect():
            print("✓ WebSocket连接成功")
            sio.disconnect()
        
        @sio.event
        def disconnect():
            print("✓ WebSocket断开成功")
        
        sio.connect('http://localhost:5000')
        time.sleep(1)
        return True
        
    except ImportError:
        print("⚠ WebSocket测试跳过 (缺少python-socketio)")
        return True
    except Exception as e:
        print(f"✗ WebSocket连接失败: {e}")
        return False

def main():
    """主测试函数"""
    print("龙泉青瓷窑温智能预测系统 - 系统测试")
    print("=" * 50)
    
    # 等待服务启动
    print("等待服务启动...")
    time.sleep(3)
    
    # 运行测试
    tests = [
        ("API连接", test_api_connection),
        ("批次创建", lambda: test_batch_creation()),
        ("WebSocket连接", test_websocket)
    ]
    
    batch_id = None
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        try:
            result = test_func()
            if result:
                passed += 1
                if test_name == "批次创建":
                    batch_id = result
        except Exception as e:
            print(f"✗ {test_name}测试异常: {e}")
    
    # 如果有批次ID，继续测试
    if batch_id:
        additional_tests = [
            ("预测功能", lambda: test_prediction(batch_id)),
            ("传感器数据", lambda: test_sensor_data(batch_id))
        ]
        
        for test_name, test_func in additional_tests:
            print(f"\n{test_name}:")
            try:
                if test_func():
                    passed += 1
                total += 1
            except Exception as e:
                print(f"✗ {test_name}测试异常: {e}")
                total += 1
    
    # 输出测试结果
    print("\n" + "=" * 50)
    print(f"测试完成: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！系统运行正常")
        return 0
    else:
        print("❌ 部分测试失败，请检查系统配置")
        return 1

if __name__ == '__main__':
    sys.exit(main())
