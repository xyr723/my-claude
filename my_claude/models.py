"""
模型配置与 settings 配置管理模块。
使用 ruamel.yaml 保留文件中的注释。
"""

from pathlib import Path
from typing import Any, Dict, List, Tuple
from ruamel.yaml import YAML


# 初始化 YAML 解析器（保留注释和格式）
yaml = YAML()
yaml.preserve_quotes = True
yaml.indent(mapping=2, sequence=4, offset=2)
yaml.width = 4096  # 防止自动换行


# ========== models.yml 相关 ==========


def load_models_config(models_yml_path: Path) -> Tuple[Dict[str, Any], str]:
    """
    加载 models.yml 配置。

    Args:
        models_yml_path: models.yml 文件路径

    Returns:
        (model_configs, current_use_model) 元组
    """
    with open(models_yml_path, "r", encoding="utf-8") as f:
        data = yaml.load(f)

    model_configs = data.get("model_configs", {})
    current_model = data.get("use_model", "")

    return model_configs, current_model


def list_available_models(models_yml_path: Path) -> List[Dict[str, Any]]:
    """
    列出所有可用的模型配置。

    Args:
        models_yml_path: models.yml 文件路径

    Returns:
        模型配置列表，每个元素包含 name, config, is_current
    """
    with open(models_yml_path, "r", encoding="utf-8") as f:
        data = yaml.load(f)

    model_configs = data.get("model_configs", {})
    current_model = data.get("use_model", "")

    result = []
    for name, config in model_configs.items():
        result.append(
            {
                "name": name,
                "config": config,
                "is_current": name == current_model,
            }
        )

    return result


def get_current_model(models_yml_path: Path) -> str:
    """获取当前使用的模型名称。"""
    with open(models_yml_path, "r", encoding="utf-8") as f:
        data = yaml.load(f)
    return data.get("use_model", "")


def update_use_model(models_yml_path: Path, new_model: str) -> None:
    """
    更新 use_model 配置。

    Args:
        models_yml_path: models.yml 文件路径
        new_model: 新的模型名称

    Raises:
        ValueError: 当 new_model 不在 model_configs 中时抛出
    """
    with open(models_yml_path, "r", encoding="utf-8") as f:
        data = yaml.load(f)

    model_configs = data.get("model_configs", {})
    if new_model not in model_configs:
        available = ", ".join(model_configs.keys())
        raise ValueError(f"模型 '{new_model}' 不存在。可用模型: {available}")

    data["use_model"] = new_model

    with open(models_yml_path, "w", encoding="utf-8") as f:
        yaml.dump(data, f)


# ========== settings.yml 相关 ==========


def load_settings_config(settings_yml_path: Path) -> Dict[str, Any]:
    """加载 settings.yml 配置。"""
    with open(settings_yml_path, "r", encoding="utf-8") as f:
        data = yaml.load(f)
    return data.get("settings", {})


def get_current_output_style(settings_yml_path: Path) -> str:
    """获取当前输出风格。"""
    settings = load_settings_config(settings_yml_path)
    return settings.get("outputStyle", "")


def list_available_output_styles(output_styles_dir: Path) -> List[str]:
    """
    列出所有可用的输出风格。

    Args:
        output_styles_dir: output-styles 目录路径

    Returns:
        输出风格名称列表（不含 .md 后缀）
    """
    if not output_styles_dir.exists():
        return []

    styles = []
    for file in output_styles_dir.glob("*.md"):
        styles.append(file.stem)

    return sorted(styles)


def update_output_style(settings_yml_path: Path, new_style: str) -> None:
    """
    更新输出风格配置。

    Args:
        settings_yml_path: settings.yml 文件路径
        new_style: 新的输出风格名称
    """
    with open(settings_yml_path, "r", encoding="utf-8") as f:
        data = yaml.load(f)

    data["settings"]["outputStyle"] = new_style

    with open(settings_yml_path, "w", encoding="utf-8") as f:
        yaml.dump(data, f)


def get_current_model_level(settings_yml_path: Path) -> str:
    """获取当前模型级别（opus/sonnet/haiku）。"""
    settings = load_settings_config(settings_yml_path)
    return settings.get("model", "")


def list_available_model_levels() -> List[str]:
    """列出可用的模型级别。"""
    return ["opus", "sonnet", "haiku"]


def update_model_level(settings_yml_path: Path, new_level: str) -> None:
    """
    更新模型级别配置。

    Args:
        settings_yml_path: settings.yml 文件路径
        new_level: 新的模型级别（opus/sonnet/haiku）
    """
    valid_levels = {"opus", "sonnet", "haiku"}
    if new_level not in valid_levels:
        raise ValueError(
            f"无效的模型级别: {new_level}。可用值: {', '.join(valid_levels)}")

    with open(settings_yml_path, "r", encoding="utf-8") as f:
        data = yaml.load(f)

    data["settings"]["model"] = new_level

    with open(settings_yml_path, "w", encoding="utf-8") as f:
        yaml.dump(data, f)


def get_always_thinking_enabled(settings_yml_path: Path) -> bool:
    """获取深度思考模式是否启用。"""
    settings = load_settings_config(settings_yml_path)
    return settings.get("alwaysThinkingEnabled", False)


def update_always_thinking_enabled(settings_yml_path: Path, enabled: bool) -> None:
    """更新深度思考模式配置。"""
    with open(settings_yml_path, "r", encoding="utf-8") as f:
        data = yaml.load(f)

    data["settings"]["alwaysThinkingEnabled"] = enabled

    with open(settings_yml_path, "w", encoding="utf-8") as f:
        yaml.dump(data, f)


def get_current_permission_mode(settings_yml_path: Path) -> str:
    """获取当前权限模式。"""
    settings = load_settings_config(settings_yml_path)
    permissions = settings.get("permissions", {})
    return permissions.get("defaultMode", "default")


def list_available_permission_modes() -> List[str]:
    """列出可用的权限模式。"""
    return ["default", "acceptEdits", "plan", "dontAsk", "bypassPermissions", "delegate"]


def update_permission_mode(settings_yml_path: Path, new_mode: str) -> None:
    """更新权限模式配置。"""
    valid_modes = set(list_available_permission_modes())
    if new_mode not in valid_modes:
        raise ValueError(f"无效的权限模式: {new_mode}。可用值: {', '.join(valid_modes)}")

    with open(settings_yml_path, "r", encoding="utf-8") as f:
        data = yaml.load(f)

    data["settings"]["permissions"]["defaultMode"] = new_mode

    with open(settings_yml_path, "w", encoding="utf-8") as f:
        yaml.dump(data, f)
