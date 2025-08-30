"""
Live2D Desktop API 配置文件
"""
import os
import socket

class Config:
    # 窗口配置
    WINDOW_WIDTH = 800
    WINDOW_HEIGHT = 1200
    WINDOW_TITLE = "Live2D Desktop Renderer"
    
    # 渲染配置
    FPS = 60
    BACKGROUND_COLOR = (0.0, 0.0, 0.0, 0.0)  # 透明背景
    
    # API配置
    API_HOST = "127.0.0.1"
    API_PORT = None  # 自动选择可用端口
    API_DEBUG = True
    
    # 模型配置
    MODELS_DIR = os.path.join(os.path.dirname(__file__), "models")
    DEFAULT_MODEL = None
    
    # 动画配置
    ANIMATION_SMOOTHING = 0.1
    PARAMETER_SMOOTHING = 0.2
    
    # OBS 兼容模式配置
    OBS_COMPATIBLE_MODE = False  # 设置为 True 可让 OBS 捕获窗口
    OBS_MODE_OPACITY = 1.0       # OBS 模式下的不透明度
    OBS_MODE_SHOW_IN_TASKBAR = True  # OBS 模式下是否在任务栏显示
    
    # 鼠标穿透配置
    CLICK_THROUGH_ENABLED = False   # 是否启用鼠标穿透
    MODEL_HIT_THRESHOLD = 0.1      # 模型点击检测阈值（透明度）
    
    @staticmethod
    def find_available_port(start_port=6000, max_attempts=100):
        """查找可用的端口"""
        for port in range(start_port, start_port + max_attempts):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                try:
                    sock.bind(('localhost', port))
                    return port
                except OSError:
                    continue
        raise RuntimeError(f"无法找到可用端口 (尝试范围: {start_port}-{start_port + max_attempts})")

# 全局配置实例
config = Config()

# 自动设置API端口
if config.API_PORT is None:
    config.API_PORT = config.find_available_port()