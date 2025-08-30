"""
Live2D Desktop API
一个功能完整的桌面 Live2D 渲染器和 HTTP API 服务

主要模块:
- simple_live2d_renderer: Live2D 桌面渲染器
- simple_flask_api: HTTP API 服务  
- real_live2d_controller: Live2D 控制器
- config: 配置管理
"""

__version__ = "1.0.0"
__author__ = "Live2D Desktop API Team"
__description__ = "桌面Live2D渲染器和HTTP API服务"

# 版本信息
VERSION_INFO = {
    "version": __version__,
    "build_date": "2024-12-19",
    "python_requires": ">=3.8",
    "features": [
        "Live2D 桌面渲染",
        "HTTP API 服务", 
        "OBS 直播兼容",
        "鼠标穿透功能",
        "边框调整大小",
        "系统托盘集成"
    ]
}

# 导出主要类和函数
try:
    from .simple_live2d_renderer import Live2DRenderer
    from .simple_flask_api import app as flask_app, set_renderer
    from .real_live2d_controller import real_live2d_controller
    from .config import config
    
    __all__ = [
        'Live2DRenderer',
        'flask_app', 
        'set_renderer',
        'real_live2d_controller',
        'config',
        'VERSION_INFO'
    ]
    
except ImportError:
    # 在某些情况下导入可能失败，这是正常的
    __all__ = ['VERSION_INFO']

def get_version():
    """获取版本信息"""
    return __version__

def get_version_info():
    """获取详细版本信息"""
    return VERSION_INFO