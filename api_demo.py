"""
Live2D Desktop API 演示脚本
展示如何通过HTTP接口控制Live2D模型
"""
import requests
import json
import time

BASE_URL = "http://localhost:6000"

def test_api():
    """测试所有API接口"""
    print("=" * 60)
    print("Live2D Desktop API 功能演示")
    print("=" * 60)
    
    # 1. 测试API基础信息
    print("1. 获取API信息...")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ API名称: {data.get('name')}")
            print(f"   ✓ 版本: {data.get('version')}")
            print(f"   ✓ 状态: {data.get('status')}")
        else:
            print(f"   ✗ 错误: {response.status_code}")
    except Exception as e:
        print(f"   ✗ 连接失败: {e}")
        return
    
    # # 2. 获取可用模型
    # print("\n2. 获取可用模型...")
    # try:
    #     response = requests.get(f"{BASE_URL}/models")
    #     if response.status_code == 200:
    #         data = response.json()
    #         print(f"   ✓ 找到 {data.get('count', 0)} 个模型:")
    #         for model in data.get('models', []):
    #             print(f"     - {model.get('name')}")
    #     else:
    #         print(f"   ✗ 错误: {response.status_code}")
    # except Exception as e:
    #     print(f"   ✗ 请求失败: {e}")
    
    # # 3. 加载模型
    # print("\n3. 加载模型 (illue)...")
    # try:
    #     payload = {"model_name": "illue"}
    #     response = requests.post(f"{BASE_URL}/load_model", json=payload)
    #     if response.status_code == 200:
    #         data = response.json()
    #         print(f"   ✓ 模型加载{'成功' if data.get('success') else '失败'}")
    #     else:
    #         print(f"   ✗ 错误: {response.status_code}")
    # except Exception as e:
    #     print(f"   ✗ 请求失败: {e}")
    
    # # 4. 设置单个参数
    # print("\n4. 设置眼球参数...")
    # try:
    #     payload = {"name": "ParamEyeBallX", "value": 0.5}
    #     response = requests.post(f"{BASE_URL}/model/parameter", json=payload)
    #     if response.status_code == 200:
    #         data = response.json()
    #         print(f"   ✓ 参数设置{'成功' if data.get('success') else '失败'}")
    #     else:
    #         print(f"   ✗ 错误: {response.status_code}")
    # except Exception as e:
    #     print(f"   ✗ 请求失败: {e}")
    
    # # 5. 批量设置参数
    # print("\n5. 批量设置参数...")
    # try:
    #     payload = {
    #         "parameters": {
    #             "ParamAngleX": 10,
    #             "ParamAngleY": -5,
    #             "ParamEyeLOpen": 0.8,
    #             "ParamEyeROpen": 0.8
    #         }
    #     }
    #     response = requests.post(f"{BASE_URL}/model/parameters", json=payload)
    #     if response.status_code == 200:
    #         data = response.json()
    #         print(f"   ✓ 设置了 {data.get('parameters_set', 0)} 个参数")
    #     else:
    #         print(f"   ✗ 错误: {response.status_code}")
    # except Exception as e:
    #     print(f"   ✗ 请求失败: {e}")
    
    # # 6. 播放表情
    # print("\n6. 播放表情...")
    # try:
    #     payload = {"expression": "erji"}
    #     response = requests.post(f"{BASE_URL}/model/expression", json=payload)
    #     if response.status_code == 200:
    #         data = response.json()
    #         print(f"   ✓ 表情播放{'成功' if data.get('success') else '失败'}")
    #     else:
    #         print(f"   ✗ 错误: {response.status_code}")
    # except Exception as e:
    #     print(f"   ✗ 请求失败: {e}")

    # 6. 播放表情
    print("\n6. 播放动作...")
    try:
        print("基础权重动作播放")
        payload = {"motion": "idle","no":2,"priority":2}
        response = requests.post(f"{BASE_URL}/model/motion", json=payload)
        # time.sleep(2)
        # payload = {"motion": "idle","no":3,"priority":2}
        # response = requests.post(f"{BASE_URL}/model/motion", json=payload)
        time.sleep(1)
        print("更高权重动作播放")
        payload = {"motion": "idle","no":1,"priority":3}
        response = requests.post(f"{BASE_URL}/model/motion", json=payload)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ 表情播放{'成功' if data.get('success') else '失败'}")
        else:
            print(f"   ✗ 错误: {response.status_code}")
    except Exception as e:
        print(f"   ✗ 请求失败: {e}")
    
    # # 7. 控制嘴部开合
    # print("\n7. 控制嘴部开合...")
    # try:
    #     # 张开嘴巴
    #     payload = {"open": 0.8}
    #     response = requests.post(f"{BASE_URL}/model/mouth", json=payload)
    #     if response.status_code == 200:
    #         print("   ✓ 嘴巴张开")
        
    #     time.sleep(1)
        
    #     # 闭上嘴巴
    #     payload = {"open": 0.0}
    #     response = requests.post(f"{BASE_URL}/model/mouth", json=payload)
    #     if response.status_code == 200:
    #         print("   ✓ 嘴巴闭合")
            
    # except Exception as e:
    #     print(f"   ✗ 请求失败: {e}")
    
    # # 8. 获取模型信息
    # print("\n8. 获取当前模型信息...")
    # try:
    #     response = requests.get(f"{BASE_URL}/model/info")
    #     if response.status_code == 200:
    #         data = response.json()
    #         print(f"   ✓ 当前模型: {data.get('current_model', 'None')}")
    #         print(f"   ✓ 参数数量: {len(data.get('parameters', {}))}")
    #     else:
    #         print(f"   ✗ 错误: {response.status_code}")
    # except Exception as e:
    #     print(f"   ✗ 请求失败: {e}")
    
    print("\n" + "=" * 60)
    print("API演示完成！")
    print("你可以通过这些接口控制Live2D模型的各种参数和动画。")
    print("=" * 60)

if __name__ == "__main__":
    test_api()