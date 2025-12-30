from __future__ import annotations

"""
Prompt 加载与渲染服务。

功能：
- 按平台与模式从 prompts/ 目录中安全加载 prompt 文件
- 自动将 global_rules.txt 拼接在每个 prompt 前面
- 支持 {{var}} 形式的占位符渲染
- 防止路径穿越攻击
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Dict
import re

from core.logger import logger


PROMPTS_ROOT = Path(__file__).resolve().parents[1] / "prompts"
GLOBAL_RULES_FILE = PROMPTS_ROOT / "global_rules.txt"


_PLACEHOLDER_PATTERN = re.compile(r"{{\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*}}")


class PromptNotFoundError(Exception):
    """指定的 prompt 未找到"""


def _sanitize_name(name: str) -> str:
    """
    平台 / 模式名称安全过滤：
    - 仅允许字母、数字、下划线、短横线
    - 禁止出现路径分隔符和 ..
    """
    if not name:
        raise ValueError("name 不能为空")
    if "/" in name or "\\" in name or ".." in name:
        raise ValueError("非法名称，包含路径分隔符或 ..")
    if not re.fullmatch(r"[a-zA-Z0-9_-]+", name):
        raise ValueError("非法名称，仅允许字母、数字、下划线和短横线")
    return name


def _safe_read_file(path: Path) -> str:
    """安全读取文本文件，文件不存在时返回空字符串。"""
    try:
        if not path.exists():
            return ""
        return path.read_text(encoding="utf-8")
    except Exception as exc:  # noqa: BLE001
        logger.error(f"读取 prompt 文件失败: {path}: {exc}")
        return ""


def _render_placeholders(template: str, variables: Dict[str, str]) -> str:
    """使用 {{var}} 形式的占位符进行简单渲染。缺失变量保持原样。"""

    def replacer(match: re.Match) -> str:  # type: ignore[type-arg]
        key = match.group(1)
        return str(variables.get(key, match.group(0)))

    return _PLACEHOLDER_PATTERN.sub(replacer, template)


@dataclass
class PromptLoadResult:
    platform: str
    mode: str
    prompt_path: Path
    content: str


class PromptLoader:
    """提示词加载与渲染服务。"""

    def __init__(self, prompts_root: Path | None = None) -> None:
        self.prompts_root = prompts_root or PROMPTS_ROOT

    def load_prompt(
        self,
        platform: str,
        mode: str = "default",
        variables: Dict[str, str] | None = None,
    ) -> PromptLoadResult:
        """
        加载指定平台 + 模式的 prompt，并进行占位符渲染。

        加载逻辑：
        1. 校验 platform / mode，防止路径穿越
        2. 尝试读取 {prompts_root}/{platform}/{mode}.prompt
        3. 如不存在则回退到 {prompts_root}/{platform}/default.prompt
        4. 在最终内容前拼接 global_rules.txt
        """
        safe_platform = _sanitize_name(platform)
        safe_mode = _sanitize_name(mode)

        platform_dir = self.prompts_root / safe_platform
        primary_file = platform_dir / f"{safe_mode}.prompt"
        fallback_file = platform_dir / "default.prompt"

        content = _safe_read_file(primary_file)
        used_file = primary_file

        if not content:
            logger.info(
                "指定模式 prompt 不存在或为空，回退到 default.prompt",
            )
            content = _safe_read_file(fallback_file)
            used_file = fallback_file

        if not content:
            raise PromptNotFoundError(
                f"未找到可用的 prompt 文件: {primary_file} 或 {fallback_file}",
            )

        global_rules = _safe_read_file(GLOBAL_RULES_FILE)
        full_content = f"{global_rules.strip()}\n\n{content.lstrip()}" if global_rules else content

        if variables:
            full_content = _render_placeholders(full_content, variables)

        return PromptLoadResult(
            platform=safe_platform,
            mode=safe_mode,
            prompt_path=used_file,
            content=full_content,
        )


