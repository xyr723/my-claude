"""
配置同步模块。
调用 task sync 或 ansible-playbook 同步配置。
"""

import subprocess
from pathlib import Path
from typing import Optional


def run_sync(repo_path: Path, skip_confirm: bool = False, quiet: bool = False) -> bool:
    """
    运行配置同步。

    Args:
        repo_path: my-claude 仓库路径
        skip_confirm: 是否跳过确认（使用 --force）
        quiet: 是否安静模式（不显示输出）

    Returns:
        同步成功返回 True，失败返回 False
    """
    # 选择任务
    if skip_confirm:
        task_name = "sync-force"
    else:
        task_name = "sync"

    cmd = ["uv", "run", "task", task_name]

    try:
        if quiet:
            result = subprocess.run(
                cmd,
                cwd=repo_path,
                capture_output=True,
                text=True,
            )
        else:
            result = subprocess.run(
                cmd,
                cwd=repo_path,
            )

        return result.returncode == 0
    except KeyboardInterrupt:
        if not quiet:
            print("\n\n⚠️  同步已取消")
        return False
    except Exception as e:
        if not quiet:
            print(f"\n❌ 同步失败: {e}")
        return False


def run_check_sync(repo_path: Path) -> Optional[str]:
    """
    预览配置变更（不执行）。

    Args:
        repo_path: my-claude 仓库路径

    Returns:
        变更预览输出，如果失败返回 None
    """
    cmd = ["uv", "run", "task", "check-sync"]

    try:
        result = subprocess.run(
            cmd,
            cwd=repo_path,
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            return result.stdout
        return None
    except Exception:
        return None
