# Live2D Desktop API

一个功能完整的桌面 Live2D 渲染器和 HTTP API 服务，支持 OBS 直播捕获、鼠标穿透、边框调整大小等高级功能。

## ✨ 主要功能

### 🎭 Live2D 渲染器
- **桌面宠物模式**：透明背景，可穿透鼠标事件
- **OBS 直播模式**：不透明背景，可被 OBS 捕获
- **边框调整**：类似传统软件的边框拖拽调整大小
- **系统托盘**：最小化到托盘，右键菜单控制

### 🌐 HTTP API 服务
- **完整的 LAppModel 接口**：覆盖所有 Live2D 核心功能
- **RESTful 设计**：标准 JSON 响应格式
- **实时控制**：参数、表情、动作、颜色等
- **跨域支持**：可从网页或其他应用调用

### 🎮 交互功能
- **窗口拖拽**：点击窗口任意位置拖拽移动
- **鼠标穿透**：启用后鼠标点击穿透到桌面
- **点击检测**：支持模型部件的点击交互
- **多模式切换**：通过托盘菜单快速切换

## 🚀 快速开始

### Windows 用户

1. **自动安装**（推荐）
   ```batch
   # 双击运行或在命令行执行
   install.bat
   ```

2. **快速启动**
   ```batch
   # 双击运行或在命令行执行
   run.bat
   ```

### Linux/macOS 用户

1. **自动安装**
   ```bash
   chmod +x install.sh
   ./install.sh
   ```

2. **手动安装**
   ```bash
   # 创建虚拟环境
   python3 -m venv venv
   source venv/bin/activate  # Linux/macOS
   
   # 安装依赖
   pip install -r requirements.txt
   ```

### 环境检查

```bash
python check_env.py
```

## 📁 项目结构

```
live2d-desktop-api/
├── models/                      # Live2D 模型文件目录
│   └── your_model/             # 模型文件夹
│       ├── model.model3.json   # 模型配置
│       ├── model.moc3          # 模型数据
│       └── textures/           # 贴图文件
├── config.py                   # 配置文件
├── full_main.py               # 完整启动脚本（渲染器+API）
├── simple_live2d_renderer.py  # 纯渲染器
├── simple_flask_api.py        # API 服务
├── real_live2d_controller.py  # Live2D 控制器
├── api_demo.py               # API 功能演示
├── requirements.txt          # 生产环境依赖
├── requirements-dev.txt      # 开发环境依赖
├── install.bat/.sh          # 自动安装脚本
├── run.bat                  # Windows 快速启动
├── check_env.py            # 环境检查工具
├── setup.py               # Python 包安装配置
└── api_usage_examples.md  # API 使用示例
```

## 🎯 使用方式

### 1. 完整模式（推荐）
```bash
python full_main.py
```
- 同时启动渲染器和 API 服务
- 适合需要外部控制的场景

### 2. 仅渲染器模式
```bash
python simple_live2d_renderer.py
```
- 只启动桌面渲染器
- 适合纯桌面宠物使用

### 3. API 功能演示
```bash
python api_demo.py
```
- 演示所有 API 功能
- 适合学习和测试

## ⚙️ 配置选项

在 `config.py` 中可以配置：

```python
# 窗口设置
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 1200
WINDOW_TITLE = "Live2D Desktop Renderer"

# 渲染设置
FPS = 60
BACKGROUND_COLOR = (0.0, 0.0, 0.0, 0.0)  # 透明背景

# 功能开关
OBS_COMPATIBLE_MODE = False        # OBS 兼容模式
CLICK_THROUGH_ENABLED = False      # 鼠标穿透
OBS_MODE_OPACITY = 1.0            # OBS 模式不透明度

# API 设置
API_HOST = "127.0.0.1"
API_PORT = None  # 自动选择端口
```

## 🎮 托盘菜单功能

右键点击系统托盘图标可以：
- **显示/隐藏窗口**
- **切换 OBS 模式**：在桌面宠物模式和直播模式间切换
- **切换鼠标穿透**：启用/禁用鼠标事件穿透
- **切换调整模式**：显示边框，拖拽调整窗口大小
- **退出程序**

## 🌐 API 接口

### 基础功能
- `GET /` - 获取 API 信息和完整端点列表
- `GET /models` - 获取可用模型列表
- `GET /model/info` - 获取当前模型信息

### 参数控制
- `POST /model/parameter` - 设置单个参数
- `POST /model/parameters` - 批量设置参数
- `POST /model/parameter_detailed` - 设置参数（包含权重）
- `GET /model/parameters/info` - 获取所有参数信息

### 表情和动作
- `POST /model/expression` - 播放表情
- `POST /model/expression/random` - 随机表情
- `POST /model/motion` - 播放动作
- `POST /model/motion/random` - 随机动作

### 模型变换
- `POST /model/resize` - 调整画布大小
- `POST /model/offset` - 设置偏移
- `POST /model/scale` - 设置缩放
- `POST /model/rotate` - 旋转模型

详细的 API 文档请参考 `api_usage_examples.md`

## 🔧 开发环境

### 安装开发依赖
```bash
pip install -r requirements-dev.txt
```

### 代码质量工具
```bash
# 代码格式化
black *.py

# 代码检查
flake8 *.py

# 类型检查
mypy *.py

# 运行测试
pytest
```

## 📋 系统要求

### 最低要求
- **Python**: 3.8 或更高版本
- **操作系统**: Windows 10, Linux (Ubuntu 18.04+), macOS 10.14+
- **内存**: 4GB RAM
- **显卡**: 支持 OpenGL 3.0 的显卡

### 推荐配置
- **Python**: 3.10+
- **内存**: 8GB RAM
- **显卡**: 独立显卡，支持 OpenGL 4.0+

## 🐛 故障排除

### 常见问题

1. **PyQt5 安装失败**
   ```bash
   # Linux
   sudo apt install python3-pyqt5 python3-pyqt5-dev
   
   # macOS
   brew install pyqt5
   ```

2. **OpenGL 相关错误**
   ```bash
   # 安装 OpenGL 系统库
   sudo apt install libgl1-mesa-dev libglu1-mesa-dev  # Linux
   ```

3. **live2d-py 安装问题**
   - 确保使用 64 位 Python
   - 检查是否有预编译包可用

4. **OBS 无法捕获窗口**
   - 启用 OBS 兼容模式
   - 在 OBS 中使用"窗口捕获"而非"显示捕获"

5. **鼠标穿透不生效**
   - 确保在 Windows 平台上运行
   - 检查是否有管理员权限要求

### 环境诊断
```bash
python check_env.py
```

## 📖 API 示例

### Python 示例
```python
import requests

# 设置参数
requests.post("http://localhost:6000/model/parameter", 
    json={"name": "ParamAngleX", "value": 15.0})

# 播放表情
requests.post("http://localhost:6000/model/expression", 
    json={"expression": "happy"})

# 播放动作
requests.post("http://localhost:6000/model/motion", 
    json={"motion": "idle", "no": 0, "priority": 3})
```

### JavaScript 示例
```javascript
// 设置参数
fetch('http://localhost:6000/model/parameter', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({name: 'ParamAngleX', value: 15.0})
});

// 播放随机表情
fetch('http://localhost:6000/model/expression/random', {
    method: 'POST'
});
```

更多示例请参考 `api_usage_examples.md`

## 📄 许可证

本项目基于 MIT 许可证开源。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📞 支持

如果遇到问题，请：
1. 运行 `python check_env.py` 检查环境
2. 查看控制台错误信息
3. 提交 Issue 并附上错误日志