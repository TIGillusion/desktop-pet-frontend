@echo off
echo ========================================
echo Live2D Desktop API 快速启动
echo ========================================
echo.

REM 检查虚拟环境是否存在
if not exist venv (
    echo [错误] 虚拟环境不存在，请先运行 install.bat 安装依赖
    pause
    exit /b 1
)

REM 激活虚拟环境
echo [信息] 激活虚拟环境...
call venv\Scripts\activate.bat

REM 检查模型目录
if not exist models (
    echo [警告] models/ 目录不存在，将创建空目录
    mkdir models
    echo [提示] 请将 Live2D 模型文件放入 models/ 目录
)

echo.
echo 请选择启动模式:
echo 1. 完整模式 (渲染器 + API服务)
echo 2. 仅渲染器模式
echo 3. 仅API服务模式  
echo 4. API功能演示
echo 5. 退出
echo.

set /p choice="请输入选择 (1-5): "

if "%choice%"=="1" (
    echo [启动] 完整模式 - 渲染器 + API服务
    python full_main.py
) else if "%choice%"=="2" (
    echo [启动] 仅渲染器模式
    python simple_live2d_renderer.py
) else if "%choice%"=="3" (
    echo [启动] 仅API服务模式
    python simple_flask_api.py
) else if "%choice%"=="4" (
    echo [启动] API功能演示
    python api_demo.py
) else if "%choice%"=="5" (
    echo 退出...
    exit /b 0
) else (
    echo [错误] 无效选择
    pause
    exit /b 1
)

pause