#!/usr/bin/env python3
"""
Live2D Desktop API 环境检查脚本
检查所有依赖是否正确安装并给出建议
"""
import sys
import importlib
import platform
import subprocess

def check_python_version():
    """检查Python版本"""
    print("=" * 50)
    print("Python 环境检查")
    print("=" * 50)
    
    version_info = sys.version_info
    version_str = f"{version_info.major}.{version_info.minor}.{version_info.micro}"
    
    print(f"Python 版本: {version_str}")
    print(f"完整版本: {sys.version}")
    print(f"执行路径: {sys.executable}")
    
    if version_info < (3, 8):
        print("❌ Python 版本过低，需要 3.8 或更高版本")
        return False
    else:
        print("✅ Python 版本符合要求")
        return True

def check_package(package_name, import_name=None, required=True):
    """检查单个包是否安装"""
    if import_name is None:
        import_name = package_name
    
    try:
        module = importlib.import_module(import_name)
        version = getattr(module, '__version__', '未知版本')
        status = "✅"
        message = f"{package_name}: {version}"
    except ImportError as e:
        status = "❌" if required else "⚠️"
        message = f"{package_name}: 未安装 ({e})"
        return False, message
    
    return True, f"{status} {message}"

def check_all_dependencies():
    """检查所有依赖"""
    print("\n" + "=" * 50)
    print("依赖包检查")
    print("=" * 50)
    
    # 核心依赖
    dependencies = [
        # GUI 和渲染
        ("PyQt5", "PyQt5.QtCore", True),
        ("PyOpenGL", "OpenGL.GL", True),
        ("numpy", "numpy", True),
        
        # Live2D 引擎
        ("live2d-py", "live2d.v3", True),
        
        # Web API
        ("Flask", "flask", True),
        ("Flask-Cors", "flask_cors", True),
        ("Werkzeug", "werkzeug", True),
        
        # 网络
        ("requests", "requests", True),
    ]
    
    # 可选依赖
    optional_dependencies = [
        ("PyOpenGL-accelerate", "OpenGL_accelerate", False),
        ("psutil", "psutil", False),
    ]
    
    all_good = True
    
    print("核心依赖:")
    for pkg_name, import_name, required in dependencies:
        success, message = check_package(pkg_name, import_name, required)
        print(f"  {message}")
        if not success and required:
            all_good = False
    
    print("\n可选依赖:")
    for pkg_name, import_name, required in optional_dependencies:
        success, message = check_package(pkg_name, import_name, required)
        print(f"  {message}")
    
    return all_good

def check_system_info():
    """检查系统信息"""
    print("\n" + "=" * 50)
    print("系统环境信息")
    print("=" * 50)
    
    print(f"操作系统: {platform.system()} {platform.release()}")
    print(f"架构: {platform.machine()}")
    print(f"处理器: {platform.processor()}")
    
    # Windows 特定检查
    if platform.system() == "Windows":
        print("Windows 特定功能:")
        try:
            import ctypes
            print("  ✅ ctypes 可用 (鼠标穿透功能)")
        except ImportError:
            print("  ❌ ctypes 不可用")

def check_models_directory():
    """检查模型目录"""
    print("\n" + "=" * 50)
    print("模型目录检查")
    print("=" * 50)
    
    models_dir = "models"
    if not os.path.exists(models_dir):
        print(f"❌ {models_dir}/ 目录不存在")
        print("   建议: 创建 models/ 目录并放入 Live2D 模型文件")
        return False
    
    import os
    models = [d for d in os.listdir(models_dir) 
             if os.path.isdir(os.path.join(models_dir, d))]
    
    if not models:
        print(f"⚠️  {models_dir}/ 目录为空")
        print("   建议: 放入 Live2D 模型文件")
        return False
    
    print(f"✅ 找到 {len(models)} 个模型目录:")
    for model in models:
        print(f"   - {model}")
    
    return True

def check_configuration():
    """检查配置文件"""
    print("\n" + "=" * 50)
    print("配置文件检查")
    print("=" * 50)
    
    try:
        from config import config
        print("✅ 配置文件加载成功")
        print(f"   窗口大小: {config.WINDOW_WIDTH}x{config.WINDOW_HEIGHT}")
        print(f"   API端口: {config.API_PORT}")
        print(f"   模型目录: {config.MODELS_DIR}")
        print(f"   OBS兼容模式: {config.OBS_COMPATIBLE_MODE}")
        print(f"   鼠标穿透: {config.CLICK_THROUGH_ENABLED}")
        return True
    except Exception as e:
        print(f"❌ 配置文件加载失败: {e}")
        return False

def main():
    """主检查流程"""
    print("Live2D Desktop API 环境检查工具")
    print(f"检查时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 执行所有检查
    checks = [
        ("Python版本", check_python_version),
        ("系统环境", check_system_info),
        ("依赖包", check_all_dependencies),
        ("配置文件", check_configuration),
        ("模型目录", check_models_directory),
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ {name}检查失败: {e}")
            results.append((name, False))
    
    # 总结报告
    print("\n" + "=" * 50)
    print("检查结果总结")
    print("=" * 50)
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{name}: {status}")
    
    all_passed = all(result for _, result in results)
    
    if all_passed:
        print("\n🎉 所有检查通过！您可以正常使用 Live2D Desktop API")
        print("\n推荐的启动命令:")
        print("  python full_main.py          # 完整模式")
        print("  python simple_live2d_renderer.py  # 仅渲染器")
    else:
        print("\n⚠️  发现问题，请根据上述提示解决后重新检查")
        print("\n常见解决方案:")
        print("  1. 重新运行安装脚本: install.bat (Windows) 或 ./install.sh (Linux/macOS)")
        print("  2. 手动安装依赖: pip install -r requirements.txt")
        print("  3. 检查 models/ 目录是否包含 Live2D 模型文件")

if __name__ == "__main__":
    import os
    import time
    
    # 确保在正确的目录中运行
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    main()