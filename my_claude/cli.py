"""
my-claude CLI 主入口。
用于快速管理 my-claude-ansible 项目的配置。
"""

from pathlib import Path
from typing import Optional
import click
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

from .config import (
    find_repo_path,
    get_models_yml_path,
    get_settings_yml_path,
    get_output_styles_dir,
)
from .models import (
    list_available_models,
    get_current_model,
    update_use_model,
    get_current_output_style,
    list_available_output_styles,
    update_output_style,
    get_current_model_level,
    list_available_model_levels,
    update_model_level,
    get_always_thinking_enabled,
    update_always_thinking_enabled,
    get_current_permission_mode,
    list_available_permission_modes,
    update_permission_mode,
)
from .sync import run_sync, run_check_sync


CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"]}

app = typer.Typer(
    name="my-claude",
    help="快速管理 my-claude-ansible 项目配置的 CLI 工具",
    add_completion=True,
    context_settings=CONTEXT_SETTINGS,
)
console = Console()


def get_repo(repo: Optional[str] = None) -> Path:
    """获取仓库路径的辅助函数。"""
    try:
        return find_repo_path(repo)
    except FileNotFoundError as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(1)


# ========== 模型提供商命令组 ==========


model_provider_group = typer.Typer(
    name="provider",
    help="模型提供商配置管理",
    context_settings=CONTEXT_SETTINGS,
)
app.add_typer(model_provider_group)


@model_provider_group.command("list")
def list_providers(
    repo: Optional[str] = typer.Option(
        None, "--repo", "-r", help="my-claude 仓库路径"),
):
    """列出所有可用的模型提供商。"""
    repo_path = get_repo(repo)
    models_yml_path = get_models_yml_path(repo_path)

    try:
        models = list_available_models(models_yml_path)
    except Exception as e:
        console.print(f"[red]读取配置失败: {e}[/red]")
        raise typer.Exit(1)

    table = Table(
        title="可用模型提供商",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold magenta",
    )
    table.add_column("状态", style="dim", width=6)
    table.add_column("名称", style="cyan")
    table.add_column("API 地址", style="green")
    table.add_column("Opus 模型", style="yellow")

    for model in models:
        status = "✓ 当前" if model["is_current"] else ""
        config = model["config"]
        table.add_row(
            status,
            model["name"],
            config.get("baseURL", "-"),
            config.get("opus_model", "-"),
        )

    console.print(table)


@model_provider_group.command("current")
def current_provider(
    repo: Optional[str] = typer.Option(
        None, "--repo", "-r", help="my-claude 仓库路径"),
):
    """显示当前使用的模型提供商。"""
    repo_path = get_repo(repo)
    models_yml_path = get_models_yml_path(repo_path)

    try:
        current = get_current_model(models_yml_path)
    except Exception as e:
        console.print(f"[red]读取配置失败: {e}[/red]")
        raise typer.Exit(1)

    console.print(
        Panel(f"当前模型提供商: [bold cyan]{current}[/bold cyan]", box=box.ROUNDED))


@model_provider_group.command("use")
def use_provider(
    model_name: str = typer.Argument(..., help="要使用的模型提供商名称"),
    sync: bool = typer.Option(False, "--sync", "-s", help="切换后自动同步配置"),
    skip_confirm: bool = typer.Option(False, "--force", "-f", help="同步时跳过确认"),
    repo: Optional[str] = typer.Option(
        None, "--repo", "-r", help="my-claude 仓库路径"),
):
    """切换模型提供商。"""
    repo_path = get_repo(repo)
    models_yml_path = get_models_yml_path(repo_path)

    try:
        update_use_model(models_yml_path, model_name)
    except ValueError as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]更新配置失败: {e}[/red]")
        raise typer.Exit(1)

    console.print(f"[green]✅ 已切换到模型提供商: [bold]{model_name}[/bold][/green]")

    if sync:
        console.print("\n[cyan]🔄 开始同步配置...[/cyan]\n")
        success = run_sync(repo_path, skip_confirm=skip_confirm)
        if success:
            console.print("\n[green]✅ 配置同步完成！[/green]")
        else:
            console.print("\n[red]❌ 配置同步失败[/red]")
            raise typer.Exit(1)
    else:
        console.print("\n[yellow]💡 提示: 运行 'my-claude sync' 同步配置[/yellow]")


# ========== 输出风格命令组 ==========


style_group = typer.Typer(
    name="style",
    help="输出风格配置管理",
    context_settings=CONTEXT_SETTINGS,
)
app.add_typer(style_group)


@style_group.command("list")
def list_styles(
    repo: Optional[str] = typer.Option(
        None, "--repo", "-r", help="my-claude 仓库路径"),
):
    """列出所有可用的输出风格。"""
    repo_path = get_repo(repo)
    settings_yml_path = get_settings_yml_path(repo_path)
    output_styles_dir = get_output_styles_dir(repo_path)

    try:
        current = get_current_output_style(settings_yml_path)
        available = list_available_output_styles(output_styles_dir)
    except Exception as e:
        console.print(f"[red]读取配置失败: {e}[/red]")
        raise typer.Exit(1)

    table = Table(
        title="可用输出风格",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold magenta",
    )
    table.add_column("状态", style="dim", width=6)
    table.add_column("名称", style="cyan")

    for style in available:
        status = "✓ 当前" if style == current else ""
        table.add_row(status, style)

    console.print(table)


@style_group.command("current")
def current_style(
    repo: Optional[str] = typer.Option(
        None, "--repo", "-r", help="my-claude 仓库路径"),
):
    """显示当前使用的输出风格。"""
    repo_path = get_repo(repo)
    settings_yml_path = get_settings_yml_path(repo_path)

    try:
        current = get_current_output_style(settings_yml_path)
    except Exception as e:
        console.print(f"[red]读取配置失败: {e}[/red]")
        raise typer.Exit(1)

    console.print(
        Panel(f"当前输出风格: [bold cyan]{current}[/bold cyan]", box=box.ROUNDED))


@style_group.command("use")
def use_style(
    style_name: str = typer.Argument(..., help="要使用的输出风格名称"),
    sync: bool = typer.Option(False, "--sync", "-s", help="切换后自动同步配置"),
    skip_confirm: bool = typer.Option(False, "--force", "-f", help="同步时跳过确认"),
    repo: Optional[str] = typer.Option(
        None, "--repo", "-r", help="my-claude 仓库路径"),
):
    """切换输出风格。"""
    repo_path = get_repo(repo)
    settings_yml_path = get_settings_yml_path(repo_path)
    output_styles_dir = get_output_styles_dir(repo_path)

    # 验证风格是否存在
    try:
        available = list_available_output_styles(output_styles_dir)
        if style_name not in available:
            console.print(
                f"[red]输出风格 '{style_name}' 不存在。可用风格: {', '.join(available)}[/red]")
            raise typer.Exit(1)

        update_output_style(settings_yml_path, style_name)
    except Exception as e:
        console.print(f"[red]更新配置失败: {e}[/red]")
        raise typer.Exit(1)

    console.print(f"[green]✅ 已切换到输出风格: [bold]{style_name}[/bold][/green]")

    if sync:
        console.print("\n[cyan]🔄 开始同步配置...[/cyan]\n")
        success = run_sync(repo_path, skip_confirm=skip_confirm)
        if success:
            console.print("\n[green]✅ 配置同步完成！[/green]")
        else:
            console.print("\n[red]❌ 配置同步失败[/red]")
            raise typer.Exit(1)
    else:
        console.print("\n[yellow]💡 提示: 运行 'my-claude sync' 同步配置[/yellow]")


# ========== 模型级别命令组 ==========


model_level_group = typer.Typer(
    name="level",
    help="模型级别配置管理（opus/sonnet/haiku）",
    context_settings=CONTEXT_SETTINGS,
)
app.add_typer(model_level_group)


@model_level_group.command("list")
def list_levels(
    repo: Optional[str] = typer.Option(
        None, "--repo", "-r", help="my-claude 仓库路径"),
):
    """列出所有可用的模型级别。"""
    repo_path = get_repo(repo)
    settings_yml_path = get_settings_yml_path(repo_path)

    try:
        current = get_current_model_level(settings_yml_path)
        available = list_available_model_levels()
    except Exception as e:
        console.print(f"[red]读取配置失败: {e}[/red]")
        raise typer.Exit(1)

    table = Table(
        title="可用模型级别",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold magenta",
    )
    table.add_column("状态", style="dim", width=6)
    table.add_column("名称", style="cyan")
    table.add_column("说明", style="dim")

    descriptions = {
        "opus": "最高智能，最强大",
        "sonnet": "平衡选择，推荐日常使用",
        "haiku": "最快响应，轻量级任务",
    }

    for level in available:
        status = "✓ 当前" if level == current else ""
        table.add_row(status, level, descriptions.get(level, "-"))

    console.print(table)


@model_level_group.command("current")
def current_level(
    repo: Optional[str] = typer.Option(
        None, "--repo", "-r", help="my-claude 仓库路径"),
):
    """显示当前使用的模型级别。"""
    repo_path = get_repo(repo)
    settings_yml_path = get_settings_yml_path(repo_path)

    try:
        current = get_current_model_level(settings_yml_path)
    except Exception as e:
        console.print(f"[red]读取配置失败: {e}[/red]")
        raise typer.Exit(1)

    console.print(
        Panel(f"当前模型级别: [bold cyan]{current}[/bold cyan]", box=box.ROUNDED))


@model_level_group.command("use")
def use_level(
    level_name: str = typer.Argument(..., help="要使用的模型级别（opus/sonnet/haiku）"),
    sync: bool = typer.Option(False, "--sync", "-s", help="切换后自动同步配置"),
    skip_confirm: bool = typer.Option(False, "--force", "-f", help="同步时跳过确认"),
    repo: Optional[str] = typer.Option(
        None, "--repo", "-r", help="my-claude 仓库路径"),
):
    """切换模型级别。"""
    repo_path = get_repo(repo)
    settings_yml_path = get_settings_yml_path(repo_path)

    try:
        update_model_level(settings_yml_path, level_name)
    except ValueError as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]更新配置失败: {e}[/red]")
        raise typer.Exit(1)

    console.print(f"[green]✅ 已切换到模型级别: [bold]{level_name}[/bold][/green]")

    if sync:
        console.print("\n[cyan]🔄 开始同步配置...[/cyan]\n")
        success = run_sync(repo_path, skip_confirm=skip_confirm)
        if success:
            console.print("\n[green]✅ 配置同步完成！[/green]")
        else:
            console.print("\n[red]❌ 配置同步失败[/red]")
            raise typer.Exit(1)
    else:
        console.print("\n[yellow]💡 提示: 运行 'my-claude sync' 同步配置[/yellow]")


# ========== 深度思考命令组 ==========


thinking_group = typer.Typer(
    name="thinking",
    help="深度思考模式配置管理",
    context_settings=CONTEXT_SETTINGS,
)
app.add_typer(thinking_group)


@thinking_group.command("status")
def thinking_status(
    repo: Optional[str] = typer.Option(
        None, "--repo", "-r", help="my-claude 仓库路径"),
):
    """显示深度思考模式状态。"""
    repo_path = get_repo(repo)
    settings_yml_path = get_settings_yml_path(repo_path)

    try:
        enabled = get_always_thinking_enabled(settings_yml_path)
    except Exception as e:
        console.print(f"[red]读取配置失败: {e}[/red]")
        raise typer.Exit(1)

    status_text = "[green]已启用[/green]" if enabled else "[red]已禁用[/red]"
    console.print(Panel(f"深度思考模式: {status_text}", box=box.ROUNDED))


@thinking_group.command("enable")
def enable_thinking(
    sync: bool = typer.Option(False, "--sync", "-s", help="切换后自动同步配置"),
    skip_confirm: bool = typer.Option(False, "--force", "-f", help="同步时跳过确认"),
    repo: Optional[str] = typer.Option(
        None, "--repo", "-r", help="my-claude 仓库路径"),
):
    """启用深度思考模式。"""
    repo_path = get_repo(repo)
    settings_yml_path = get_settings_yml_path(repo_path)

    try:
        update_always_thinking_enabled(settings_yml_path, True)
    except Exception as e:
        console.print(f"[red]更新配置失败: {e}[/red]")
        raise typer.Exit(1)

    console.print("[green]✅ 已启用深度思考模式[/green]")

    if sync:
        console.print("\n[cyan]🔄 开始同步配置...[/cyan]\n")
        success = run_sync(repo_path, skip_confirm=skip_confirm)
        if success:
            console.print("\n[green]✅ 配置同步完成！[/green]")
        else:
            console.print("\n[red]❌ 配置同步失败[/red]")
            raise typer.Exit(1)


@thinking_group.command("disable")
def disable_thinking(
    sync: bool = typer.Option(False, "--sync", "-s", help="切换后自动同步配置"),
    skip_confirm: bool = typer.Option(False, "--force", "-f", help="同步时跳过确认"),
    repo: Optional[str] = typer.Option(
        None, "--repo", "-r", help="my-claude 仓库路径"),
):
    """禁用深度思考模式。"""
    repo_path = get_repo(repo)
    settings_yml_path = get_settings_yml_path(repo_path)

    try:
        update_always_thinking_enabled(settings_yml_path, False)
    except Exception as e:
        console.print(f"[red]更新配置失败: {e}[/red]")
        raise typer.Exit(1)

    console.print("[green]✅ 已禁用深度思考模式[/green]")

    if sync:
        console.print("\n[cyan]🔄 开始同步配置...[/cyan]\n")
        success = run_sync(repo_path, skip_confirm=skip_confirm)
        if success:
            console.print("\n[green]✅ 配置同步完成！[/green]")
        else:
            console.print("\n[red]❌ 配置同步失败[/red]")
            raise typer.Exit(1)


# ========== 权限模式命令组 ==========


permission_group = typer.Typer(
    name="permission",
    help="权限模式配置管理",
    context_settings=CONTEXT_SETTINGS,
)
app.add_typer(permission_group)


@permission_group.command("list")
def list_permissions(
    repo: Optional[str] = typer.Option(
        None, "--repo", "-r", help="my-claude 仓库路径"),
):
    """列出所有可用的权限模式。"""
    repo_path = get_repo(repo)
    settings_yml_path = get_settings_yml_path(repo_path)

    try:
        current = get_current_permission_mode(settings_yml_path)
        available = list_available_permission_modes()
    except Exception as e:
        console.print(f"[red]读取配置失败: {e}[/red]")
        raise typer.Exit(1)

    table = Table(
        title="可用权限模式",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold magenta",
    )
    table.add_column("状态", style="dim", width=6)
    table.add_column("名称", style="cyan")

    for mode in available:
        status = "✓ 当前" if mode == current else ""
        table.add_row(status, mode)

    console.print(table)


@permission_group.command("current")
def current_permission(
    repo: Optional[str] = typer.Option(
        None, "--repo", "-r", help="my-claude 仓库路径"),
):
    """显示当前使用的权限模式。"""
    repo_path = get_repo(repo)
    settings_yml_path = get_settings_yml_path(repo_path)

    try:
        current = get_current_permission_mode(settings_yml_path)
    except Exception as e:
        console.print(f"[red]读取配置失败: {e}[/red]")
        raise typer.Exit(1)

    console.print(
        Panel(f"当前权限模式: [bold cyan]{current}[/bold cyan]", box=box.ROUNDED))


@permission_group.command("use")
def use_permission(
    mode_name: str = typer.Argument(..., help="要使用的权限模式"),
    sync: bool = typer.Option(False, "--sync", "-s", help="切换后自动同步配置"),
    skip_confirm: bool = typer.Option(False, "--force", "-f", help="同步时跳过确认"),
    repo: Optional[str] = typer.Option(
        None, "--repo", "-r", help="my-claude 仓库路径"),
):
    """切换权限模式。"""
    repo_path = get_repo(repo)
    settings_yml_path = get_settings_yml_path(repo_path)

    try:
        update_permission_mode(settings_yml_path, mode_name)
    except ValueError as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]更新配置失败: {e}[/red]")
        raise typer.Exit(1)

    console.print(f"[green]✅ 已切换到权限模式: [bold]{mode_name}[/bold][/green]")

    if sync:
        console.print("\n[cyan]🔄 开始同步配置...[/cyan]\n")
        success = run_sync(repo_path, skip_confirm=skip_confirm)
        if success:
            console.print("\n[green]✅ 配置同步完成！[/green]")
        else:
            console.print("\n[red]❌ 配置同步失败[/red]")
            raise typer.Exit(1)
    else:
        console.print("\n[yellow]💡 提示: 运行 'my-claude sync' 同步配置[/yellow]")


# ========== 通用命令 ==========


@app.command("sync")
def sync_config(
    skip_confirm: bool = typer.Option(False, "--force", "-f", help="跳过确认"),
    repo: Optional[str] = typer.Option(
        None, "--repo", "-r", help="my-claude 仓库路径"),
):
    """同步配置到 ~/.claude/。"""
    repo_path = get_repo(repo)

    console.print("[cyan]🔄 开始同步配置...[/cyan]\n")
    success = run_sync(repo_path, skip_confirm=skip_confirm)
    if success:
        console.print("\n[green]✅ 配置同步完成！[/green]")
    else:
        console.print("\n[red]❌ 配置同步失败[/red]")
        raise typer.Exit(1)


@app.command("check")
def check_config(
    repo: Optional[str] = typer.Option(
        None, "--repo", "-r", help="my-claude 仓库路径"),
):
    """预览配置变更（不执行）。"""
    repo_path = get_repo(repo)

    console.print("[cyan]🔍 预览配置变更...[/cyan]\n")
    output = run_check_sync(repo_path)
    if output is not None:
        console.print(output)
    else:
        console.print("[red]❌ 预览失败[/red]")
        raise typer.Exit(1)


@app.command("status")
def show_status(
    repo: Optional[str] = typer.Option(
        None, "--repo", "-r", help="my-claude 仓库路径"),
):
    """显示当前所有配置状态。"""
    repo_path = get_repo(repo)
    models_yml_path = get_models_yml_path(repo_path)
    settings_yml_path = get_settings_yml_path(repo_path)

    try:
        provider = get_current_model(models_yml_path)
        style = get_current_output_style(settings_yml_path)
        level = get_current_model_level(settings_yml_path)
        thinking = get_always_thinking_enabled(settings_yml_path)
        permission = get_current_permission_mode(settings_yml_path)
    except Exception as e:
        console.print(f"[red]读取配置失败: {e}[/red]")
        raise typer.Exit(1)

    table = Table(
        title="当前配置状态",
        box=box.ROUNDED,
        show_header=False,
    )
    table.add_column("配置项", style="bold magenta")
    table.add_column("值", style="cyan")

    thinking_status = "✓ 启用" if thinking else "✗ 禁用"
    thinking_color = "green" if thinking else "red"

    table.add_row("模型提供商", provider)
    table.add_row("输出风格", style)
    table.add_row("模型级别", level)
    table.add_row(
        "深度思考", f"[{thinking_color}]{thinking_status}[/{thinking_color}]")
    table.add_row("权限模式", permission)

    console.print(table)


def main():
    app()


if __name__ == "__main__":
    main()
