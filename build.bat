@echo off
echo ========================================
echo Live2D Desktop API 项目构建脚本
echo ========================================
echo.

REM 激活虚拟环境
if not exist venv (
    echo [错误] 虚拟环境不存在，请先运行 install.bat
    pause
    exit /b 1
)

call venv\Scripts\activate.bat

echo [步骤 1/5] 环境检查...
python check_env.py
if errorlevel 1 (
    echo [错误] 环境检查失败，请解决问题后重试
    pause
    exit /b 1
)

echo.
echo [步骤 2/5] 代码格式化...
if exist venv\Scripts\black.exe (
    black *.py --line-length 100
    echo [完成] 代码格式化完成
) else (
    echo [跳过] black 未安装，跳过代码格式化
)

echo.
echo [步骤 3/5] 代码检查...
if exist venv\Scripts\flake8.exe (
    flake8 *.py --max-line-length 100 --ignore E203,W503
    echo [完成] 代码检查完成
) else (
    echo [跳过] flake8 未安装，跳过代码检查
)

echo.
echo [步骤 4/5] 运行测试...
if exist test_main.py (
    python test_main.py
    echo [完成] 测试完成
) else (
    echo [跳过] 测试文件不存在
)

echo.
echo [步骤 5/5] 创建分发包...
python setup.py sdist bdist_wheel
if errorlevel 1 (
    echo [错误] 包构建失败
    pause
    exit /b 1
)

echo.
echo ========================================
echo 构建完成！
echo ========================================
echo.
echo 构建输出:
echo   dist/           - 分发包文件
echo   build/          - 构建临时文件
echo   *.egg-info/     - 包信息文件
echo.
echo 安装构建的包:
echo   pip install dist\live2d_desktop_api-1.0.0-py3-none-any.whl
echo.

pause