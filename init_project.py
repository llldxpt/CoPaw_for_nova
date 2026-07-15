#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
NovaPaw Initialization Script
Automates the initialization of NovaPaw user data for single or multiple instances

Usage:
    python init_project.py              # Run initialization (skip if already done)
    python init_project.py --force     # Force re-initialization
    python init_project.py --check      # Check if initialized
    python init_project.py --workspace myws    # Initialize specific workspace
    python init_project.py --count 3           # Initialize 3 workspaces
    python init_project.py --count 3 --workspace-prefix myws  # Initialize workspace1-3
"""

import os
import sys
import subprocess
from pathlib import Path
import argparse


def get_project_root():
    return Path(__file__).parent.absolute()


def get_venv_python():
    project_root = get_project_root()
    venv_python = project_root / "env" / "python.exe"

    if not venv_python.exists():
        print(f"Error: Virtual environment Python not found at {venv_python}")
        print("Please create virtual environment first:")
        print("  python -m venv env")
        return None
    return str(venv_python)


def check_initialized(workspace_path: Path = None):
    if workspace_path is None:
        workspace_path = Path.home() / ".novapaw"

    config_file = workspace_path / "config.json"

    if config_file.exists():
        print(f"Already initialized: {config_file}")
        return True
    else:
        print(f"Not initialized yet: {config_file} does not exist")
        return False


def run_novapaw_init(workspace_path: Path = None, force=False):
    venv_python = get_venv_python()
    if not venv_python:
        return False

    project_root = get_project_root()

    print("=" * 60)
    print("NovaPaw Initialization")
    print("=" * 60)
    print()

    if workspace_path:
        print(f"Workspace: {workspace_path}")
        if check_initialized(workspace_path) and not force:
            print("Workspace already initialized.")
            print("Use --force to re-initialize")
            return True
    else:
        if check_initialized() and not force:
            print("Project already initialized.")
            print("Use --force to re-initialize:")
            print("  python init_project.py --force")
            return True

    if force:
        print("Force re-initialization requested...")

    env = os.environ.copy()
    if workspace_path:
        env["NOVAPAW_WORKING_DIR"] = str(workspace_path.resolve())

    cmd = [venv_python, "-m", "novapaw", "init", "--defaults", "--accept-security"]

    if force:
        cmd.append("--force")

    try:
        subprocess.run(cmd, cwd=str(project_root), env=env, check=True)
        print()
        print("=" * 60)
        print("Initialization complete!")
        print("=" * 60)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Initialization failed: {e}")
        return False


def initialize_workspace(workspace_name: str, force: bool = False):
    project_root = get_project_root()
    workspace_path = project_root / workspace_name

    workspace_path.mkdir(parents=True, exist_ok=True)

    print(f"Initializing workspace: {workspace_name}")
    return run_novapaw_init(workspace_path, force)


def initialize_multiple(count: int, workspace_prefix: str = "workspace", force: bool = False):
    print(f"Initializing {count} workspaces with prefix '{workspace_prefix}':")
    print()

    success_count = 0
    for i in range(1, count + 1):
        workspace_name = f"{workspace_prefix}{i}"
        print(f"[{i}/{count}] Initializing {workspace_name}...")
        if initialize_workspace(workspace_name, force):
            success_count += 1
        print()

    print("=" * 60)
    print(f"Initialization complete: {success_count}/{count} workspaces")
    print("=" * 60)
    print()
    print("Workspace Summary:")
    for i in range(1, count + 1):
        workspace_name = f"{workspace_prefix}{i}"
        print(f"  {workspace_name}: {get_project_root() / workspace_name}")
    print()

    return success_count == count


def main():
    parser = argparse.ArgumentParser(
        description="NovaPaw Initialization Script",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python init_project.py                          # Default initialization
  python init_project.py --force                  # Force re-initialize
  python init_project.py --check                  # Check if initialized
  python init_project.py --workspace myws         # Initialize specific workspace
  python init_project.py --count 3                # Initialize 3 workspaces
  python init_project.py --count 3 --workspace-prefix myws  # Initialize myws1-3
  python init_project.py --count 3 --force        # Force re-initialize all
        """
    )

    parser.add_argument(
        "--force",
        action="store_true",
        help="Force re-initialization"
    )

    parser.add_argument(
        "--check",
        action="store_true",
        help="Check if initialized"
    )

    parser.add_argument(
        "--workspace",
        type=str,
        help="Workspace directory name to initialize"
    )

    parser.add_argument(
        "--count",
        type=int,
        default=0,
        help="Number of workspaces to initialize"
    )

    parser.add_argument(
        "--workspace-prefix",
        type=str,
        default="workspace",
        help="Workspace prefix for --count mode (default: workspace)"
    )

    args = parser.parse_args()

    if args.check:
        check_initialized()
    elif args.count > 0:
        initialize_multiple(args.count, args.workspace_prefix, args.force)
    elif args.workspace:
        initialize_workspace(args.workspace, args.force)
    else:
        run_novapaw_init(force=args.force)


if __name__ == "__main__":
    main()
