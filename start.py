#!/usr/bin/env python
"""
NovaPaw Startup Script
启动 NovaPaw 项目（后端 API + 前端静态文件服务）

首次运行会自动创建虚拟环境并安装所有依赖，之后直接启动。

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
    return Path(__file__).parent.absolute()


def _setup_env(project_root):
    """Create venv and install novapaw if env doesn't exist yet."""
    venv_python = project_root / "env" / "python.exe"

    if venv_python.exists():
        try:
            result = subprocess.run(
                [str(venv_python), "-c", "import novapaw"],
                capture_output=True, timeout=10,
            )
            if result.returncode == 0:
                return True
        except Exception:
            pass

    print("首次运行 — 正在创建虚拟环境...")
    subprocess.run(
        [sys.executable, "-m", "venv", str(project_root / "env")],
        check=True,
    )

    # Upgrade pip first to avoid the pip 24.0 resolvelib bug
    print("升级 pip...")
    subprocess.run(
        [str(venv_python), "-m", "pip", "install", "--upgrade", "pip", "--quiet"],
        check=True,
    )

    # Install novapaw in editable mode with all deps
    print("安装 NovaPaw 及全部依赖（首次需要几分钟）...")
    subprocess.run(
        [str(venv_python), "-m", "pip", "install", "-e", ".[dev,full]", "--quiet"],
        cwd=str(project_root),
        check=True,
    )

    print("环境初始化完成！\n")
    return True


def activate_venv():
    project_root = get_project_root()
    venv_path = project_root / "env"

    # Auto-setup on first run
    if not _setup_env(project_root):
        print("错误：无法创建虚拟环境")
        return False

    os.environ["PATH"] = str(venv_path) + os.pathsep + os.environ["PATH"]
    os.environ["VIRTUAL_ENV"] = str(project_root / "env")

    venv_python = venv_path / "python.exe"
    if venv_python.exists():
        sys.executable = str(venv_python)

    return True


def build_frontend():
    print("正在构建前端...")
    console_path = get_project_root() / "console"

    if not console_path.exists():
        print("错误：console 目录不存在")
        return False

    node_modules = console_path / "node_modules"
    if not node_modules.exists():
        print("正在安装 npm 依赖...")
        try:
            subprocess.run(["npm", "install"], cwd=str(console_path), check=True)
        except subprocess.CalledProcessError as e:
            print(f"npm install 失败：{e}")
            return False

    try:
        subprocess.run(["npm", "run", "build"], cwd=str(console_path), check=True)
        print("前端构建完成！")
        return True
    except subprocess.CalledProcessError as e:
        print(f"前端构建失败：{e}")
        return False


def start_backend(debug=False, host="127.0.0.1", port=8088):
    print("正在启动 NovaPaw 后端服务...")
    project_root = get_project_root()
    os.environ["NOVAPAW_HOME"] = str(project_root)

    cmd = [
        sys.executable, "-m", "novapaw", "app",
        "--host", host,
        "--port", str(port),
    ]
    if debug:
        cmd.extend(["--log-level", "debug"])

    print(f"[EXIT-HOOK] backend command: {' '.join(cmd)}")

    try:
        result = subprocess.run(cmd, cwd=str(project_root), check=False)
        code = result.returncode
        if code == 0:
            print("[EXIT-HOOK] backend exited normally (code=0)")
            return True
        if code < 0:
            print(f"[EXIT-HOOK] backend exited by signal (code={code})")
        else:
            print(f"[EXIT-HOOK] backend exited with non-zero code ({code})")
        return False
    except KeyboardInterrupt:
        print("\n[EXIT-HOOK] backend interrupted by KeyboardInterrupt")
        return False
    except Exception as e:
        print(f"[EXIT-HOOK] backend exited due to unexpected exception: {e}")
        return False


def start_dev_mode(host="127.0.0.1", port=8088):
    print("=" * 60)
    print("NovaPaw 开发模式")
    print("=" * 60)
    print()

    project_root = get_project_root()
    console_path = project_root / "console"
    os.environ["NOVAPAW_HOME"] = str(project_root)

    backend_cmd = [
        sys.executable, "-m", "novapaw", "app",
        "--host", host, "--port", str(port),
        "--log-level", "debug",
    ]

    print(f"后端命令：novapaw app --host {host} --port {port} --log-level debug")
    print("前端命令：npm run dev")
    print(f"访问地址:\n  - 前端：http://localhost:5173\n  - 后端 API: http://{host}:{port}")
    print("按 Ctrl+C 停止服务")
    print("=" * 60)
    print()

    try:
        backend_process = subprocess.Popen(backend_cmd, cwd=str(project_root))
        time.sleep(2)
        frontend_process = subprocess.Popen(["npm", "run", "dev"], cwd=str(console_path))
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
    parser = argparse.ArgumentParser(
        description="NovaPaw 启动脚本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python start.py              # 启动后端服务（仅本机）
  python start.py --lan        # 启动后端服务（允许局域网访问）
  python start.py --port 9090  # 指定端口
  python start.py --dev        # 开发模式（前后端同时启动）
  python start.py --build      # 先构建前端再启动后端
        """,
    )
    parser.add_argument("--dev", action="store_true", help="开发模式：同时启动前后端服务")
    parser.add_argument("--build", action="store_true", help="先构建前端再启动后端")
    parser.add_argument("--debug", action="store_true", help="调试模式：启用 debug 日志")
    parser.add_argument("--lan", action="store_true", help="允许局域网访问（绑定 0.0.0.0）")
    parser.add_argument("--host", default=None, help="绑定的主机地址（覆盖 --lan）")
    parser.add_argument("--port", type=int, default=8088, help="绑定的端口（默认 8088）")

    args = parser.parse_args()
    host = args.host or ("0.0.0.0" if args.lan else "127.0.0.1")

    print("=" * 60)
    print("NovaPaw - Nova Personal AI Assistant Workstation")
    print("=" * 60)
    print()

    final_ok = True
    exit_reason = "normal"

    try:
        if not activate_venv():
            final_ok = False
            exit_reason = "activate_venv_failed"
            return 1

        if args.build or args.dev:
            if not build_frontend():
                print("警告：前端构建失败，但将继续启动后端服务")

        if args.dev:
            start_dev_mode(host=host, port=args.port)
        else:
            final_ok = start_backend(debug=args.debug, host=host, port=args.port)
            if not final_ok:
                exit_reason = "backend_process_exit_nonzero_or_interrupted"

        return 0 if final_ok else 1
    except KeyboardInterrupt:
        final_ok = False
        exit_reason = "keyboard_interrupt"
        return 130
    except Exception as e:
        final_ok = False
        exit_reason = f"unhandled_exception:{e}"
        raise
    finally:
        print(f"[EXIT-HOOK] start.py exiting: ok={final_ok}, reason={exit_reason}")


if __name__ == "__main__":
    sys.exit(main())
