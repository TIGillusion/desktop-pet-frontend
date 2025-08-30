"""
Live2D Desktop API Setup Script
"""
from setuptools import setup, find_packages
import os

# 读取 README 文件
def read_long_description():
    readme_path = os.path.join(os.path.dirname(__file__), '使用说明.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "Live2D Desktop API - 桌面Live2D渲染器和HTTP API服务"

# 读取依赖
def read_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            # 过滤掉注释和空行
            return [line.strip() for line in lines 
                   if line.strip() and not line.strip().startswith('#')]
    return []

setup(
    name="live2d-desktop-api",
    version="1.0.0",
    author="Live2D Desktop API Team",
    author_email="",
    description="桌面Live2D渲染器和HTTP API服务",
    long_description=read_long_description(),
    long_description_content_type="text/markdown",
    url="",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Multimedia :: Graphics :: 3D Rendering",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "isort>=5.12.0",
            "mypy>=1.5.0",
        ],
        "performance": [
            "psutil>=5.9.0",
            "Pillow>=9.0.0",  # 图像处理优化
        ]
    },
    entry_points={
        "console_scripts": [
            "live2d-desktop=full_main:main",
            "live2d-renderer=simple_live2d_renderer:main",
            "live2d-api=simple_flask_api:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.md", "*.json", "*.bat", "*.sh"],
        "models": ["*"],
    },
    project_urls={
        "Documentation": "https://github.com/your-repo/wiki",
        "Source": "https://github.com/your-repo",
        "Tracker": "https://github.com/your-repo/issues",
    },
)