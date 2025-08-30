#!/bin/bash

echo "========================================"
echo "Live2D Desktop API 自动安装脚本"
echo "========================================"
echo

# 检查 Python 版本
if ! command -v python3 &> /dev/null; then
    echo "[错误] 未找到 Python3，请先安装 Python 3.8 或更高版本"
    echo "Ubuntu/Debian: sudo apt install python3 python3-pip python3-venv"
    echo "CentOS/RHEL: sudo yum install python3 python3-pip"
    echo "macOS: brew install python3"
    exit 1
fi

echo "[信息] 检测到的 Python 版本:"
python3 --version

echo
echo "[步骤 1/4] 创建虚拟环境..."
if [ -d "venv" ]; then
    echo "[信息] 虚拟环境已存在，跳过创建"
else
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "[错误] 虚拟环境创建失败"
        exit 1
    fi
    echo "[成功] 虚拟环境创建完成"
fi

echo
echo "[步骤 2/4] 激活虚拟环境..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "[错误] 虚拟环境激活失败"
    exit 1
fi

echo
echo "[步骤 3/4] 升级 pip..."
python -m pip install --upgrade pip

echo
echo "[步骤 4/4] 安装项目依赖..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "[错误] 依赖安装失败"
    echo "[建议] 请检查网络连接或尝试使用国内镜像源:"
    echo "         pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/"
    exit 1
fi

echo
echo "========================================"
echo "安装完成！"
echo "========================================"
echo
echo "下一步:"
echo "1. 确保 models/ 目录中有 Live2D 模型文件"
echo "2. 运行: python full_main.py 启动完整服务"
echo "3. 运行: python simple_live2d_renderer.py 仅启动渲染器"
echo "4. 运行: python api_demo.py 测试 API 功能"
echo
echo "项目目录结构:"
echo "  models/           - Live2D模型文件目录"
echo "  config.py         - 配置文件"
echo "  full_main.py      - 完整启动脚本（渲染器+API）"
echo "  simple_live2d_renderer.py - 纯渲染器"
echo "  simple_flask_api.py - API服务"
echo "  api_demo.py       - API测试演示"
echo

# Linux/macOS 特定说明
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "Linux 特定说明:"
    echo "- 如果遇到 PyQt5 安装问题，请安装系统依赖:"
    echo "  sudo apt install python3-pyqt5 python3-pyqt5-dev"
    echo "  sudo apt install libgl1-mesa-dev libglu1-mesa-dev"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    echo "macOS 特定说明:"
    echo "- 如果遇到 PyQt5 安装问题，请使用 Homebrew:"
    echo "  brew install pyqt5"
fi

echo
echo "激活虚拟环境命令:"
echo "  source venv/bin/activate  (Linux/macOS)"
echo "  venv\\Scripts\\activate.bat  (Windows)"