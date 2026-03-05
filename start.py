#!/usr/bin/env python
"""
NovaPaw Startup Script
启动 NovaPaw 项目（后端 API + 前端静态文件服务）

使用方法:
    python start.py              # 启动后端服务（默认端口 8088）
    python start.py --dev        # 开发模式（同时启动前后端）
    python start.py --build      # 先构建前端再启动后端
    python start.py --help       # 显示帮助信息
"""

import os
import sys
import subprocess
import argparse
import time
from pathlib import Path


def get_project_root():
    """获取项目根目录"""
    return Path(__file__).parent.absolute()


def activate_venv():
    """激活虚拟环境"""
    project_root = get_project_root()
    venv_path = project_root / "env" / "Scripts"
    
    if not venv_path.exists():
        print(f"错误：虚拟环境不存在于 {venv_path}")
        print("请先创建虚拟环境并安装依赖:")
        print("  python -m venv env")
        print("  .\\env\\Scripts\\Activate")
        print("  pip install -e \".[dev]\"")
        return False
    
    # 将虚拟环境的 Scripts 目录添加到 PATH
    os.environ["PATH"] = str(venv_path) + os.pathsep + os.environ["PATH"]
    os.environ["VIRTUAL_ENV"] = str(project_root / "env")
    
    # 更新 sys.path 以使用虚拟环境的 Python
    venv_python = venv_path / "python.exe"
    if venv_python.exists():
        sys.executable = str(venv_python)
    
    return True


def check_dependencies():
    """检查依赖是否已安装"""
    try:
        import novapaw
        return True
    except ImportError:
        return False


def install_dependencies():
    """安装项目依赖"""
    print("正在安装项目依赖...")
    project_root = get_project_root()
    
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-e", ".[dev]"],
            cwd=str(project_root),
            check=True
        )
        print("依赖安装完成！")
        return True
    except subprocess.CalledProcessError as e:
        print(f"依赖安装失败：{e}")
        return False


def build_frontend():
    """构建前端"""
    print("正在构建前端...")
    console_path = get_project_root() / "console"
    
    if not console_path.exists():
        print("错误：console 目录不存在")
        return False
    
    # 检查 node_modules
    node_modules = console_path / "node_modules"
    if not node_modules.exists():
        print("正在安装 npm 依赖...")
        try:
            subprocess.run(["npm", "install"], cwd=str(console_path), check=True)
        except subprocess.CalledProcessError as e:
            print(f"npm install 失败：{e}")
            return False
    
    # 构建前端
    try:
        subprocess.run(["npm", "run", "build"], cwd=str(console_path), check=True)
        print("前端构建完成！")
        return True
    except subprocess.CalledProcessError as e:
        print(f"前端构建失败：{e}")
        return False


def start_backend(debug=False):
    """启动后端服务"""
    print("正在启动 NovaPaw 后端服务...")
    project_root = get_project_root()
    
    # 设置环境变量
    os.environ["NOVAPAW_HOME"] = str(project_root)
    
    cmd = [sys.executable, "-m", "novapaw", "app"]
    
    if debug:
        cmd.append("--debug")
    
    try:
        subprocess.run(cmd, cwd=str(project_root), check=True)
    except subprocess.CalledProcessError as e:
        print(f"后端服务启动失败：{e}")
        return False
    except KeyboardInterrupt:
        print("\n后端服务已停止")
    
    return True


def start_dev_mode():
    """开发模式：同时启动前后端"""
    print("=" * 60)
    print("NovaPaw 开发模式")
    print("=" * 60)
    print()
    
    project_root = get_project_root()
    console_path = project_root / "console"
    
    # 设置环境变量
    os.environ["NOVAPAW_HOME"] = str(project_root)
    
    # 启动后端
    backend_cmd = [sys.executable, "-m", "novapaw", "app", "--debug"]
    
    print("后端命令：novapaw app --debug")
    print("前端命令：npm run dev")
    print()
    print("访问地址:")
    print("  - 前端：http://localhost:5173")
    print("  - 后端 API: http://localhost:8088")
    print()
    print("按 Ctrl+C 停止服务")
    print("=" * 60)
    print()
    
    try:
        # 启动后端进程
        backend_process = subprocess.Popen(
            backend_cmd,
            cwd=str(project_root)
        )
        
        # 等待 2 秒确保后端启动
        time.sleep(2)
        
        # 启动前端进程
        frontend_process = subprocess.Popen(
            ["npm", "run", "dev"],
            cwd=str(console_path)
        )
        
        # 等待进程结束
        backend_process.wait()
        frontend_process.wait()
        
    except KeyboardInterrupt:
        print("\n正在停止服务...")
        backend_process.terminate()
        frontend_process.terminate()
        backend_process.wait()
        frontend_process.wait()
        print("所有服务已停止")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="NovaPaw 启动脚本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python start.py              # 启动后端服务
  python start.py --dev        # 开发模式（前后端同时启动）
  python start.py --build      # 先构建前端再启动后端
  python start.py --reinstall  # 重新安装依赖
        """
    )
    
    parser.add_argument(
        "--dev",
        action="store_true",
        help="开发模式：同时启动前后端服务"
    )
    
    parser.add_argument(
        "--build",
        action="store_true",
        help="先构建前端再启动后端"
    )
    
    parser.add_argument(
        "--reinstall",
        action="store_true",
        help="重新安装 Python 依赖"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="调试模式：启用 debug 日志"
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("NovaPaw - Nova Personal AI Assistant Workstation")
    print("=" * 60)
    print()
    
    # 激活虚拟环境
    if not activate_venv():
        sys.exit(1)
    
    # 检查/安装依赖
    if args.reinstall or not check_dependencies():
        if not install_dependencies():
            sys.exit(1)
    
    # 构建前端
    if args.build or args.dev:
        if not build_frontend():
            print("警告：前端构建失败，但将继续启动后端服务")
    
    # 启动服务
    if args.dev:
        start_dev_mode()
    else:
        start_backend(debug=args.debug)


if __name__ == "__main__":
    main()
