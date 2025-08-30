"""
完整的Live2D桌面API程序
集成桌面渲染器和HTTP API服务
"""
import sys
import os
import threading
from PyQt5.QtWidgets import QApplication
from simple_live2d_renderer import Live2DRenderer
from simple_flask_api import set_renderer, start_api_server_thread
from config import config

def main(live2d_model_name):
    """主程序入口"""
    print("=" * 60)
    print("Live2D Desktop API - 完整版")
    print("桌面渲染器 + HTTP API 服务")
    print("=" * 60)
    
    # 创建Qt应用
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)  # 关闭最后窗口时不退出程序
    
    # 创建Live2D桌面渲染器
    print("正在初始化Live2D桌面渲染器...")
    renderer = Live2DRenderer(live2d_model_name)
    
    # 设置渲染器到API服务
    set_renderer(renderer)
    
    # 启动API服务器（在后台线程中）
    print("正在启动API服务器...")
    api_thread = start_api_server_thread(live2d_model_name)
    
    # 显示渲染器窗口
    renderer.show()
    
    # 输出启动信息
    print()
    print("✓ Live2D桌面渲染器已启动")
    print(f"  - 窗口大小: {config.WINDOW_WIDTH}x{config.WINDOW_HEIGHT}")
    print(f"  - 透明背景，置顶显示")
    print(f"  - 支持鼠标拖拽移动")
    print()
    print("✓ HTTP API服务已启动")
    print(f"  - 服务地址: http://{config.API_HOST}:{config.API_PORT}")
    print(f"  - 支持跨域访问（CORS）")
    print(f"  - 完整的RESTful API")
    print()
    print("✓ 模型管理")
    print(f"  - 模型目录: {config.MODELS_DIR}")
    
    # 检查模型
    if os.path.exists(config.MODELS_DIR):
        models = [d for d in os.listdir(config.MODELS_DIR) 
                 if os.path.isdir(os.path.join(config.MODELS_DIR, d))]
        if models:
            print(f"  - 发现 {len(models)} 个模型: {', '.join(models)}")
            print(f"  - 已自动加载: {models[0]}")
        else:
            print("  - 警告: 没有发现任何模型文件")
    else:
        print("  - 警告: 模型目录不存在")
    
    print()
    print("🎮 使用说明:")
    print("  • 桌面窗口: 可拖拽移动，右键托盘图标控制显示")
    print("  • API控制: 通过HTTP接口远程控制Live2D模型")
    print("  • 参数设置: 实时调整眼球、嘴部、头部等参数")
    print("  • 表情播放: 支持播放模型内置表情动画")
    print()
    print("🌐 API测试:")
    print(f"  curl http://localhost:{config.API_PORT}/")
    print(f"  curl http://localhost:{config.API_PORT}/models")
    print()
    print("💡 提示: 按 Ctrl+C 退出程序")
    print("=" * 60)
    print()
    
    # 运行Qt事件循环
    try:
        sys.exit(app.exec_())
    except KeyboardInterrupt:
        print("\\n程序被用户中断")
        app.quit()

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        live2d_model_name = sys.argv[1]
    else:
        live2d_model_name = None
    print(f"模型：{live2d_model_name}")
    main(live2d_model_name)