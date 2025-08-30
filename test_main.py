"""
测试版主程序 - 用于调试
"""
import sys
import os
import threading
import time
from config import config

def test_config():
    """测试配置"""
    print("=" * 50)
    print("配置测试")
    print("=" * 50)
    print(f"窗口大小: {config.WINDOW_WIDTH}x{config.WINDOW_HEIGHT}")
    print(f"API地址: http://{config.API_HOST}:{config.API_PORT}")
    print(f"模型目录: {config.MODELS_DIR}")
    print(f"模型目录存在: {os.path.exists(config.MODELS_DIR)}")
    if os.path.exists(config.MODELS_DIR):
        models = [d for d in os.listdir(config.MODELS_DIR) if os.path.isdir(os.path.join(config.MODELS_DIR, d))]
        print(f"发现模型: {models}")
    print()

def test_api_only():
    """仅测试API服务"""
    print("启动API服务...")
    
    # 导入API模块
    from simple_flask_api import app, set_renderer
    
    # 模拟渲染器
    class MockRenderer:
        def __init__(self):
            self.current_model = None
            self.parameters = {}
            
        def load_model(self, model_path):
            print(f"[Mock] 加载模型: {model_path}")
            self.current_model = model_path
            return True
            
        def set_parameter(self, param_name, value):
            print(f"[Mock] 设置参数: {param_name} = {value}")
            self.parameters[param_name] = value
            
        def play_expression(self, expression_name):
            print(f"[Mock] 播放表情: {expression_name}")
    
    # 设置模拟渲染器
    renderer = MockRenderer()
    set_renderer(renderer)
    
    print(f"API服务启动在: http://{config.API_HOST}:{config.API_PORT}")
    print("按 Ctrl+C 退出服务")
    
    try:
        app.run(
            host=config.API_HOST,
            port=config.API_PORT,
            debug=False,
            use_reloader=False,
            threaded=True
        )
    except KeyboardInterrupt:
        print("\\nAPI服务已停止")

def main():
    """主程序"""
    test_config()
    
    print("选择测试模式:")
    print("1. 仅测试API服务")
    print("2. 完整测试（GUI + API）")
    
    # 默认启动API测试
    print("启动API服务测试...")
    test_api_only()

if __name__ == "__main__":
    main()