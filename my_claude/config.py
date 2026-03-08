"""
仓库路径发现与配置管理模块。
"""

import os
from pathlib import Path
from typing import Optional


def find_repo_path(provided_path: Optional[str] = None) -> Path:
    """
    查找 my-claude 仓库路径。

    优先级：
    1. 命令行参数 provided_path
    2. 环境变量 MY_CLAUDE_REPO
    3. 当前目录是否是仓库
    4. 从当前目录向上查找

    Args:
        provided_path: 命令行提供的路径

    Returns:
        仓库根目录的 Path 对象

    Raises:
        FileNotFoundError: 找不到仓库时抛出
    """
    # 优先级 1: 命令行参数
    if provided_path:
        path = Path(provided_path).resolve()
        if is_my_claude_repo(path):
            return path
        raise FileNotFoundError(f"指定路径不是 my-claude 仓库: {provided_path}")

    # 优先级 2: 环境变量
    env_path = os.getenv("MY_CLAUDE_REPO")
    if env_path:
        path = Path(env_path).resolve()
        if is_my_claude_repo(path):
            return path
        raise FileNotFoundError(
            f"MY_CLAUDE_REPO 路径不是 my-claude 仓库: {env_path}")

    # 优先级 3: 当前目录
    cwd = Path.cwd()
    if is_my_claude_repo(cwd):
        return cwd

    # 优先级 4: 向上查找
    for parent in [cwd] + list(cwd.parents):
        if is_my_claude_repo(parent):
            return parent

    raise FileNotFoundError(
        "无法找到 my-claude 仓库。\n"
        "请使用 --repo 参数指定路径，或设置 MY_CLAUDE_REPO 环境变量。"
    )


def is_my_claude_repo(path: Path) -> bool:
    """
    判断给定路径是否是 my-claude 仓库。

    Args:
        path: 要检查的路径

    Returns:
        如果是 my-claude 仓库返回 True，否则返回 False
    """
    if not path.is_dir():
        return False

    # 检查关键文件是否存在
    required_files = [
        "inventory/default/group_vars/all/models.yml",
        "inventory/default/group_vars/all/settings.yml",
        "Taskfile.yml",
        "playbooks/setup.yml",
    ]

    for file_path in required_files:
        if not (path / file_path).exists():
            return False

    return True


def get_models_yml_path(repo_path: Path) -> Path:
    """获取 models.yml 文件路径。"""
    return repo_path / "inventory" / "default" / "group_vars" / "all" / "models.yml"


def get_settings_yml_path(repo_path: Path) -> Path:
    """获取 settings.yml 文件路径。"""
    return repo_path / "inventory" / "default" / "group_vars" / "all" / "settings.yml"


def get_output_styles_dir(repo_path: Path) -> Path:
    """获取 output-styles 目录路径。"""
    return repo_path / "claude-assets" / "output-styles"
